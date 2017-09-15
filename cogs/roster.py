import asyncio

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants
import cogs.help


class Roster:

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.guild_only()
    async def roster(self, ctx):
        """View and manage the server's roster"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'roster')


    @roster.command()
    @commands.guild_only()
    async def setclass(self, ctx, role):
        """
        Add your Destiny 2 class to the roster

        Class must be one of Titan, Warlock, or Hunter
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        role = role.lower().title()
        if role == "Titan" or role == "Warlock" or role == "Hunter":
            with DBase() as db:
                db.add_user(ctx.author.id)
                db.update_role(ctx.author.id, role, ctx.guild.id)
            await manager.say("Your class has been updated!")
        else:
            await manager.say("Class must be one of: Titan, Hunter, Warlock")
        await manager.clear()


    @setclass.error
    async def setclass_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
            await manager.say("Oops! You didn't include your Destiny 2 class.")
            await manager.clear()


    @roster.command()
    @commands.guild_only()
    async def settimezone(self, ctx, *, time_zone):
        """
        Add your timezone to the roster

        For a full list of supported timezones, check out the bot's support server
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        time_zone = time_zone.upper()
        time_zone = "".join(time_zone.split())

        if time_zone in constants.TIME_ZONES:
            with DBase() as db:
                db.add_user(ctx.author.id)
                db.update_timezone(ctx.author.id, time_zone, ctx.guild.id)
            await manager.say("Your time zone has been updated!")
        else:
            await manager.say("Unsupported time zone. For a list of supported timezones, "
                            + "check out the bot's support server.")
        await manager.clear()


    @settimezone.error
    async def settimezone_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
            await manager.say("Oops! You didn't include your timezone.")
            await manager.clear()


    @roster.command()
    @commands.guild_only()
    async def show(self, ctx):
        """
        Display the roster

        The roster includes the name, Destiny 2 class,
        and timezone of server members. Note that only
        users who have set a role or timezone will be
        displayed on the roster.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        with DBase() as db:
            roster = db.get_roster(ctx.guild.id)

        if len(roster) != 0:

            text = "```\n"
            for row in roster:
                member = ctx.guild.get_member(row[0])
                if member:
                    name = member.display_name
                    formatted_name = (name[:18] + '..') if len(name) > 18 else name
                    role = row[1] if row[1] else "---"
                    time_zone = row[2] if row[2] else "---"
                    text += '{:20} {:6} {:7}\n'.format(formatted_name, time_zone, role)
            text += "```"

            embed_msg = discord.Embed(color=constants.BLUE)
            embed_msg.title="{} Roster".format(ctx.guild.name)
            embed_msg.description = text
            await manager.say(embed_msg, embed=True, delete=False)
        else:
            await manager.say("No roster exists yet. Use `{}settings settimezone` or `{}settings "
                            + "setclass` to add the first entry!".format(ctx.prefix, ctx.prefix))
        await manager.clear()
