from discord.ext import commands
from db.dbase import DBase
from datetime import datetime
from utils.messages import delete_all, clear_messages
import discord
import asyncio
import re


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.group(pass_context=True)
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            m = await self.bot.say(ctx.message.author.mention
                                   + ": Invalid event command passed. "
                                   + "Use '!event help' to view available commands.")
            return await clear_messages(self.bot, [ctx.message, m])


    @event.command(pass_context=True)
    async def create(self, ctx):

        # Check if the user has the permissions to create events
        if not ctx.message.author.server_permissions.manage_server:
            m = await self.bot.say(ctx.message.author.mention
                                     + ": Sorry, you must have the Manage Server permission to do that.")
            return await bot.clear_messages(bot, [ctx.message, m])

        # Return if the user is in a private message
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        # Get event title from user
        to_delete = [ctx.message]
        m1 = await self.bot.say(ctx.message.author.mention + ": Enter event title")
        m2 = await self.bot.wait_for_message(author=ctx.message.author)
        if m2.content.startswith('!'):
            to_delete.append(m1)
            return await clear_messages(self.bot, to_delete)
        to_delete.extend((m1, m2))
        title = m2.content

        # Get description from user
        m1 = await self.bot.say(ctx.message.author.mention + ": Enter event description (type 'none' for no description)")
        m2 = await self.bot.wait_for_message(author=ctx.message.author)
        if m2.content.startswith('!'):
            to_delete.append(m1)
            return await clear_messages(self.bot, to_delete)
        to_delete.extend((m1, m2))
        description = ''
        if m2.content.upper() != 'NONE':
            description = m2.content

        # Get start time from user
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

        # Get time zone from user
        m1 = await self.bot.say(ctx.message.author.mention + ": Enter the time zone (PST, EST, etc.)")
        m2 = await self.bot.wait_for_message(author=ctx.message.author)
        if m2.content.startswith('!'):
            to_delete.append(m1)
            return await clear_messages(self.bot, to_delete)
        to_delete.extend((m1, m2))
        time_zone = m2.content.upper()

        # Add event to the database
        with DBase() as db:
            db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
        m = await self.bot.say(ctx.message.author.mention
                               + ": Event has been created! "
                               + "The list of upcoming events will be updated momentarily.")
        to_delete.append(m)

        # Clean up messages and update events channel
        await clear_messages(self.bot, to_delete)
        await self.list_events(ctx.message.server)


    @event.command(pass_context=True)
    async def delete(self, ctx, event_id=None):

        # Check if the user has the permissions to create events
        if not ctx.message.author.server_permissions.manage_server:
            m = await self.bot.say(ctx.message.author.mention
                                     + ": Sorry, you must have the Manage Server permission to do that.")
            return await bot.clear_messages(bot, [ctx.message, m])

        # Return if the user is in a private message
        if ctx.message.channel.is_private:
            return await self.bot.say(ctx.message.author.mention
                                      + ": That command is not supported in a direct message.")

        # Attempt to delete the event
        deleted = False
        to_delete = [ctx.message]
        if event_id is not None:
            with DBase() as db:
                affected_count = db.delete_event(event_id)
                if affected_count > 0:
                    deleted = True
            if deleted:
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

        # Clean up messages and update the events channel if event was deleted
        await clear_messages(self.bot, to_delete)
        if deleted:
            await self.list_events(ctx.message.server)


    async def list_events(self, server):

        # Clear the event channel and display all upcoming events
        events = None
        events_channel = await self.get_events_channel(server)
        await self.bot.purge_from(events_channel, limit=999, check=delete_all)
        with DBase() as db:
            events = db.get_events(server.id)
        if len(events) != 0:
            for row in events:
                embed_msg = discord.Embed(color=discord.Colour(3381759))
                embed_msg.set_footer(text="Use '!event delete " + str(row[0]) + "' to remove this event")
                embed_msg.title = row[1]
                if row[2]:
                    embed_msg.description = row[2]
                embed_msg.add_field(name="Time", value=str(row[3]) + row[4], inline=False)
                embed_msg.add_field(name="Accepted", value=row[5])
                embed_msg.add_field(name="Declined", value=row[6])
                msg = await self.bot.send_message(events_channel, embed=embed_msg)
                await self.bot.add_reaction(msg, "\N{WHITE HEAVY CHECK MARK}")
                await self.bot.add_reaction(msg, "\N{CROSS MARK}")


    async def on_reaction_add(self, reaction, user):

        # If reaction is indicating event attendance, update the database
        channel_name = reaction.message.channel.name
        author = reaction.message.author
        num_embeds = len(reaction.message.embeds)
        if (channel_name == "upcoming-events"
                and author == self.bot.user
                and num_embeds is not 0
                and user is not author):
            username = user.name
            footer = reaction.message.embeds[0]['footer']['text']
            event_id = re.search('\d+', footer).group()
            attending = None
            if reaction.emoji == "\N{WHITE HEAVY CHECK MARK}":
                attending = 1
            elif reaction.emoji == "\N{CROSS MARK}":
                attending = 0
            else:
                await asyncio.sleep(0.5)
                return await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
            with DBase() as db:
                db.update_attendance(username, event_id, attending)

            # Update contents of event message
            event = None
            with DBase() as db:
                event = db.get_event(event_id)
            embed_msg = discord.Embed(color=discord.Colour(3381759))
            embed_msg.set_footer(text="Use '!event delete " + event_id + "' to remove this event")
            embed_msg.title = event[0][0]
            if event[0][1]:
                embed_msg.description = event[0][1]
            embed_msg.add_field(name="Time", value=str(event[0][2]) + event[0][3], inline=False)
            embed_msg.add_field(name="Accepted", value=event[0][4])
            embed_msg.add_field(name="Declined", value=event[0][5])
            await self.bot.edit_message(reaction.message, embed=embed_msg)

            # Remove reaction
            await asyncio.sleep(0.5)
            await self.bot.remove_reaction(reaction.message, reaction.emoji, user)


    async def get_events_channel(self, server):

        # Return the event channel if it already exists
        for channel in server.channels:
            if channel.name == "upcoming-events":
                return channel

        # Otherwise, create an event channel and return it
        return await self.bot.create_channel(server, "upcoming-events")


    # When the bot starts, refresh the events channel
    # We do this because messages need to be in the bot's cache in order for
    # wait_for_reaction() to work properly
    async def on_server_available(self, server):
        await self.list_events(server)
