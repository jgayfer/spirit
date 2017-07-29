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
    async def help(self, ctx):
        """Display command information"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        prefix = ""
        with DBase() as db:
            prefix = db.get_prefix(ctx.message.server.id)

        text = ("**{0}event create** - create a new event\n"
              + "**{0}event delete <id>** - delete event with the given ID\n"
              + "**{0}role <class>** - choose which role you intend on playing in D2\n"
              + "**{0}roster** - display the selected role of all members\n"
              + "**{0}prefix** - change the command prefix").format(prefix)
        help = discord.Embed(title="Available Commands", color=constants.BLUE)
        help.description = text

        await manager.say(help, embed=True, delete=False)
        await manager.clear()
