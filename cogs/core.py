from discord.ext import commands

from db.dbase import DBase
from cogs.utils import constants
from cogs.utils.messages import MessageManager


class Core:
    """Core functionality required for the bot to function"""

    def __init__(self, bot):
        self.bot = bot


    async def on_ready(self):
        """Display startup information"""
        print('Spirit v{}'.format(constants.VERSION))
        print('Username: {}'.format(self.bot.user.name))
        print('------')


    async def on_server_join(self, server):
        """Add server and it's members to database"""
        with DBase() as db:
            db.add_server(server.id)


    async def on_server_remove(self, server):
        """Remove server from database"""
        with DBase() as db:
            db.remove_server(server.id)


    async def on_member_remove(self, user):
        """Remove user from database when they leave the server"""
        with DBase() as db:
            db.remove_user(str(user))


    async def on_command_error(self, error, ctx):
        """Let user know if a command is invalid"""
        if isinstance(error, commands.CommandNotFound):
            user = ctx.message.author
            channel = ctx.message.channel
            server = ctx.message.server
            manager = MessageManager(self.bot, user, channel, [ctx.message])
            await manager.say("Command '{}' not found.".format(ctx.message.content.replace(ctx.prefix, '')))
            await manager.clear()
        else:
            print(error)
