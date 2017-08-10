import discord
from discord.ext import commands

from db.dbase import DBase
from cogs.utils import constants
from cogs.utils.messages import MessageManager


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")


    @commands.command(pass_context=True)
    async def help(self, ctx, command=None):
        """Display command information"""
        user = ctx.message.author
        channel = ctx.message.channel
        prefix = ctx.prefix
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        if command:
            print(command)
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
        if isinstance(commands, dict):
            help = discord.Embed(title="Available Commands", color=constants.BLUE)
            for key in commands:
                command = self.bot.commands.get(key)
                help.add_field(name="{}{}".format(prefix, command.name), value="{}".format(command.help), inline=False)
            return help
        else:
            command = commands
            params = self.strip_params(command.clean_params)
            help = discord.Embed(title="{}{} {}".format(prefix, command.name, params), color=constants.BLUE)
            help.description = "{}".format(command.help)
            return help


    def strip_params(self, params):
        print(type(params))
        return ""
