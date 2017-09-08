from datetime import datetime

import discord
from discord.ext import commands
import pytz

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class General:

    def __init__(self, bot):
        self.bot = bot


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
