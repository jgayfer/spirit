from datetime import datetime

import pytz
from discord.ext import commands
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Owner:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    @commands.is_owner()
    async def pm(self, ctx, user_id: int, *message):

        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        user = self.bot.get_user(user_id)

        if len(message) == 0:
            await manager.say("You forgot to include your message!")
            return await manager.clear()

        response = "You have received a message from my developer:\n\n**"
        for word in message:
            response += "{} ".format(word)
        response += ("**\n\nYour response will not be tracked here. If you wish "
                   + "to speak with him further, join the official **{} Support** "
                   + "server - https://discord.gg/GXCFpkr").format(self.bot.user.name)

        try:
            await user.send(response)
        except:
            await ctx.send('Could not PM user with ID {}'.format(user_id))
        else:
            await ctx.send('PM successfully sent.')


    @commands.command(hidden=True)
    @commands.is_owner()
    async def botstats(self, ctx):
        """Displays the bot's stats"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        num_guilds = len(self.bot.guilds)
        users = []
        for guild in self.bot.guilds:
            if guild.id not in (264445053596991498, 110373943822540800, 349975342884061187):
                guild_users = [user for user in guild.members if user.id != self.bot.user.id]
                users.extend(guild_users)
        num_users = len(set(users))

        e = discord.Embed(title='{} Stats'.format(self.bot.user.name), colour=constants.BLUE)
        e.description = "**Servers**: {}\n**Users**: {}".format(num_guilds, num_users)
        e.timestamp = datetime.now(tz=pytz.timezone('US/Pacific'))
        await ctx.channel.send(embed=e)
        await manager.clear()
