import discord
from discord.ext import commands

from db.dbase import DBase
from cogs.utils import constants
from cogs.utils.messages import MessageManager


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")


    @commands.command(pass_context=True, hidden=True)
    async def help(self, ctx, str_cmd=None, str_subcmd=None):
        """Display command information"""
        user = ctx.message.author
        channel = ctx.message.channel
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        # Determine which prefix to display in the help message
        prefix = ""
        if channel.is_private:
            prefix = '!'
        else:
            if ctx.prefix != '<@{}> '.format(self.bot.user.id):
                prefix = ctx.prefix
            else:
                with DBase() as db:
                    prefix = db.get_prefix(ctx.message.server.id)


        # User passed a command and a subcommand
        if str_cmd and str_subcmd:

            cmd = self.bot.commands.get(str_cmd)
            if cmd is None:
                await manager.say("There are no commands called '{}'".format(str_cmd))
                return await manager.clear()

            # Check for subcommand
            if hasattr(cmd, 'commands'):
                if str_subcmd in cmd.commands.keys():
                    subcmd = cmd.commands[str_subcmd]
                    help = self.help_embed_single(prefix, subcmd)
                    await manager.say(help, embed=True, delete=False)
                else:
                    await manager.say("'{}' doesn't have a subcommand called '{}'".format(str_cmd, str_subcmd))
                    return await manager.clear()
            else:
                await manager.say("'{}' does not have any subcommands".format(str_cmd))
                return await manager.clear()

        # User passed in a single command
        elif str_cmd:

            cmd = self.bot.commands.get(str_cmd)
            if cmd is None:
                await manager.say("There are no commands called '{}'".format(str_cmd))
                return await manager.clear()

            help = self.help_embed_single(prefix, cmd)
            await manager.say(help, embed=True, delete=False)

        # No commands passed, print help for all commands
        else:
            help = self.help_embed(prefix, self.bot.commands)
            await manager.say(help, embed=True, delete=False)
        await manager.clear()


    def help_embed(self, prefix, commands):
        """Create an embed message that displays command help"""
        if isinstance(commands, dict):

            # Create embed for all commands
            help = discord.Embed(title="Available Commands", color=constants.BLUE)
            help.description = ("Items in <angled_brackets> are *required*"
                              + "\nItems in [square_brackets] are *optional*"
                              + "\nNote - don't include the [] and <> characters")
            help.set_footer(text="Use {}help [command] for more info on a command".format(prefix))

            for key in commands:
                command = self.bot.commands.get(key)
                if command.hidden:
                    continue
                signature = self.get_command_signature(prefix, command)
                help.add_field(name="{}".format(signature), value="{}".format(command.help.split('\n')[0]), inline=False)
            return help
        else:

            # Create embed for a single command
            command = commands
            signature = self.get_command_signature(prefix, command)
            help = discord.Embed(title="{}".format(signature), color=constants.BLUE)
            help.description = "{}".format(self.format_long_help(command.help))
            return help

    def help_embed_single(self, prefix, command):
        signature = self.get_command_signature(prefix, command)
        help = discord.Embed(title="{}".format(signature), color=constants.BLUE)
        help.description = "{}".format(self.format_long_help(command.help))
        return help


    def get_command_signature(self, prefix, cmd):
        """Create a user friendly command signature"""
        result = []
        params = cmd.clean_params
        parent = cmd.full_parent_name
        name = prefix + cmd.name if not parent else prefix + parent + ' ' + cmd.name
        result.append(name)

        # Format arguments to display which are required and which are optional
        if len(params) > 0:
            for name, param in params.items():
                if param.default is not param.empty:
                    result.append('[{}]'.format(name))
                elif param.kind == param.VAR_POSITIONAL:
                    result.append('[{}...]'.format(name))
                else:
                    result.append('<{}>'.format(name))
        return(' '.join(result))


    def format_long_help(self, help_msg):
        """
        Remove single new lines, but keep double new lines.
        This ensures that text will fit to the size of the discord chat window
        as help messages are docstrings, which have newline characters after every line
        """
        placeholder = '*)4_8^'
        help_msg = help_msg.replace('\n\n', placeholder)
        help_msg = help_msg.replace('\n', ' ')
        return help_msg.replace(placeholder, '\n\n')
