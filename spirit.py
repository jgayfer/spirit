import json
import logging
import asyncio

import discord
from discord.ext import commands
import pydest

from db.dbase import DBase
from cogs.utils import constants
from cogs.events import Events
from cogs.roster import Roster
from cogs.help import Help
from cogs.settings import Settings
from cogs.general import General
from cogs.core import Core
from cogs.destiny import Destiny
from cogs.stats import Stats
from cogs.owner import Owner


async def _prefix_callable(bot, message):
    """Get current command prefix"""
    base = ['<@{}> '.format(bot.user.id)]
    if isinstance(message.channel, discord.abc.PrivateChannel):
        base.append('!')
    else:
        with DBase() as db:
            custom_prefix = db.get_prefix(message.guild.id)
            if len(custom_prefix) > 0 and len(custom_prefix[0]) > 0:
                base.append(custom_prefix[0][0])
    return base


bot = commands.AutoShardedBot(command_prefix=_prefix_callable)
with open('credentials.json') as f:
    api_key = json.load(f)['d2-api-key']
destiny = pydest.Pydest(api_key)

bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))
bot.add_cog(Help(bot))
bot.add_cog(Settings(bot))
bot.add_cog(General(bot))
bot.add_cog(Core(bot))
bot.add_cog(Destiny(bot, destiny))
bot.add_cog(Stats(bot, destiny))
bot.add_cog(Owner(bot))


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
