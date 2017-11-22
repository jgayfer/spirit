import json
import datetime
import asyncio

import discord
from discord.ext import commands
import pydest
import aioredis

from db.dbase import DBase
from cogs.events import Events
from cogs.roster import Roster
from cogs.help import Help
from cogs.settings import Settings
from cogs.general import General
from cogs.core import Core
from cogs.stats import Stats
from cogs.owner import Owner
from cogs.item import Item
from cogs.register import Register
from cogs.loadout import Loadout
from cogs.destiny import Destiny


async def _prefix_callable(bot, message):
    """Get current command prefix"""
    base = ['<@{}> '.format(bot.user.id)]
    if isinstance(message.channel, discord.abc.PrivateChannel):
        base.append('!')
    else:
        result = bot.db.get_prefix(message.guild.id)
        if result:
            base.append(result.get('prefix'))
        else:
            bot.db.add_guild(message.guild.id)
            base.append('!')
    return base


class Spirit(commands.AutoShardedBot):

    def __init__(self, token, bungie_api_key, bungie_client_id):
        super().__init__(command_prefix=_prefix_callable)
        self.token = token
        self.db = DBase('credentials.json')
        self.destiny = pydest.Pydest(bungie_api_key)
        self.bungie_client_id = bungie_client_id
        self.uptime = datetime.datetime.utcnow()
        self.command_count = 0

    def run(self):
        super().run(self.token, reconnect=True)

    async def on_command(self, ctx):
        self.command_count += 1


if __name__ == '__main__':

    # Get configuration from file
    with open('credentials.json') as f:
        file_dict = json.load(f)
    token = file_dict['token']
    bungie_api_key = file_dict['d2-api-key']
    bungie_client_id = file_dict['client-id']

    bot = Spirit(token, bungie_api_key, bungie_client_id)

    # Add modules to bot
    bot.add_cog(Core(bot))
    bot.add_cog(Events(bot))
    bot.add_cog(General(bot))
    bot.add_cog(Help(bot))
    bot.add_cog(Owner(bot))
    bot.add_cog(Roster(bot))
    bot.add_cog(Settings(bot))
    bot.add_cog(Stats(bot))
    bot.add_cog(Item(bot))
    bot.add_cog(Register(bot))
    bot.add_cog(Loadout(bot))
    bot.add_cog(Destiny(bot))

    bot.run()
