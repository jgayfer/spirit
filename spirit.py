from discord.ext import commands
from db.dbase import DBase
from datetime import datetime
import cogs.events as events
import cogs.roster as roster
import json
import discord
import asyncio
import re


bot = commands.Bot(command_prefix='!')
bot.add_cog(events.Events(bot))
bot.add_cog(roster.Roster(bot))


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
