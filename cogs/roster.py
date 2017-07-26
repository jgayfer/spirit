import asyncio

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Roster:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def role(self, ctx, role="None"):
        """Update the user's role on current server"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        user = str(ctx.message.author)
        role = role.lower().title()
        server_id = ctx.message.server.id

        if role == "Titan" or role == "Warlock" or role == "Hunter":
            with DBase() as db:
                db.update_roster(user, role, server_id)
            await manager.say("Your role has been updated!")
        else:
            await manager.say("Role must be one of: Titan, Hunter, Warlock")
        await manager.clear()

    @commands.command(pass_context=True)
    async def roster(self, ctx):
        """List the server's current roster"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await manager.say(user.mention + ": That command is not supported in a direct message.")

        with DBase() as db:
            roster = db.get_roster(ctx.message.server.id)
            if len(roster) != 0:

                message = "```\n"
                for row in roster:
                    message += row[0].split("#")[0]
                    spaces = 25 - len(row[0].split("#")[0])
                    for _ in range (0, spaces):
                        message += " "
                    message += row[1] + "\n"
                message += "```"

                embed_msg = discord.Embed(color=constants.BLUE)
                embed_msg.title="Destiny 2 Pre Launch Roster"
                embed_msg.description = message
                await manager.say(embed_msg, embed=True, delete=False)
            else:
                await manager.say("No roles have been assigned yet. Use !role to assign yourself a role.")
            await manager.clear()
