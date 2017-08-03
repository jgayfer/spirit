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
        channel = ctx.message.channel
        prefix = ctx.prefix
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        help = discord.Embed(title="Available Commands", color=constants.BLUE)
        help.add_field(name="Events",
                       value="{}event - create a new event\n".format(prefix))
        help.add_field(name="Roster",
                       value="{}role <class> - choose which role you intend on playing in D2\n".format(prefix)
                           + "{}roster - display the selected D2 role of all members".format(prefix))
        help.add_field(name="Other",
                       value="{}setprefix - change the server's command prefix".format(prefix)
                           + "{}feedback - send feedback to the bot's developer".format(prefix))

        await manager.say(help, embed=True, delete=False)
        await manager.clear()
