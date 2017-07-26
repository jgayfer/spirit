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
        if ctx.invoked_subcommand is None:
            await manager.say("Invalid event command. Use '!help' to view available commands.")
            return await clear_messages(self.bot, [ctx.message, m])

    @event.command(pass_context=True)
    async def create(self, ctx):
        """Create an event. Update the events channel on success"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        if not user.server_permissions.manage_server:
            await manager.say("You must have the Manage Server permission to do that.")
            return await manager.clear()

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        res = await manager.say_and_wait("Enter event title")
        title = res.content

        description = ""
        res = await manager.say_and_wait("Enter event description (type 'none' for no description)")
        if res.content.upper() != 'NONE':
            description = res.content

        start_time = None
        while not start_time:
            res = await manager.say_and_wait("Enter event time (YYYY-MM-DD HH:MM AM/PM)")
            start_time_format = '%Y-%m-%d %I:%M %p'
            try:
                start_time = datetime.strptime(res.content, start_time_format)
            except ValueError:
                await manager.say("Invalid event time!")

        time_zone = None
        while not time_zone:
            res = await manager.say_and_wait("Enter the time zone (PST, EST, etc.)")
            if res.content.upper() not in constants.time_zones:
                await manager.say("Unsupported time zone")
            else:
                time_zone = res.content.upper()

        with DBase() as db:
            db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
        await manager.say("Event has been created! The list of upcoming events will be updated momentarily.")

        await manager.clear()
        await self.list_events(ctx.message.server)

    @event.command(pass_context=True)
    async def delete(self, ctx, event_id=None):
        """Delete an event. Update the events channel on success"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        if not user.server_permissions.manage_server:
            await manager.say("You must have the Manage Server permission to do that.")
            return await manager.clear()

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await manager.say("That command is not supported in a direct message.")

        deleted = None
        if event_id is not None:
            with DBase() as db:
                affected_count = db.delete_event(event_id)
                if affected_count > 0:
                    deleted = True
                    await manager.say("Event successfuly deleted. "
                                    + "The list of upcoming events will be updated momentarily.")
                else:
                    await manager.say("That event doesn't exist.")
        else:
            await manager.say("An event ID must be specified! (Eg. '!event delete 117')")
        await manager.clear()

        # Event list needs to be updated since we removed one
        if deleted:
            await self.list_events(ctx.message.server)

    async def list_events(self, server):
        """Clear the event channel and display all upcoming events"""
        events_channel = await self.get_events_channel(server)
        await self.bot.purge_from(events_channel, limit=999, check=delete_all)
        with DBase() as db:
            events = db.get_events(server.id)
            for row in events:
                event_embed = self.create_event_embed(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                msg = await self.bot.send_message(events_channel, embed=event_embed)
                await self.bot.add_reaction(msg, "\N{WHITE HEAVY CHECK MARK}")
                await self.bot.add_reaction(msg, "\N{CROSS MARK}")

    async def on_reaction_add(self, reaction, user):
        """If a reaction represents a user RSVP, update the DB and event message"""
        message = reaction.message

        # We check that the user is not the message author as to not count
        # the initial reactions added by the bot as being indicative of attendance
        if is_event(message) and user is not message.author:

            attending = None
            if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                attending = 1
            elif reaction.emoji == "\N{CROSS MARK}":
                attending = 0

            if attending is not None:
                with DBase() as db:
                    event_id = re.search('\d+', message.embeds[0]['footer']['text']).group()
                    db.update_attendance(user.name, event_id, attending)

                # Update event message in place for a more seamless user experience
                with DBase() as db:
                    event = db.get_event(event_id)
                    event_embed = self.create_event_embed(event_id, event[0][0], event[0][1], event[0][2],
                                                          event[0][3], event[0][4], event[0][5])
                    await self.bot.edit_message(reaction.message, embed=event_embed)

            # Remove the reaction to keep the event message looking clean
            await asyncio.sleep(constants.REACTION_DELAY)
            await self.bot.remove_reaction(message, reaction.emoji, user)

    async def get_events_channel(self, server):
        """Return the events channel if it exists, otherwise create one and return it"""
        for channel in server.channels:
            if channel.name == "upcoming-events":
                return channel

        overwrite = discord.PermissionOverwrite(send_messages=False, add_reactions=True)
        return await self.bot.create_channel(server, "upcoming-events", (server.default_role, overwrite))

    def create_event_embed(self, id, title, description, time, time_zone, accepted=None, declined=None):
        """Create and return a Discord Embed object that represents an upcoming event"""
        embed_msg = discord.Embed(color=constants.BLUE)
        embed_msg.set_footer(text="Use '!event delete " + str(id) + "' to remove this event")
        embed_msg.title = title

        if description:
            embed_msg.description = description
        time_str = time.strftime("%A %b %-d, %Y @ %-I:%M %p")
        embed_msg.add_field(name="Time", value=time_str + " " + time_zone, inline=False)

        if accepted:
            accepted = accepted.split(',')
            accepted_list = ""
            for member in accepted:
                accepted_list += "{}\n".format(member)
            embed_msg.add_field(name="Accepted", value=accepted_list)
        else:
            embed_msg.add_field(name="Accepted", value="-")

        if declined:
            declined = declined.split(',')
            declined_list = ""
            for member in declined:
                declined_list += "{}\n".format(member)
            embed_msg.add_field(name="Declined", value=declined_list)
        else:
            embed_msg.add_field(name="Declined", value="-")

        return embed_msg

    async def on_server_available(self, server):
        """Refresh upcoming events when the bot starts so that the event messages
           are in the bot's cache so that wait_for_reaction will work properly
           """
        await self.list_events(server)
