from discord.ext import commands
import discord

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
        db_guilds = []
        to_delete = []
        results = self.bot.db.get_guilds()
        for row in results:
            guild_id = row.get('guild_id')
            guild = self.bot.get_guild(guild_id)
            if not guild:
                to_delete.append(guild_id)

        # Remove guilds
        for guild_id in to_delete:
            self.bot.db.remove_guild(guild_id)


    async def on_member_remove(self, user):
        """Remove user from database when they leave the guild"""
        member_ids = []
        for member in self.bot.get_all_members():
            member_ids.append(member.id)

        if user.id not in member_ids:
            self.bot.db.remove_user(user.id)


    async def on_command_error(self, ctx, error):
        """Command error handler"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

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
