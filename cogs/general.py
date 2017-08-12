from datetime import datetime

import discord
from discord.ext import commands

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class General:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def countdown(self, ctx):
        """Show time until upcoming Destiny 2 releases"""
        manager = MessageManager(self.bot, ctx.message.author, ctx.message.channel, [ctx.message])

        text = ""
        for name, date in constants.RELEASE_DATES:
            diff = date - datetime.now()
            if diff.days == -1:
                text += "{}: Today!\n".format(name)
            elif diff.days == 0:
                text += "{}: Tomorrow!\n".format(name)
            elif diff.days > 1:
                text += "{}: {} days\n".format(name, diff.days)

        countdown = discord.Embed(title="Destiny 2 Countdown", color=constants.BLUE)
        countdown.description = text
        await manager.say(countdown, embed=True, delete=False)
        await manager.clear()


    @commands.command(pass_context=True)
    async def feedback(self, ctx, *message):
        """
        Send a message to the bot's developer

        Ex. '!feedback Your bot is awesome!'
        """
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, [ctx.message])

        if len(message) == 0:
            await manager.say("You forgot to include your feedback!")
            return await manager.clear()

        feedback = ""
        for word in message:
            feedback += "{} ".format(word)

        # Send user feedback to Asal, the bot's devloper
        asal = await self.bot.get_user_info("118926942404608003")
        await self.bot.send_message(asal, "Feedback from {}:\n---\n{}".format(user.mention, feedback))

        await manager.say("Your feedback has been sent to the devloper. Thank you for your input!")
        await manager.clear()
