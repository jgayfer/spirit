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
    async def role(self, ctx, role):
        """
        Add your Destiny 2 role to the roster

        Ex. '!role Warlock'
        """
        user = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        # Return if the user is in a private message as the roster is server specific
        if channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        if not role:
            await manager.say("You must specify a role.")
            return await manager.clear()

        role = role.lower().title()
        if role == "Titan" or role == "Warlock" or role == "Hunter":
            with DBase() as db:
                db.add_user(server.id, str(user))
                db.update_role(str(user), role, server.id)
            await manager.say("Your role has been updated!")
        else:
            await manager.say("Role must be one of: Titan, Hunter, Warlock")
        await manager.clear()


    @commands.command(pass_context=True)
    async def timezone(self, ctx, time_zone):
        """
        Add your timezone to the roster

        Ex. '!timezone PST'
        """
        user = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        # Return if the user is in a private message as the roster is server specific
        if channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        if not time_zone:
            await manager.say("You must specify a timezone.")
            return manager.clear()

        time_zone = time_zone.upper()
        if time_zone in constants.TIME_ZONES:
            with DBase() as db:
                db.add_user(server.id, str(user))
                db.update_time_zone(str(user), time_zone, server.id)
            await manager.say("Your time zone has been updated!")
        else:
            await manager.say("Unsupported time zone")
        await manager.clear()


    @commands.command(pass_context=True)
    async def roster(self, ctx):
        """
        Display the roster

        The roster includes the name, Destiny 2 class,
        and timezone of server members. Note that only
        users who have set a role or timezone will be
        displayed on the roster.
        """
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
                    name = row[0].split("#")[0]
                    name = (name[:18] + '..') if len(name) > 18 else name
                    role = row[1] if row[1] else "---"
                    time_zone = row[2] if row[2] else "---"
                    text += '{:20} {:5} {:7}\n'.format(name, time_zone, role)
                text += "```"

                embed_msg = discord.Embed(color=constants.BLUE)
                embed_msg.title="{} Roster".format(server.name)
                embed_msg.description = text
                await manager.say(embed_msg, embed=True, delete=False)
            else:
                await manager.say("No roster exists yet. Use 'role' or 'timezone' to add the first entry!")
            await manager.clear()
