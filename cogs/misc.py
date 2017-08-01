import discord
from discord.ext import commands

from cogs.utils.messages import MessageManager


class Misc:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def feedback(self, ctx):
        """Allow user to send feedback to the bot's developer"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, ctx.message)

        res = await manager.say_and_wait("Enter the feedback you would like to send to the developer")
        if not res:
            return
        feedback = res.content
        await manager.say("Feedback received! Thank you for your input.")

        # Send user feedback to Asal, the bot's devloper
        asal = await self.bot.get_user_info("118926942404608003")
        await self.bot.send_message(asal, "Feedback from {}:\n{}".format(user.mention, feedback))

        await manager.clear()
