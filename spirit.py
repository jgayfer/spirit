import json
import logging
import asyncio

from discord.ext import commands

from db.dbase import DBase
from cogs.events import Events
from cogs.roster import Roster
from cogs.help import Help
from cogs.settings import Settings
from cogs.misc import Misc


async def _prefix_callable(bot, message):
    """Get the server's prefix"""
    if message.channel.is_private:
        if not message.content.startswith('!'):
            await bot.send_message(message.channel, message.author.mention + ": The ! prefix must be used in a direct message.")
        return '!'
    else:
        with DBase() as db:
            return db.get_prefix(message.server.id)


bot = commands.Bot(command_prefix=_prefix_callable)
bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))
bot.add_cog(Help(bot))
bot.add_cog(Settings(bot))
bot.add_cog(Misc(bot))


@bot.event
async def on_ready():
    """Display startup information"""
    print('Spirit v0.2.0\n')
    print('Username: {}'.format(bot.user.name))
    print('------')


@bot.event
async def on_server_join(server):
    """Add server and it's members to database"""
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
