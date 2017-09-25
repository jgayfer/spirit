from datetime import datetime

import discord
from discord.ext import commands
import pytz
import psutil

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class General:

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()


    @commands.command()
    async def feedback(self, ctx, *, message):
        """
        Send a message to the bot's developer

        Ex. '!feedback Your bot is awesome!'
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        e = discord.Embed(title='Feedback', colour=constants.BLUE)
        e.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        e.description = message
        e.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            e.add_field(name='Server', value='{} (ID: {})'.format(ctx.guild.name, ctx.guild.id), inline=False)

        e.add_field(name='Channel', value='{} (ID: {})'.format(ctx.channel, ctx.channel.id), inline=False)
        e.set_footer(text='Author ID: {}'.format(ctx.author.id))

        feedback_channel = self.bot.get_channel(359848505654771715)
        if feedback_channel:
            await feedback_channel.send(embed=e)
        else:
            asal = await self.bot.get_user_info("118926942404608003")
            await asal.send(embed=e)

        await manager.say("Your feedback has been sent to the developer!")
        await manager.clear()


    @feedback.error
    async def feedback_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
            await manager.say("You forgot to include your feedback!")
            await manager.clear()


    @commands.command()
    async def about(self, ctx):
        """Display information about the bot itself"""
        embed = discord.Embed(colour=constants.BLUE)
        #embed.url = 'https://discordapp.com/oauth2/authorize?client_id=335084645743984641&scope=bot&permissions=523344'

        embed.description = ("[Invite Spirit](https://discordapp.com/oauth2/authorize?client_id=335084645743984641&scope=bot&permissions=523344)\n"
                           + "[Spirit Support Server](https://discord.gg/GXCFpkr)")

        owner = self.bot.get_user(118926942404608003)
        embed.set_author(name=str(owner), icon_url=owner.avatar_url)

        # statistics
        total_members = sum(1 for _ in self.bot.get_all_members())
        total_online = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.online})
        total_unique = len(self.bot.users)

        voice_channels = []
        text_channels = []
        for guild in self.bot.guilds:
            voice_channels.extend(guild.voice_channels)
            text_channels.extend(guild.text_channels)

        text = len(text_channels)
        voice = len(voice_channels)

        embed.add_field(name='Members', value='{} total\n{} unique\n{} unique online'.format(total_members, total_unique, total_online))
        embed.add_field(name='Channels', value='{} total\n{} text\n{} voice'.format(text + voice, text, voice))

        memory_usage = "%0.2f" % (self.process.memory_full_info().uss / 1024**2)
        cpu_usage = "%0.2f" % (self.process.cpu_percent() / psutil.cpu_count())
        embed.add_field(name='Process', value='{} MiB\n{}% CPU'.format(memory_usage, cpu_usage))

        embed.add_field(name='Guilds', value=len(self.bot.guilds))
        embed.add_field(name='Commands Run', value=self.bot.command_count)
        embed.add_field(name='Uptime', value=self.get_bot_uptime(brief=True))

        embed.set_footer(text='Made with discord.py', icon_url='http://i.imgur.com/5BFecvA.png')
        await ctx.send(embed=embed)


    def get_bot_uptime(self, *, brief=False):
        now = datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)


    async def on_guild_join(self, guild):
        """Send welcome message to the server owner"""
        message = ("Greetings! My name is **{}**, and my sole responsibility is to help you and "
                   "your group kick ass in Destiny 2! You're receiving this message because you "
                   "or one of your trusted associates has added me to **{}**.\n\n"
                   "**Command Prefix**\n\n"
                   "My default prefix is **!**, but you can also just mention me with **@{}**. "
                   "If another bot is already using the **!** prefix, you can choose a different prefix "
                   "for your server with **!settings setprefix <new_prefix>** (don't include the brackets).\n\n"
                   "For a list of all available commands, use the **!help** command. If you want more "
                   "information on a command, use **!help <command_name>**.\n\n"
                   "If you have any feedback, you can use my **!feedback** command to send "
                   "a message to my developer! If you want to request a feature, report a bug, "
                   "stay up to date with new features, or just want some extra help, check out the official "
                   "{} Support server! (https://discord.gg/GXCFpkr)"
                   ).format(self.bot.user.name, guild.name, self.bot.user.name,
                            self.bot.user.name, self.bot.user.name)
        await guild.owner.send(message)
