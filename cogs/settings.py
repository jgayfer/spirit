import asyncio

from discord.ext import commands
import discord

from db.dbase import DBase
from cogs.utils.messages import MessageManager
from cogs.utils.checks import is_admin


class Settings:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def setprefix(self, ctx, new_prefix):
        """
        Change the server's command prefix (admin only)

        Ex. '!setprefix $'
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return await manager.say("That command is not supported in a direct message.")

        if not is_admin(ctx.author, ctx.channel):
            await manager.say("You must be an admin to do that.")
            return await manager.clear()

        if len(new_prefix) > 5:
            await manager.say("Prefix must be less than 6 characters.")
            return await manager.clear()

        with DBase() as db:
            db.set_prefix(ctx.guild.id, new_prefix)
            await manager.say("Command prefix has been changed to " + new_prefix)
            return await manager.clear()


    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
            await manager.say("Oops! You didn't provide a new prefix.")
            await manager.clear()
