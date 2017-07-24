import asyncio

from discord.ext import commands
from db.dbase import DBase
import discord


class Roster:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def role(self, ctx, role="None"):
        """Update the user's role on current server"""
        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        user = str(ctx.message.author)
        role = role.lower().title()
        server_id = ctx.message.server.id
        msg_res = None
        if role == "Titan" or role == "Warlock" or role == "Hunter":
            with DBase() as db:
                db.update_roster(user, role, server_id)
            msg_res = await self.bot.say(ctx.message.author.mention + ": Your role has been updated!")
        else:
            msg_res = await self.bot.say(ctx.message.author.mention
                                         + ": Oops! Role must be one of: Titan, Hunter, Warlock")
        await asyncio.sleep(4)
        await self.bot.delete_message(msg_res)
        await self.bot.delete_message(ctx.message)


    @commands.command(pass_context=True)
    async def roster(self, ctx):
        """List the server's current roster"""
        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        with DBase() as db:
            roster = db.get_roster(ctx.message.server.id)
            if len(roster) != 0:

                message = "```\n"
                for row in roster:
                    message += row[0].split("#")[0]
                    spaces = 17 - len(row[0].split("#")[0])
                    for _ in range (0, spaces):
                        message += " "
                    message += row[1] + "\n"
                message += "```"

                embed_msg = discord.Embed(color=discord.Colour(3381759))
                embed_msg.title="Destiny 2 Pre Launch Roster"
                embed_msg.description = message

                await self.bot.say(embed=embed_msg)
                await asyncio.sleep(4)
                await self.bot.delete_message(ctx.message)
            else:
                msg_res = await self.bot.say(ctx.message.author.mention
                                             + ": No roles have been assigned yet. "
                                             + "Use !role to assign yourself a role.")
                await asyncio.sleep(4)
                await self.bot.delete_message(msg_res)
                await self.bot.delete_message(ctx.message)
