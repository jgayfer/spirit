import asyncio

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import MessageManager


class Settings:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def prefix(self, ctx, new_prefix):

        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        if not user.server_permissions.administrator:
            await manager.say("Oops! You must be an admin to do that.")
            return await manager.clear()

        # Return if the user is in a private message as prefixes are server specific
        if ctx.message.channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        if len(new_prefix) > 5:
            await manager.say("Oops! Prefix must be less than 6 characters")
            return await manager.clear()

        with DBase() as db:
            db.set_prefix(ctx.message.server.id, new_prefix)
            await manager.say("Command prefix has been changed to " + new_prefix)
            return await manager.clear()
