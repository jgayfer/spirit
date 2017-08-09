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
        help.add_field(name="Events", inline=False,
                       value="{}event - create a new event\n".format(prefix))
        help.add_field(name="Roster", inline=False,
                       value="{}role <class> - update the roster with your D2 role\n".format(prefix)
                           + "{}timezone <timezone> - update the roster with your timezone\n".format(prefix)
                           + "{}roster - display the current roster".format(prefix))
        help.add_field(name="Other", inline=False,
                       value="{}prefix - change the server's command prefix\n".format(prefix)
                           + "{}feedback - send feedback to the bot's developer".format(prefix))

        await manager.say(help, embed=True, delete=False)
        await manager.clear()
