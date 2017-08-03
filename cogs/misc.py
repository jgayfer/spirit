import discord
from discord.ext import commands

from cogs.utils.messages import MessageManager


class Misc:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def feedback(self, ctx, *args):
        """Allow user to send feedback to the bot's developer"""
        user = ctx.message.author
        manager = MessageManager(self.bot, user, ctx.message.channel, [ctx.message])

        if len(args) == 0:
            await manager.say("You forgot to include your feedback!")
            return await manager.clear()

        feedback = ""
        for word in args:
            feedback += "{} ".format(word)

        # Send user feedback to Asal, the bot's devloper
        asal = await self.bot.get_user_info("118926942404608003")
        await self.bot.send_message(asal, "Feedback from {}:\n---\n{}".format(user.mention, feedback))

        await manager.say("Your feedback has been sent to the devloper. Thank you for your input!")
        await manager.clear()
