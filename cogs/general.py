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
            if diff.days == -1:
                text += "{}: Today!\n".format(name)
            elif diff.days == 0:
                text += "{}: Tomorrow!\n".format(name)
            elif diff.days > 1:
                text += "{}: {} days\n".format(name, diff.days + 1)

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

        # Send user feedback to Asal, the bot's devloper
        asal = await self.bot.get_user_info("118926942404608003")
        await asal.send("Feedback from {} ({}):\n---\n{}".format(ctx.author.name, ctx.author.id, feedback))
        await manager.say("Your feedback has been sent to the devloper. Thank you for your input!")
        await manager.clear()


    async def on_guild_join(self, guild):
        """Send welcome message to the server owner"""
        message = ("Greetings! My name is **{}**, and my sole responsibility is to help you and "
                   "your group kick ass in Destiny 2! You're receiving this message because you "
                   "or one of your trusted associates has added me to **{}**.\n\n"
                   "**Command Prefix**\n\n"
                   "My default prefix is `!`, but you can also just mention me with `@{}`. "
                   "If another bot is already using the `!` prefix, you can choose a different prefix "
                   "for your server with `!setprefix <new_prefix>` (don't include the brackets). "
                   "If you forget your custom prefix, you can always change it back to default with "
                   "`@{} setprefix !`.\n\n"
                   "For a list of all available commands, use the `!help` command. If you want more "
                   "information on a command, use `!help <command_name>`.\n\n"
                   "If you have any questions or feedback, you can use my `!feedback` command to send "
                   "a message to my developer!"
                   ).format(self.bot.user.name, guild.name, self.bot.user.name, self.bot.user.name)
        await guild.owner.send(message)
