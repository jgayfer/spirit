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
        """Let user know if a command is invalid"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if isinstance(error, commands.CommandNotFound):
            command_name = ctx.message.content.split(' ')[0].replace(ctx.prefix, '')
            await manager.say("Command '{}' not found.".format(command_name))

        elif isinstance(error, commands.MissingRequiredArgument):
            pass

        elif isinstance(error, commands.NoPrivateMessage):
            await manager.say("You can't' use that command in a private message", mention=False)

        else:
            raise error

        await manager.clear()
