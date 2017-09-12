from discord.ext import commands
import discord

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

        # Get guilds in database
        with DBase() as db:
            db = db.get_guilds()
        db_guilds = []
        to_delete = []
        for row in db:
            guild = self.bot.get_guild(row[0])
            if guild:
                db_guilds.append(guild)
            else:
                to_delete.append(row[0])

        # Add guilds
        for guild in self.bot.guilds:
            if guild not in db_guilds:
                with DBase() as db:
                    db.add_guild(guild.id)

        # Remove guilds
        for guild_id in to_delete:
            with DBase() as db:
                db.remove_guild(guild_id)


    async def on_guild_join(self, guild):
        """Add guild and it's members to database"""
        with DBase() as db:
            db.add_guild(guild.id)


    async def on_guild_remove(self, guild):
        """Remove guild from database"""
        with DBase() as db:
            db.remove_guild(guild.id)


    async def on_member_remove(self, user):
        """Remove user from database when they leave the guild"""
        with DBase() as db:
            db.remove_user(str(user))


    async def on_command_error(self, ctx, error):
        """Command error handler"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.MissingRequiredArgument):
            pass

        elif isinstance(error, commands.NotOwner):
            pass

        elif isinstance(error, commands.NoPrivateMessage):
            await manager.say("You can't use that command in a private message", mention=False)

        elif isinstance(error, commands.CheckFailure):
            await manager.say("You don't have the required permissions to do that")

        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.errors.Forbidden):
                pass
            else:
                raise error

        else:
            raise error

        await manager.clear()
