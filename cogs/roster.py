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
        channel = ctx.message.channel
        server = ctx.message.server
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        # Return if the user is in a private message as the roster is server specific
        if channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        role = role.lower().title()
        if role == "Titan" or role == "Warlock" or role == "Hunter":
            with DBase() as db:
                db.add_user(server.id, str(user))
                db.update_roster(str(user), role, server.id)
            await manager.say("Your role has been updated!")
        else:
            await manager.say("Role must be one of: Titan, Hunter, Warlock")
        await manager.clear()


    @commands.command(pass_context=True)
    async def roster(self, ctx):
        """List the server's current roster"""
        user = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        # Return if the user is in a private message as roles are server specific
        if channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        with DBase() as db:
            roster = db.get_roster(server.id)
            if len(roster) != 0:

                text = "```\n"
                for row in roster:
                    text += row[0].split("#")[0]
                    spaces = 25 - len(row[0].split("#")[0])
                    for _ in range (0, spaces):
                        text += " "
                    text += row[1] + "\n"
                text += "```"

                embed_msg = discord.Embed(color=constants.BLUE)
                embed_msg.title="Destiny 2 Pre Launch Roster"
                embed_msg.description = text
                await manager.say(embed_msg, embed=True, delete=False)
            else:
                await manager.say("No roles have been assigned yet. Use the 'role' command to assign yourself a role.")
            await manager.clear()
