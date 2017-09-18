from datetime import datetime
import asyncio
import re

from discord.ext import commands
import discord

from db.dbase import DBase
from db.query_wrappers import get_event_role, get_event_delete_role
from cogs.utils.messages import delete_all, MessageManager
from cogs.utils.checks import is_event, is_int
from cogs.utils import constants
from cogs.utils.format import format_role_name


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.guild_only()
    async def event(self, ctx):
        """
        Create an event in the events channel

        After invoking the event command, the bot will ask
        you to enter the event details. Once the event
        is created, it will appear in the upcoming-events
        channel. The upcoming-events channel is designed with
        the assumption that it isn't used for anything but
        displaying events; non event messages will be deleted.

        Users will be able to accept and decline the
        event by adding reactions. If a maximum number
        of attendees is set and the event is full,
        additional attendees will be placed in a standby
        section. If a spot opens up, the user at the
        top of the standby section will be automatically
        moved into the event.

        By default, everyone can make events. However, a minimum role
        requirement to create events can be defined in the settings.
        See `help settings seteventrole` for more information.

        The event creator and those with the Manage Sever permission
        can delete events by reacting to the event message with \U0001f480.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        event_role = get_event_role(ctx.guild)
        member_permissions = ctx.author.permissions_in(ctx.channel)

        if event_role:
            if ctx.author.top_role < event_role:
                event_role_str = format_role_name(event_role)
                await manager.say("You must be of role **{}** or higher to do that.".format(event_role))
                return await manager.clear()

        await manager.say('Event creation instructions have been messaged to you')

        res = await manager.say_and_wait("Enter event title:", dm=True)
        if not res:
            return await manager.clear()
        title = res.content

        description = ""
        res = await manager.say_and_wait("Enter event description (type 'none' for no description):", dm=True)
        if not res:
            return await manager.clear()
        if res.content.upper() != 'NONE':
            description = res.content

        max_members = 0
        while not max_members:
            res = await manager.say_and_wait("Enter the maximum numbers of attendees (type 'none' for no maximum):", dm=True)
            if not res:
                return await manager.clear()
            if res.content.upper() == 'NONE':
                break
            elif is_int(res.content) and int(res.content) > 0:
                max_members = int(res.content)
            else:
                await manager.say("That is not a a valid entry.", dm=True)

        start_time = None
        while not start_time:
            res = await manager.say_and_wait("Enter event time (YYYY-MM-DD HH:MM AM/PM):", dm=True)
            if not res:
                return await manager.clear()
            start_time_format = '%Y-%m-%d %I:%M %p'
            try:
                start_time = datetime.strptime(res.content, start_time_format)
            except ValueError:
                await manager.say("Invalid event time!", dm=True)

        time_zone = None
        while not time_zone:
            res = await manager.say_and_wait("Enter the time zone (PST, EST, etc):", dm=True)
            if not res:
                return await manager.clear()
            user_timezone = "".join(res.content.upper().split())
            if user_timezone not in constants.TIME_ZONES:
                await manager.say("Unsupported time zone", dm=True)
            else:
                time_zone = user_timezone

        with DBase() as db:
            affected_rows = db.create_event(title, start_time, time_zone, ctx.guild.id, description, max_members, ctx.author.id)
        if affected_rows == 0:
            await manager.say("An event with that name already exists!", dm=True)
            return await manager.clear()

        event_channel = await self.get_events_channel(ctx.guild)
        await manager.say("Event created! The " + event_channel.mention + " channel will be updated momentarily.", dm=True)
        await self.list_events(ctx.guild)
        await manager.clear()


    async def list_events(self, guild):
        """Clear the event channel and display all upcoming events"""
        events_channel = await self.get_events_channel(guild)
        await events_channel.purge(limit=999, check=delete_all)
        with DBase() as db:
            events = db.get_events(guild.id)
        if len(events) > 0:
            for row in events:
                event_embed = self.create_event_embed(guild, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                msg = await events_channel.send(embed=event_embed)
                await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                await msg.add_reaction("\N{CROSS MARK}")
        else:
            await events_channel.send("There are no upcoming events.")


    async def on_raw_reaction_add(self, emoji, message_id, channel_id, user_id):
        """If a reaction represents a user RSVP, update the DB and event message"""
        channel = self.bot.get_channel(channel_id)
        if isinstance(channel, discord.abc.PrivateChannel):
            return

        try:
            message = await channel.get_message(message_id)
        except discord.errors.Forbidden as e:
            # Don't have permission to read this message
            return

        guild = channel.guild
        member = guild.get_member(user_id)
        manager = MessageManager(self.bot, member, channel)
        deleted = None

        # We check that the user is not the message author as to not count
        # the initial reactions added by the bot as being indicative of attendance
        if is_event(message) and member != message.author:
            title = message.embeds[0].title
            if emoji.name == "\N{WHITE HEAVY CHECK MARK}":
                await self.set_attendance(member, guild, 1, title, message)
            elif emoji.name == "\N{CROSS MARK}":
                await self.set_attendance(member, guild, 0, title, message)
            elif emoji.name == "\N{SKULL}":
                deleted =  await self.delete_event(guild, title, member, channel)

            if not deleted:
                await message.remove_reaction(emoji, member)
            await manager.clear()


    async def set_attendance(self, member, guild, attending, title, message):
        """Send updated event attendance info to db and update the event"""
        with DBase() as db:
            db.add_user(member.id)
            db.update_attendance(member.id, guild.id, attending, title, datetime.now())

        with DBase() as db:
            rows = db.get_event(guild.id, title)
        if len(rows) and len(rows[0]):
            event = rows[0]
        else:
            raise ValueError("Could not retrieve event")
            return

        # Update event message in place for a more seamless user experience
        event_embed = self.create_event_embed(guild, event[0], event[1], event[2], event[3], event[4], event[5], event[6], event[7])
        await message.edit(embed=event_embed)


    async def delete_event(self, guild, title, member, channel):
        """Delete an event and update the events channel on success"""
        event_delete_role = get_event_delete_role(guild)
        with DBase() as db:
            rows = db.get_event_creator(guild.id, title)

        if len(rows) and len(rows[0]):
            creator_id = rows[0][0]

        if member.permissions_in(channel).manage_guild or (member.id == creator_id) or (event_delete_role and member.top_role >= event_delete_role):
            with DBase() as db:
                deleted = db.delete_event(guild.id, title)
            if deleted:
                await self.list_events(guild)
                return True
        else:
            await member.send("You don't have permission to delete that event.")


    async def get_events_channel(self, guild):
        """Return the events channel if it exists, otherwise create one and return it"""
        for channel in guild.channels:
            if channel.name == "upcoming-events":
                return channel

        # Need to make sure the bot can still send messages in the events channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False, add_reactions=True),
            guild.me: discord.PermissionOverwrite(send_messages=True, add_reactions=True)
        }
        return await guild.create_text_channel("upcoming-events", overwrites=overwrites)


    def create_event_embed(self, guild, title, description, time, time_zone, creator_id, accepted=None, declined=None, max_members=None):
        """Create and return a Discord Embed object that represents an upcoming event"""
        embed_msg = discord.Embed(color=constants.BLUE)
        embed_msg.title = title

        creator = guild.get_member(creator_id)
        if creator:
            embed_msg.set_footer(text="Created by {} | React with {} to remove this event".format(creator.display_name, '\U0001f480'))
        else:
            embed_msg.set_footer(text="React with {} to remove this event".format('\U0001f480'))

        if description:
            embed_msg.description = description
        time_str = time.strftime("%A %b %-d, %Y @ %-I:%M %p")
        embed_msg.add_field(name="Time", value=time_str + " " + time_zone, inline=False)

        if accepted:
            accepted_list = None
            if max_members:
                accepted_list = accepted.split(',')[:max_members]
            else:
                accepted_list = accepted.split(',')
            text = ""
            for user_id in accepted_list:
                member = guild.get_member(int(user_id))
                text += "{}\n".format(member.display_name)
            if max_members:
                embed_msg.add_field(name="Accepted ({}/{})".format(len(accepted_list), max_members), value=text)
            else:
                embed_msg.add_field(name="Accepted", value=text)
        else:
            if max_members:
                embed_msg.add_field(name="Accepted (0/{})".format(max_members), value="-")
            else:
                embed_msg.add_field(name="Accepted", value="-")

        if declined:
            declined_list = declined.split(',')
            text = ""
            for user_id in declined_list:
                member = guild.get_member(int(user_id))
                text += "{}\n".format(member.display_name)
            embed_msg.add_field(name="Declined", value=text)
        else:
            embed_msg.add_field(name="Declined", value="-")

        if accepted and max_members:
            standby_list = accepted.split(',')[max_members:]
            if standby_list:
                text = ""
                for user_id in standby_list:
                    member = guild.get_member(int(user_id))
                    text += "{}\n".format(member.display_name)
                embed_msg.add_field(name="Standby", value=text, inline=False)

        return embed_msg
