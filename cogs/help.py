import discord
from discord.ext import commands

from utils import constants
from utils.messages import MessageManager


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command(pass_context=True)
    async def help(self, ctx):
        """Display command information"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        help = discord.Embed(color=constants.BLUE)
        help.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        help.add_field(name="Events",
                       value="**!event create** - create a new event\n"
                           + "**!event delete <id>** - delete event with the given ID")
        help.add_field(name="Roster",
                       value="**!role <class>** - lets others know class you intend on playing in D2\n"
                           + "**!roster** - display a list of what classes everyone intends on playing in D2")

        await manager.say(help, embed=True, delete=False)
        await manager.clear()
