import json

from discord.ext import commands

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
    print('Servers: {}'.format(len(bot.servers)))


if __name__ == '__main__':
    with open('credentials.json') as f:
        token = json.load(f)['token']
        bot.run(token)
