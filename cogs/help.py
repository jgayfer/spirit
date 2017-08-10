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
    async def help(self, ctx, command=None):
        """Display command information"""
        user = ctx.message.author
        channel = ctx.message.channel
        prefix = ctx.prefix
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        if command:
            command = self.bot.commands.get(command)
            if command is None:
                await manager.say("There are no commands called '{}'".format(command))
                return await manager.clear()
            help = self.help_embed(ctx.prefix, command)
            await manager.say(help, embed=True, delete=False)
        else:
            help = self.help_embed(ctx.prefix, self.bot.commands)
            await manager.say(help, embed=True, delete=False)
        await manager.clear()


    def help_embed(self, prefix, commands):
        """Create an embed message that displays command help"""
        if isinstance(commands, dict):
            help = discord.Embed(title="Available Commands", color=constants.BLUE)
            help.description = ("Items in <angled_brackets> are *required*"
                              + "\nItems in [square_brackets] are *optional*")
            help.set_footer(text="Use {}help [command] for more info on a command".format(prefix))
            for key in commands:
                command = self.bot.commands.get(key)
                if command.hidden:
                    continue
                signature = self.get_command_signature(prefix, command)
                help.add_field(name="{}".format(signature), value="{}".format(command.help.split('\n')[0].replace('\n', ' ')), inline=False)
            return help
        else:
            command = commands
            signature = self.get_command_signature(prefix, command)
            help = discord.Embed(title="{}".format(signature), color=constants.BLUE)
            help.description = "{}".format(command.help)
            return help


    def get_command_signature(self, prefix, command):
        """Create a user friendly command signature"""
        result = []
        params = command.clean_params
        parent = command.full_parent_name

        # Add command's parent if it exists
        name = prefix + command.name if not parent else prefix + parent + ' ' + command.name
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
