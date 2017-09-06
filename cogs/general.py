from datetime import datetime
import textwrap

import discord
from discord.ext import commands
import pytz

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class General:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def countdown(self, ctx):
        """Show time until upcoming Destiny 2 releases"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        pst_now = datetime.now(tz=pytz.timezone('US/Pacific'))
        text = ""

        for name, date in constants.RELEASE_DATES:
            diff = date - pst_now
            days = diff.days + 1
            if days == 0:
                text += "{}: Today!\n".format(name)
            elif days == 1:
                text += "{}: Tomorrow!\n".format(name)
            elif days > 1:
                text += "{}: {} days\n".format(name, days)

        countdown = discord.Embed(title="Destiny 2 Countdown", color=constants.BLUE)
        countdown.description = text
        await manager.say(countdown, embed=True, delete=False)
        await manager.clear()


    @commands.command()
    async def feedback(self, ctx, *message):
        """
        Send a message to the bot's developer

        Ex. '!feedback Your bot is awesome!'
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if len(message) == 0:
            await manager.say("You forgot to include your feedback!")
            return await manager.clear()

        feedback = ""
        for word in message:
            feedback += "{} ".format(word)

        e = discord.Embed(title='Feedback', colour=constants.BLUE)
        e.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        e.description = feedback
        e.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            e.add_field(name='Server', value='{} (ID: {})'.format(ctx.guild.name, ctx.guild.id), inline=False)

        e.add_field(name='Channel', value='{} (ID: {})'.format(ctx.channel, ctx.channel.id), inline=False)
        e.set_footer(text='Author ID: {}'.format(ctx.author.id))

        asal = await self.bot.get_user_info("118926942404608003")
        await asal.send(embed=e)
        await manager.say("Your feedback has been sent to the developer!")
        await manager.clear()


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
            if guild.id != 264445053596991498 or guild.id != 110373943822540800:
                guild_users = [user for user in guild.members if user.id != self.bot.user.id]
                users.extend(guild_users)
        num_users = len(set(users))

        e = discord.Embed(title='{} Stats'.format(self.bot.user.name), colour=constants.BLUE)
        e.description = "**Servers**: {}\n**Users**: {}".format(num_guilds, num_users)
        e.timestamp = datetime.now(tz=pytz.timezone('US/Pacific'))
        await ctx.channel.send(embed=e)
        await manager.clear()


    async def on_guild_join(self, guild):
        """Send welcome message to the server owner"""
        message = ("Greetings! My name is **{}**, and my sole responsibility is to help you and "
                   "your group kick ass in Destiny 2! You're receiving this message because you "
                   "or one of your trusted associates has added me to **{}**.\n\n"
                   "**Command Prefix**\n\n"
                   "My default prefix is **!**, but you can also just mention me with **@{}**. "
                   "If another bot is already using the **!** prefix, you can choose a different prefix "
                   "for your server with **!setprefix <new_prefix>** (don't include the brackets).\n\n"
                   "For a list of all available commands, use the **!help** command. If you want more "
                   "information on a command, use **!help <command_name>**.\n\n"
                   "If you have any feedback, you can use my **!feedback** command to send "
                   "a message to my developer! If you want to request a feature, report a bug, "
                   "stay up to date with new features, or just want some extra help, check out the official "
                   "{} Support server! (https://discord.gg/GXCFpkr)"
                   ).format(self.bot.user.name, guild.name, self.bot.user.name,
                            self.bot.user.name, self.bot.user.name)
        await guild.owner.send(message)
