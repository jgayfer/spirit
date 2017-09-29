import discord
from discord.ext import commands

from cogs.utils import constants
from cogs.utils.messages import MessageManager


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")


    @commands.command(hidden=True)
    @commands.cooldown(rate=3, per=5.0, type=commands.BucketType.user)
    async def help(self, ctx, str_cmd=None, str_subcmd=None):
        """Display command information"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        # Determine which prefix to display in the help message
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            prefix = '!'
        else:
            # Don't want to display @botname as the prefix in the help message
            # It's way too long!
            if ctx.prefix != '<@{}> '.format(self.bot.user.id):
                prefix = ctx.prefix
            else:
                custom_prefix = self.bot.db.get_prefix(ctx.guild.id)
                if len(custom_prefix):
                    prefix = custom_prefix.get('prefix')
                else:
                    raise AttributeError("Could not retrieve command prefix")

        # User passed a command and a subcommand
        if str_cmd and str_subcmd:
            cmd = self.bot.get_command(str_cmd)
            if cmd is None:
                await manager.say("There are no commands called '{}'".format(str_cmd))
                return await manager.clear()

            # Check for subcommand
            if hasattr(cmd, 'commands'):
                for sub_cmd in cmd.commands:
                    if sub_cmd.name == str_subcmd:
                        help = self.help_embed_single(prefix, sub_cmd)
                        await manager.say(help, embed=True, delete=False)
                        break
                else:
                    await manager.say("'{}' doesn't have a subcommand called '{}'".format(str_cmd, str_subcmd))
            else:
                await manager.say("'{}' does not have any subcommands".format(str_cmd))

        # User passed in a single command
        elif str_cmd:
            cmd = self.bot.get_command(str_cmd)
            if cmd is None:
                await manager.say("There are no commands called '{}'".format(str_cmd))
                return await manager.clear()

            # Check if command has subcommands
            if hasattr(cmd, 'commands'):
                sub_cmds = []
                for sub_cmd in cmd.commands:
                    sub_cmds.append(sub_cmd)
                help = self.help_embed_group(prefix, cmd, sub_cmds)
            else:
                help = self.help_embed_single(prefix, cmd)
            await manager.say(help, embed=True, delete=False)

        # No command passed, print help for all commands
        else:
            help = self.help_embed_all(prefix, self.bot.commands)
            await manager.say(help, embed=True, delete=False)

        await manager.clear()


    def help_embed_all(self, prefix, commands):
        """Create an embed message that displays command help"""
        help = discord.Embed(title="Available Commands", color=constants.BLUE)
        help.description = ("**Note:** don't include the angled brackets\n"
                          + "For additional help, join the support server: https://discord.gg/GXCFpkr")
        help.set_footer(text="Use {}help [command] for more info on a command".format(prefix))

        for command in commands:
            if command.hidden:
                continue
            signature = self.get_command_signature(prefix, command)
            help.add_field(name="{}".format(signature), value="{}".format(command.help.split('\n')[0]), inline=False)
        return help


    def help_embed_single(self, prefix, command):
        """Create a help embed message for a single command"""
        signature = self.get_command_signature(prefix, command)
        help = discord.Embed(title="{}".format(signature), color=constants.BLUE)
        help.description = "{}".format(self.format_long_help(command.help))
        return help


    def help_embed_group(self, prefix, cmd, sub_cmds):
        """Create a help embed message for a command and its subcommands"""
        help = discord.Embed(title="{}".format(cmd.name.title()), color=constants.BLUE)
        help.description = "*{}*".format(cmd.help.split('\n')[0])
        help.set_footer(text="Use {}help [command] for more info on a command".format(prefix))
        for sub_cmd in sub_cmds:
            signature = self.get_command_signature(prefix, sub_cmd)
            help.add_field(name="{}".format(signature), value="{}".format(sub_cmd.help.split('\n')[0]), inline=False)
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
        This ensures that text will properly wrap as help messages
        are docstrings, which have newline characters after every line

        Also add italics to the first line in the help message
        """
        placeholder = '*)4_8^'
        help_msg = help_msg.replace('\n\n', placeholder)
        help_msg = help_msg.replace('\n', ' ')
        help_msg = help_msg.replace(placeholder, '\n\n')

        first_line = help_msg.split('\n\n')[0]
        new_first_line = '*' + first_line + '*\n\n'
        if len(help_msg.split('\n\n')) > 1:
            help_msg = new_first_line + '\n\n'.join(help_msg.split('\n\n')[1:])
        else:
            help_msg = new_first_line
        return help_msg
