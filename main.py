from discord.ext import commands
from database import DBase
from datetime import datetime
import json
import discord
import asyncio

bot = commands.Bot(command_prefix='!')

@bot.group(pass_context=True)
async def event(ctx):

    if ctx.invoked_subcommand is None:
        await bot.say(ctx.message.author.mention + ": Invalid event command passed. Use '!event help' for more information.")


@event.command(pass_context=True)
async def create(ctx):

    await bot.say(ctx.message.author.mention + ": Enter event title")
    msg = await bot.wait_for_message(author=ctx.message.author)
    title = msg.content

    await bot.say(ctx.message.author.mention + ": Enter event description (type 'none' for no description)")
    msg = await bot.wait_for_message(author=ctx.message.author)
    description = ''
    if msg.content.upper() != 'NONE':
        description = msg.content

    start_time = None
    while not start_time:
        await bot.say(ctx.message.author.mention + ": Enter event time (YYYY-MM-DD HH:MM AM/PM)")
        msg = await bot.wait_for_message(author=ctx.message.author)
        start_time_str = msg.content
        start_time_format = '%Y-%m-%d %I:%M %p'
        try:
            start_time = datetime.strptime(start_time_str, start_time_format)
        except ValueError:
            await bot.say(ctx.message.author.mention + ": Invalid event time!")

    await bot.say(ctx.message.author.mention + ": Enter the time zone (PST, EST, etc.)")
    msg = await bot.wait_for_message(author=ctx.message.author)
    time_zone = msg.content.upper()

    with DBase() as db:
        db.create_event(title, start_time, time_zone, ctx.message.server.id, description)
    await bot.say(ctx.message.author.mention + ": Event has been created! Use '!event list' to display upcoming events in the events channel.")


@event.command(pass_context=True)
async def list(ctx):

    event_channel = None
    if ctx.message.channel.name != "upcoming-events":
        for channel in ctx.message.server.channels:
            if channel.name == "upcoming-events":
                event_channel = channel
                break
        if event_channel is None:
            event_channel = await bot.create_channel(ctx.message.server, "upcoming-events")
        return await bot.say(ctx.message.author.mention + ": That command can only be used in the 'upcoming-events' channel.")

    events = None
    with DBase() as db:
        events = db.get_events(ctx.message.server.id)
    if len(events) != 0:
        for row in events:
            embed_msg = discord.Embed(color=discord.Colour(3381759))
            embed_msg.title = row[1]
            if row[2]:
                embed_msg.description = row[2]
            embed_msg.add_field(name="Time", value=str(row[3]) + row[4], inline=False)
            embed_msg.add_field(name="Accepted", value=row[5])
            embed_msg.add_field(name="Declined", value=row[6])
            await bot.say(embed=embed_msg)


@bot.command(pass_context=True)
async def role(ctx, role="None"):

    if ctx.message.channel.is_private:
        return await bot.say(ctx.message.author.mention + ": That command is not supported in a direct message.")

    user = str(ctx.message.author)
    role = role.lower().title()
    server_id = ctx.message.server.id
    msg_res = None
    if role == "Titan" or role == "Warlock" or role == "Hunter":
        with DBase() as db:
            db.update_roster(user, role, server_id)
        msg_res = await bot.say(ctx.message.author.mention + ": Your role has been updated!")
    else:
        msg_res = await bot.say(ctx.message.author.mention + ": Oops! Role must be one of: Titan, Hunter, Warlock")

    await asyncio.sleep(5)
    await bot.delete_message(msg_res)
    await bot.delete_message(ctx.message)


@bot.command(pass_context=True)
async def roster(ctx):

    if ctx.message.channel.is_private:
        return await bot.say(ctx.message.author.mention + ": That command is not supported in a direct message.")

    with DBase() as db:
        roster = db.get_roster(ctx.message.server.id)
        if len(roster) != 0:
            message = "```\n"
            for row in roster:
                message += row[0].split("#")[0]
                spaces = 17 - len(row[0].split("#")[0])
                for _ in range (0, spaces):
                    message += " "
                message += row[1] + "\n"
            message += "```"
            embed_msg = discord.Embed(title="Destiny 2 Pre Launch Roster", description=message, color=discord.Colour(3381759))
            await bot.say(embed=embed_msg)
        else:
            msg_res = await bot.say(ctx.message.author.mention + ": No roles have been assigned yet. Use !role to select a role.")
            await asyncio.sleep(5)
            await bot.delete_message(msg_res)
            await bot.delete_message(ctx.message)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials['token']
    bot.run(token)
