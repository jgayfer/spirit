from datetime import datetime
import asyncio
import re

from discord.ext import commands
from db.dbase import DBase
import discord

from utils.messages import delete_all, clear_messages
import utils.constants as constants


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.group(pass_context=True)
    async def event(self, ctx):
        """Base event command"""
        if ctx.invoked_subcommand is None:
            m = await self.bot.say(ctx.message.author.mention
                                   + ": Invalid event command passed. "
                                   + "Use '!event help' to view available commands.")
            return await clear_messages(self.bot, [ctx.message, m])


    @event.command(pass_context=True)
    async def create(self, ctx):
        """Create an event. Update the events channel on success"""
        if not ctx.message.author.server_permissions.manage_server:
            m = await self.bot.say(ctx.message.author.mention
                                     + ": Sorry, you must have the Manage Server permission to do that.")
            return await bot.clear_messages(bot, [ctx.message, m])

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        to_delete = [ctx.message]
        m1 = await self.bot.say(ctx.message.author.mention + ": Enter event title")
        m2 = await self.bot.wait_for_message(author=ctx.message.author)
        if m2.content.startswith('!'):
            to_delete.append(m1)
            return await clear_messages(self.bot, to_delete)
        to_delete.extend((m1, m2))
        title = m2.content

        m1 = await self.bot.say(ctx.message.author.mention + ": Enter event description (type 'none' for no description)")
        m2 = await self.bot.wait_for_message(author=ctx.message.author)
        if m2.content.startswith('!'):
            to_delete.append(m1)
            return await clear_messages(self.bot, to_delete)
        to_delete.extend((m1, m2))
        description = ''
        if m2.content.upper() != 'NONE':
            description = m2.content

        start_time = None
        while not start_time:
            m1 = await self.bot.say(ctx.message.author.mention + ": Enter event time (YYYY-MM-DD HH:MM AM/PM)")
            m2 = await self.bot.wait_for_message(author=ctx.message.author)
            if m2.content.startswith('!'):
                to_delete.append(m1)
                return await clear_messages(self.bot, to_delete)
            to_delete.extend((m1, m2))
            start_time_str = m2.content
            start_time_format = '%Y-%m-%d %I:%M %p'
            try:
                start_time = datetime.strptime(start_time_str, start_time_format)
            except ValueError:
                m3 = await self.bot.say(ctx.message.author.mention + ": Invalid event time!")
                to_delete.append(m3)

        time_zone = None
        while not time_zone:
            m1 = await self.bot.say(ctx.message.author.mention + ": Enter the time zone (PST, EST, etc.)")
            m2 = await self.bot.wait_for_message(author=ctx.message.author)
            to_delete.append(m1)
            if m2.content.startswith('!'):
                to_delete.append(m1)
                return await clear_messages(self.bot, to_delete)
            elif len(m2.content) > 5:
                m3 =  await self.bot.say(ctx.message.author.mention
                                         + ": Time zone must be less than 6 characters!")
                to_delete.extend((m2,m3))
            else:
                to_delete.append(m2)
                time_zone = m2.content.upper()

        with DBase() as db:
            db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
        m = await self.bot.say(ctx.message.author.mention
                               + ": Event has been created! "
                               + "The list of upcoming events will be updated momentarily.")
        to_delete.append(m)

        await clear_messages(self.bot, to_delete)
        await self.list_events(ctx.message.server)


    @event.command(pass_context=True)
    async def delete(self, ctx, event_id=None):
        """Delete an event. Update the events channel on success"""
        if not ctx.message.author.server_permissions.manage_server:
            m = await self.bot.say(ctx.message.author.mention
                                     + ": Sorry, you must have the Manage Server permission to do that.")
            return await bot.clear_messages(bot, [ctx.message, m])

        # Return if the user is in a private message as events are server specific
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        deleted = None
        to_delete = [ctx.message]
        if event_id is not None:
            with DBase() as db:
                affected_count = db.delete_event(event_id)
                if affected_count > 0:
                    deleted = True
                    m = await self.bot.say(ctx.message.author.mention
                                           + ": Event successfuly deleted. The list of upcoming "
                                           + "events will be updated momentarily.")
                    to_delete.append(m)
                else:
                    m = await self.bot.say(ctx.message.author.mention + ": That event doesn't exist.")
                    to_delete.append(m)
        else:
            m = await self.bot.say(ctx.message.author.mention
                                   + ": An event ID must be specified! (Eg. '!event delete 117')")
            to_delete.append(m)

        await clear_messages(self.bot, to_delete)
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
        channel = reaction.message.channel
        message = reaction.message
        num_embeds = len(message.embeds)

        if (channel.name == "upcoming-events"
                and message.author == self.bot.user
                and num_embeds is not 0
                and user is not message.author):

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
        return await self.bot.create_channel(server, "upcoming-events")


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
