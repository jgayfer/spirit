import json
import logging
import asyncio

import discord
from discord.ext import commands

from db.dbase import DBase
from cogs.utils import constants
from cogs.events import Events
from cogs.roster import Roster
from cogs.help import Help
from cogs.settings import Settings
from cogs.general import General
from cogs.core import Core
from cogs.destiny import Destiny


async def _prefix_callable(bot, message):
    """Get current command prefix"""
    base = ['<@{}> '.format(bot.user.id)]
    if isinstance(message.channel, discord.abc.PrivateChannel):
        base.append('!')
    else:
        with DBase() as db:
            base.append(db.get_prefix(message.guild.id))
    return base


bot = commands.Bot(command_prefix=_prefix_callable)
bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))
bot.add_cog(Help(bot))
bot.add_cog(Settings(bot))
bot.add_cog(General(bot))
bot.add_cog(Core(bot))
bot.add_cog(Destiny(bot))


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
