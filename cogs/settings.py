import asyncio

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import MessageManager, get_server_from_dm
from cogs.utils.checks import is_admin


class Settings:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def prefix(self, ctx, new_prefix):
        """Change the server's command prefix"""
        user = ctx.message.author
        channel = ctx.message.channel
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        if ctx.message.channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        if not is_admin(user, channel):
            await manager.say("You must be an admin to do that.")
            return await manager.clear()

        if not new_prefix:
            await manager.say("You must provide a prefix.")
            return await manager.clear()

        if len(new_prefix) > 5:
            await manager.say("Prefix must be less than 6 characters.")
            return await manager.clear()

        with DBase() as db:
            db.set_prefix(ctx.message.server.id, new_prefix)
            await manager.say("Command prefix has been changed to " + new_prefix)
            return await manager.clear()
