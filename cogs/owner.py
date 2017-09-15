from datetime import datetime

import pytz
from discord.ext import commands
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants
from db.dbase import DBase


class Owner:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    @commands.is_owner()
    async def pm(self, ctx, user_id: int, *message):
        """Send a PM via the bot to a user given their ID"""
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
            await manager.say('Could not PM user with ID {}'.format(user_id))
        else:
            await manager.say('PM successfully sent.')
        await manager.clear()


    @commands.command(hidden=True)
    async def broadcast(self, ctx, *, message):
        """Send a message to the owner of every server the bot belongs to"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if ctx.author.id not in (182759337394044929, 118926942404608003):
            return

        count = 0
        for guild in self.bot.guilds:
            try:
                await guild.owner.send(message)
            except:
                pass
            else:
                count+= 1

        if ctx.author.id != 118926942404608003:
            asal = self.bot.get_user(118926942404608003)
            await asal.send("**{}** just sent out a broadcast message:\n\n{}".format(ctx.author.name, message))

        await manager.say("Broadcast message sent to **{}** users".format(count))
        await manager.clear()


    @broadcast.error
    async def broadcast_error(self, ctx, error):
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        await manager.say("You didn't include a broadcast message")
        return await manager.clear()


    @commands.command(hidden=True)
    async def botstats(self, ctx):
        """Displays the bot's stats"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if ctx.author.id not in (182759337394044929, 118926942404608003):
            return

        num_guilds = len(self.bot.guilds)
        users = []
        for guild in self.bot.guilds:
            if guild.id not in (264445053596991498, 110373943822540800, 349975342884061187):
                guild_users = [user for user in guild.members if not user.bot]
                users.extend(guild_users)
        num_users = len(set(users))

        e = discord.Embed(title='{} Stats'.format(self.bot.user.name), colour=constants.BLUE)
        e.description = "**Servers**: {}\n**Users**: {}".format(num_guilds, num_users)
        await ctx.channel.send(embed=e)
        await manager.clear()
