import json

from discord.ext import commands

from utils.admin import load_credentials
from cogs.events import Events
from cogs.roster import Roster


bot = commands.Bot(command_prefix='!')
bot.add_cog(Events(bot))
bot.add_cog(Roster(bot))


@bot.event
async def on_ready():
    """Display startup information"""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials['token']
    bot.run(token)
