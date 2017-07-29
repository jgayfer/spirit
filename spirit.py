import json
import logging

from discord.ext import commands

from db.dbase import DBase
from cogs.events import Events
from cogs.roster import Roster
from cogs.help import Help


bot = commands.Bot(command_prefix='!')

bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))
bot.add_cog(Help(bot))


@bot.event
async def on_ready():
    """Display startup information"""
    print('Spirit v0.1.1')
    print('------')
    print('Username: {}'.format(bot.user.name))


@bot.event
async def on_server_join(server):
    """Add server to database"""
    with DBase() as db:
        db.add_server(server.id)


@bot.event
async def on_server_remove(server):
    """Remove server from database"""
    with DBase() as db:
        db.remove_server(server.id)


def setup_logging():
    """Enable logging to a file"""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    logger.addHandler(handler)


if __name__ == '__main__':
    setup_logging()
    with open('credentials.json') as f:
        token = json.load(f)['token']
        bot.run(token)
