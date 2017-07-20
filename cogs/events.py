from discord.ext import commands
from db.dbase import DBase
from datetime import datetime
import discord
import asyncio
import re


class Events:

    def __init__(self, bot):
        self.bot = bot


    @commands.group(pass_context=True)
    async def event(self, ctx):

        if ctx.invoked_subcommand is None:
            return await self.bot.say(ctx.message.author.mention
                                      + ": Invalid event command passed. "
                                      + "Use '!event help' to view available commands.")


    @event.command(pass_context=True)
    async def create(self, ctx):

        if not await self.events_channel(ctx):
            return

        await self.bot.say(ctx.message.author.mention + ": Enter event title")
        msg = await self.bot.wait_for_message(author=ctx.message.author)
        title = msg.content

        await self.bot.say(ctx.message.author.mention
                           + ": Enter event description (type 'none' for no description)")
        msg = await self.bot.wait_for_message(author=ctx.message.author)
        description = ''
        if msg.content.upper() != 'NONE':
            description = msg.content

        start_time = None
        while not start_time:
            await self.bot.say(ctx.message.author.mention
                               + ": Enter event time (YYYY-MM-DD HH:MM AM/PM)")
            msg = await self.bot.wait_for_message(author=ctx.message.author)
            start_time_str = msg.content
            start_time_format = '%Y-%m-%d %I:%M %p'
            try:
                start_time = datetime.strptime(start_time_str, start_time_format)
            except ValueError:
                await self.bot.say(ctx.message.author.mention + ": Invalid event time!")

        await self.bot.say(ctx.message.author.mention + ": Enter the time zone (PST, EST, etc.)")
        msg = await self.bot.wait_for_message(author=ctx.message.author)
        time_zone = msg.content.upper()

        with DBase() as db:
            db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
        await self.bot.say(ctx.message.author.mention
                           + ": Event has been created! "
                           + "The list of upcoming events will be updated momentarily.")
        await asyncio.sleep(4)
        await self.list_events(ctx)


    async def list_events(self, ctx):

        # Clear the event channel and display all upcoming events
        events = None
        with DBase() as db:
            events = db.get_events(ctx.message.server.id)
        if len(events) != 0:
            await self.bot.purge_from(ctx.message.channel, limit=999, check=self.check_delete)
            for row in events:
                embed_msg = discord.Embed(color=discord.Colour(3381759))
                embed_msg.set_footer(text="Use '!event delete "
                                           + str(row[0]) + "' to remove this event")
                embed_msg.title = row[1]
                if row[2]:
                    embed_msg.description = row[2]
                embed_msg.add_field(name="Time", value=str(row[3]) + row[4], inline=False)
                embed_msg.add_field(name="Accepted", value=row[5])
                embed_msg.add_field(name="Declined", value=row[6])
                msg = await self.bot.say(embed=embed_msg)
                await self.bot.add_reaction(msg, "\N{WHITE HEAVY CHECK MARK}")
                await self.bot.add_reaction(msg, "\N{CROSS MARK}")


    async def on_reaction_add(self, reaction, user):

        # If reaction is indicating event attendance,
        # update the database and remove the reaction
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


    async def events_channel(self, ctx):

        # Check if the user is in the events channel (True is yes, False otherwise)
        # Create the events channel if it doesn't exist
        event_channel = None
        if ctx.message.channel.name != "upcoming-events":
            for channel in ctx.message.server.channels:
                if channel.name == "upcoming-events":
                    event_channel = channel
                    break
            if event_channel is None:
                event_channel = await bot.create_channel(ctx.message.server, "upcoming-events")
            await self.bot.say(ctx.message.author.mention + ": That command can only be used in the "
                          + event_channel.mention + " channel.")
            return False
        else:
            return True


    # Helper function used to delete all messages
    def check_delete(self, m):
        return True;
