from datetime import datetime

import discord
from discord.ext import commands
import psutil
import pytz

from cogs.utils.message_manager import MessageManager
from cogs.utils import constants


class General:

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def countdown(self, ctx):
        """Show time until upcoming Destiny 2 releases"""
        manager = MessageManager(ctx)
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

        if not text:
            text = "There are no concrete dates for our next adventure..."

        countdown = discord.Embed(title="Destiny 2 Countdown", color=constants.BLUE)
        countdown.description = text
        await manager.send_embed(countdown)
        await manager.clean_messages()


    @commands.command()
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.user)
    async def feedback(self, ctx, *, message):
        """
        Send a message to the bot's developer

        Ex. '!feedback Your bot is awesome!'

        This command was adapted from RoboDanny by Rapptz - https://www.github.com/Rapptz/RoboDanny
        """
        manager = MessageManager(ctx)

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

        await manager.send_message("Your feedback has been sent to the developer!")
        await manager.clean_messages()


    @feedback.error
    async def feedback_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(ctx)
            await manager.send_message("You forgot to include your feedback!")
            await manager.clean_messages()


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def about(self, ctx):
        """Display information about the bot itself

        This command was adapted from RoboDanny by Rapptz - https://www.github.com/Rapptz/RoboDanny
        """
        manager = MessageManager(ctx)
        e = discord.Embed(title='Spirit v{}'.format(constants.VERSION), colour=constants.BLUE)

        e.description = ("[Invite Spirit](https://discordapp.com/oauth2/authorize?client_id=335084645743984641&scope=bot&permissions=523344)\n"
                           + "[Spirit Support Server](https://discord.gg/GXCFpkr)")

        owner = self.bot.get_user(118926942404608003)
        e.set_author(name=str(owner), icon_url=owner.avatar_url)

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

        e.add_field(name='Members', value='{} total\n{} unique\n{} unique online'.format(total_members, total_unique, total_online))
        e.add_field(name='Channels', value='{} total\n{} text\n{} voice'.format(text + voice, text, voice))

        memory_usage = "%0.2f" % (self.process.memory_full_info().uss / 1024**2)
        cpu_usage = "%0.2f" % (self.process.cpu_percent() / psutil.cpu_count())
        e.add_field(name='Process', value='{} MiB\n{}% CPU'.format(memory_usage, cpu_usage))

        e.add_field(name='Guilds', value=len(self.bot.guilds))
        e.add_field(name='Commands Run', value=self.bot.command_count)
        e.add_field(name='Uptime', value=self.get_bot_uptime(brief=True))

        e.set_footer(text='Made with discord.py', icon_url='http://i.imgur.com/5BFecvA.png')
        await manager.send_embed(e)
        await manager.clean_messages()


    @commands.command()
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    async def donate(self, ctx):
        """Support the continued development of Spirit!"""
        manager = MessageManager(ctx)
        e = discord.Embed(colour=constants.BLUE)

        text = ("Spirit is a work of love that has taken countless hours to develop. Your donation "
              + "will go towards server hosting costs, development tools, and if you donate "
              + "monthly, will also earn you some special privelges on the Spirit Discord server!\n\n"
              + "Donate once: https://www.paypal.me/spiritbot\n"
              + "Donate monthly: https://www.patreon.com/spiritbot")
        reward_1 = "- Colored name on the Spirit Discord server"
        reward_2 = ("- Patron role and colored name on the Spirit Discord server\n"
                  + "- Access to the developer blog on Patreon and the Spirit Discord server\n"
                  + "- Access to a patron only channel on the Spirit Discord server which includes sneak peeks of new features!")
        reward_3 = ("- All rewards from the previous tier\n"
                  + "- Your own personalized message built right into Spirit!")

        e.description = text
        e.add_field(name="$1/Month", value=reward_1)
        e.add_field(name="$5/Month", value=reward_2)
        e.add_field(name="$10/Month", value=reward_3)

        await manager.send_embed(e)
        await manager.clean_messages()


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
