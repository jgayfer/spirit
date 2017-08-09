from datetime import datetime
import asyncio
import re

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import delete_all, get_server_from_dm, MessageManager
from cogs.utils.checks import is_event, is_admin, is_int
from cogs.utils import constants


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def event(self, ctx):
        """Create an event. Update the events channel on success"""
        user = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        manager = MessageManager(self.bot, user, channel, [ctx.message])

        if channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        if not is_admin(user, channel):
            await manager.say("You must be an administrator to do that.")
            return await manager.clear()

        res = await manager.say_and_wait("Enter event title")
        if not res:
            return
        title = res.content

        description = ""
        res = await manager.say_and_wait("Enter event description (type 'none' for no description)")
        if not res:
            return
        if res.content.upper() != 'NONE':
            description = res.content

        max_members = 0
        while not max_members:
            res = await manager.say_and_wait("Enter the maximum numbers of attendees (type 'none' for no maximum)")
            if not res:
                return
            if res.content.upper() == 'NONE':
                break
            elif is_int(res.content) and int(res.content) > 0:
                print(int(res.content))
                max_members = int(res.content)
            else:
                await manager.say("That is not a a valid entry.")

        start_time = None
        while not start_time:
            res = await manager.say_and_wait("Enter event time (YYYY-MM-DD HH:MM AM/PM)")
            if not res:
                return
            start_time_format = '%Y-%m-%d %I:%M %p'
            try:
                start_time = datetime.strptime(res.content, start_time_format)
            except ValueError:
                await manager.say("Invalid event time!")

        time_zone = None
        while not time_zone:
            res = await manager.say_and_wait("Enter the time zone (PST, EST, etc.)")
            if not res:
                return
            if res.content.upper() not in constants.TIME_ZONES:
                await manager.say("Unsupported time zone")
            else:
                time_zone = res.content.upper()

        with DBase() as db:
            res = db.create_event(title, start_time, time_zone, server.id, description, max_members)
            if res == 0:
                await manager.say("An event with that name already exists.")
                return await manager.clear()

        event_channel = await self.get_events_channel(server)
        await manager.say("Event created! The " + event_channel.mention + " channel will be updated momentarily.")
        await manager.clear()
        await self.list_events(server)


    async def list_events(self, server):
        """Clear the event channel and display all upcoming events"""
        events_channel = await self.get_events_channel(server)
        await self.bot.purge_from(events_channel, limit=999, check=delete_all)
        with DBase() as db:
            events = db.get_events(server.id)
            if len(events) > 0:
                for row in events:
                    event_embed = self.create_event_embed(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                    msg = await self.bot.send_message(events_channel, embed=event_embed)
                    await self.bot.add_reaction(msg, "\N{WHITE HEAVY CHECK MARK}")
                    await self.bot.add_reaction(msg, "\N{CROSS MARK}")
            else:
                await self.bot.send_message(events_channel, "There are no upcoming events.")


    async def on_reaction_add(self, reaction, user):
        """If a reaction represents a user RSVP, update the DB and event message"""
        message = reaction.message
        server = message.server
        channel = message.channel
        manager = MessageManager(self.bot, user, channel)

        # We check that the user is not the message author as to not count
        # the initial reactions added by the bot as being indicative of attendance
        if is_event(message) and user is not message.author:

            title = message.embeds[0]['title']
            if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                await self.set_attendance(str(user), server.id, 1, title, message)
            elif reaction.emoji == "\N{CROSS MARK}":
                await self.set_attendance(str(user), server.id, 0, title, message)
            elif reaction.emoji == "\N{SKULL}":
                if is_admin(user, channel):
                    return await self.delete_event(server, title)
                else:
                    await manager.say("You must be an administrator to do that.")

            # Remove the reaction to keep the event message looking clean
            await asyncio.sleep(constants.REACTION_DELAY)
            await self.bot.remove_reaction(message, reaction.emoji, user)
            await manager.clear()


    async def set_attendance(self, username, server_id, attending, title, message):
        """Send updated event attendance info to db and update the event"""
        with DBase() as db:
            db.add_user(server_id, username)
            db.update_attendance(username, server_id, attending, title, datetime.now())

        # Update event message in place for a more seamless user experience
        with DBase() as db:
            event = db.get_event(server_id, title)
            event_embed = self.create_event_embed(event[0][0], event[0][1], event[0][2],
                                                  event[0][3], event[0][4], event[0][5], event[0][6])
            await self.bot.edit_message(message, embed=event_embed)


    async def delete_event(self, server, title):
        """Delete an event and update the events channel on success"""
        with DBase() as db:
            res = db.delete_event(server.id, title)
            if res:
                await self.list_events(server)


    async def get_events_channel(self, server):
        """Return the events channel if it exists, otherwise create one and return it"""
        for channel in server.channels:
            if channel.name == "upcoming-events":
                return channel

        # Need to make sure the bot can still send messages in the events channel
        users = discord.PermissionOverwrite(send_messages=False, add_reactions=True)
        me = discord.PermissionOverwrite(send_messages=True, add_reactions=True)
        channel = await self.bot.create_channel(server, "upcoming-events", (server.default_role, users), (server.me, me))
        return channel


    def create_event_embed(self, title, description, time, time_zone, accepted=None, declined=None, max_members=None):
        """Create and return a Discord Embed object that represents an upcoming event"""
        embed_msg = discord.Embed(color=constants.BLUE)
        embed_msg.set_footer(text="React with {} to remove this event".format('\U0001f480'))
        embed_msg.title = title

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
            for member in accepted_list:
                text += "{}\n".format(member.split("#")[0])
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
            for member in declined_list:
                text += "{}\n".format(member.split("#")[0])
            embed_msg.add_field(name="Declined", value=text)
        else:
            embed_msg.add_field(name="Declined", value="-")

        if accepted and max_members:
            standby_list = accepted.split(',')[max_members:]
            if standby_list:
                text = ""
                for member in standby_list:
                    text += "{}\n".format(member.split("#")[0])
                embed_msg.add_field(name="Standby", value=text, inline=False)

        return embed_msg


    async def on_server_available(self, server):
        """Refresh upcoming events when the bot starts so that the event messages
           are in the bot's cache so that wait_for_reaction() will work properly
           """
        await self.list_events(server)
