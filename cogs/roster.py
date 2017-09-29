import asyncio

from discord.ext import commands
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants
import cogs.help


class Roster:

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
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
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        role = role.lower().title()
        if role == "Titan" or role == "Warlock" or role == "Hunter":
            self.bot.db.add_user(ctx.author.id)
            self.bot.db.update_role(ctx.author.id, role, ctx.guild.id)
            await manager.say("Your class has been updated!")
        else:
            await manager.say("Class must be one of: Titan, Hunter, Warlock")
        await manager.clear()


    @setclass.error
    async def setclass_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
            await manager.say("Oops! You didn't include your Destiny 2 class.")
            await manager.clear()


    @roster.command()
    @commands.guild_only()
    async def settimezone(self, ctx, *, time_zone):
        """
        Add your timezone to the roster

        For a full list of supported timezones, check out the bot's support server
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        time_zone = time_zone.upper()
        time_zone = "".join(time_zone.split())

        if time_zone in constants.TIME_ZONES:
            self.bot.db.add_user(ctx.author.id)
            self.bot.db.update_timezone(ctx.author.id, time_zone, ctx.guild.id)
            await manager.say("Your time zone has been updated!")
        else:
            await manager.say("Unsupported time zone. For a list of supported timezones, "
                            + "check out the bot's support server.")
        await manager.clear()


    @settimezone.error
    async def settimezone_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
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
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        roster_groups = []
        roster = self.bot.db.get_roster(ctx.guild.id)

        if len(roster) != 0:

            text = "```\n"
            for row in roster:

                # Add a single entry to the roster message
                member = ctx.guild.get_member(row.get('user_id'))
                role = row.get('role')
                timezone = row.get('timezone')
                if member:
                    name = member.display_name
                    formatted_name = (name[:16] + '..') if len(name) > 16 else name
                    role = role if role else "---"
                    timezone = timezone if timezone else "---"
                    text += '{:18} {:6} {:7}\n'.format(formatted_name, timezone, role)

                # If the message is too big, place it into a group
                if len(text) > 2000:
                    text += "```"
                    roster_groups.append(text)
                    text = "```\n"

            # Add any remaining entries into a roster group
            if len(text) > 5:
                text += "```"
                roster_groups.append(text)

            # Send the initial roster message
            embed_msg = discord.Embed(color=constants.BLUE)
            embed_msg.title="{} Roster".format(ctx.guild.name)
            embed_msg.description = roster_groups[0]
            await manager.say(embed_msg, embed=True, delete=False)

            # Send additional roster messages if the roster is too long
            for group in roster_groups[1:]:
                embed_msg = discord.Embed(color=constants.BLUE)
                embed_msg.title="{} Roster (continued)".format(ctx.guild.name)
                embed_msg.description = group
                await manager.say(embed_msg, embed=True, delete=False)

        else:
            await manager.say("No roster exists yet. Use '{}roster settimezone' or '{}roster ".format(ctx.prefix, ctx.prefix)
                            + "setclass' to add the first entry!")
        await manager.clear()
