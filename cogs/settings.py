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
    async def setprefix(self, ctx, new_prefix=None):

        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        server = None
        if ctx.message.channel.is_private:
            server = get_server_from_dm(self.bot, ctx)
            if not server:
                return await manager.say("You must be part of only one {} server to do that in a DM".format(self.bot.user.mention))
        else:
            server = ctx.message.server

        if not is_admin(user, server):
            await manager.say("You must be an admin to do that.")
            return await manager.clear()

        if not new_prefix:
            await manager.say("You must provide a new prefix.")

        if len(new_prefix) > 5:
            await manager.say("Oops! Prefix must be less than 6 characters.")
            return await manager.clear()

        with DBase() as db:
            db.set_prefix(server.id, new_prefix)
            await manager.say("Command prefix has been changed to " + new_prefix)
            return await manager.clear()
