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

        help = discord.Embed(title="Available Commands", color=constants.BLUE)
        help.add_field(name="Events",
                       value="{}event create - create a new event\n".format(prefix)
                           + "{}event delete <id> - delete event with the given ID".format(prefix))
        help.add_field(name="Roster",
                       value="{}role <class> - choose which role you intend on playing in D2\n".format(prefix)
                           + "{}roster - display the selected D2 role of all members".format(prefix))
        help.add_field(name="Settings",
                       value="{0}change_prefix - change the command prefix".format(prefix))

        await manager.say(help, embed=True, delete=False)
        await manager.clear()
