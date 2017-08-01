from datetime import datetime
import asyncio
import re

from discord.ext import commands
from db.dbase import DBase
import discord

from cogs.utils.messages import delete_all, MessageManager
from cogs.utils.checks import is_event
from cogs.utils import constants


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.group(pass_context=True)
    async def event(self, ctx):
        """Base event command"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        if ctx.invoked_subcommand is None:
            await manager.say("Invalid event command. Use '!help' to view available commands.")
            return await manager.clear()


    @event.command(pass_context=True)
    async def create(self, ctx):
        """Create an event. Update the events channel on success"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        if ctx.message.channel.is_private:
            # To Do - Add check if user is admin
            return
        else:
            if not user.server_permissions.administrator:
                await manager.say("You must be an admin to do that.")
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
            if res.content.upper() not in constants.time_zones:
                await manager.say("Unsupported time zone")
            else:
                time_zone = res.content.upper()

        with DBase() as db:
            res = db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
            if res == 0:
                await manager.say("That event already exists!")
                return await manager.clear()

        event_channel = await self.get_events_channel(ctx.message.server)
        await manager.say("Event created! The " + event_channel.mention + " channel will be updated momentarily.")
        await manager.clear()
        await self.list_events(ctx.message.server)


    async def list_events(self, server):
        """Clear the event channel and display all upcoming events"""
        events_channel = await self.get_events_channel(server)
        await self.bot.purge_from(events_channel, limit=999, check=delete_all)
        with DBase() as db:
            events = db.get_events(server.id)
            if len(events) > 0:
                for row in events:
                    event_embed = self.create_event_embed(row[0], row[1], row[2], row[3], row[4], row[5])
                    msg = await self.bot.send_message(events_channel, embed=event_embed)
                    await self.bot.add_reaction(msg, "\N{WHITE HEAVY CHECK MARK}")
                    await self.bot.add_reaction(msg, "\N{CROSS MARK}")
            else:
                await self.bot.send_message(events_channel, "There are no upcoming events.")


    async def on_reaction_add(self, reaction, user):
        """If a reaction represents a user RSVP, update the DB and event message"""
        message = reaction.message
        server = message.server

        # We check that the user is not the message author as to not count
        # the initial reactions added by the bot as being indicative of attendance
        if is_event(message) and user is not message.author:

            title = message.embeds[0]['title']

            if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                await self.set_attendance(str(user), server.id, 1, title)
            elif reaction.emoji == "\N{CROSS MARK}":
                await self.set_attendance(str(user), server.id, 0, title)
            elif reaction.emoji == "\N{SKULL}":
                return await self.delete_event(server, title)

            # Update event message in place for a more seamless user experience
            with DBase() as db:
                event = db.get_event(server.id, title)
                event_embed = self.create_event_embed(event[0][0], event[0][1], event[0][2],
                                                      event[0][3], event[0][4], event[0][5])
                await self.bot.edit_message(message, embed=event_embed)

            # Remove the reaction to keep the event message looking clean
            await asyncio.sleep(constants.REACTION_DELAY)
            await self.bot.remove_reaction(message, reaction.emoji, user)


    async def set_attendance(self, username, server_id, attending, title):
        """Send updated event attendance info to db"""
        with DBase() as db:
            db.update_attendance(username, server_id, attending, title)


    async def delete_event(self, server, title):
        """Delete an event. Update the events channel on success"""
        with DBase() as db:
            db.delete_event(server.id, title)
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


    def create_event_embed(self, title, description, time, time_zone, accepted=None, declined=None):
        """Create and return a Discord Embed object that represents an upcoming event"""
        embed_msg = discord.Embed(color=constants.BLUE)
        embed_msg.set_footer(text="React with {} to remove this event".format('\U0001f480'))
        embed_msg.title = title

        if description:
            embed_msg.description = description
        time_str = time.strftime("%A %b %-d, %Y @ %-I:%M %p")
        embed_msg.add_field(name="Time", value=time_str + " " + time_zone, inline=False)

        if accepted:
            accepted = accepted.split(',')
            accepted_list = ""
            for member in accepted:
                accepted_list += "{}\n".format(member.split("#")[0])
            embed_msg.add_field(name="Accepted", value=accepted_list)
        else:
            embed_msg.add_field(name="Accepted", value="-")

        if declined:
            declined = declined.split(',')
            declined_list = ""
            for member in declined:
                declined_list += "{}\n".format(member.split("#")[0])
            embed_msg.add_field(name="Declined", value=declined_list)
        else:
            embed_msg.add_field(name="Declined", value="-")
        return embed_msg


    async def on_server_available(self, server):
        """Refresh upcoming events when the bot starts so that the event messages
           are in the bot's cache so that wait_for_reaction will work properly
           """
        await self.list_events(server)
