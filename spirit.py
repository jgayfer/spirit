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
    with DBase() as db:
        prefix = db.get_prefix(str(message.author))
        if prefix:
            return prefix
    await bot.send_message(message.channel, "That command won't work in a DM as you are part of multiple "
                                          + "servers running this bot - I don't know which server you are from!")

    # Return dummy prefix to make sure no commands run, and no errors are thrown
    return "-()76"

bot = commands.Bot(command_prefix=_prefix_callable)
bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))
bot.add_cog(Help(bot))
bot.add_cog(Settings(bot))
bot.add_cog(Misc(bot))


@bot.event
async def on_ready():
    """Display startup information"""
    print('Spirit v0.1.1')
    print('Username: {}'.format(bot.user.name))
    print('------')


@bot.event
async def on_server_join(server):
    """Add server and it's members to database"""
    with DBase() as db:
        db.add_server(server.id)
        for user in server.members:
            if user.id != bot.user.id:
                db.add_user(server.id, str(user))


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
