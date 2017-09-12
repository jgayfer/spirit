import asyncio

import discord

from db.dbase import DBase
from cogs.utils import constants


def delete_all(message):
    """Helper function used to delete messages"""
    return True;


class MessageManager:

    def __init__(self, bot, user, channel, messages=None):
        self.bot = bot
        self.user = user
        self.channel = channel
        if messages:
            self.messages = messages
        else:
            self.messages = []


    async def say_and_wait(self, content, dm=False, mention=True):
        """Send a message and wait for user's response"""
        channel = self.channel
        if dm:
            channel =  self.user.dm_channel
            if not channel:
                channel = await self.user.create_dm()

        def check_res(m):
            return m.author == self.user and m.channel == channel

        if mention and not isinstance(channel, discord.abc.PrivateChannel):
            msg = await channel.send("{}: {}".format(self.user.mention, content))
        else:
            msg = await channel.send("{}".format(content))

        self.messages.append(msg)

        try:
            res = await self.bot.wait_for('message', check=check_res, timeout=60)
        except asyncio.TimeoutError as e:
            if mention and not isinstance(channel, discord.abc.PrivateChannel):
                msg = await channel.send("{}: I'm not sure where you went. We can try this again later.".format(self.user.mention))
            else:
                msg = await channel.send("I'm not sure where you went. We can try this again later.")
            self.messages.append(msg)
            await self.clear()
            return False

        # If the user responds with a command, we'll need to stop executing and clean up
        if res.content.startswith('!'):
            await self.clear()
            return False
        else:
            self.messages.append(res)
            return res


    async def say(self, content, embed=False, dm=False, delete=True, mention=True):
        """Send a message"""
        channel = self.channel
        if dm:
            channel =  self.user.dm_channel
            if not channel:
                channel = await self.user.create_dm()

        msg = None
        if embed:
            msg = await channel.send(embed=content)
        else:
            if mention and not isinstance(channel, discord.abc.PrivateChannel):
                msg = await channel.send("{}: {}".format(self.user.mention, content))
            else:
                msg = await channel.send("{}".format(content))

        if delete:
            self.messages.append(msg)


    async def clear(self):
        """Delete messages marked for deletion"""
        def check(message):
            if (message.author in (self.user, self.bot.user)
                and message.id in [m.id for m in self.messages]):
                return True

        if not isinstance(self.channel, discord.abc.PrivateChannel):
            with DBase() as db:
                cleanup = db.get_cleanup(self.channel.guild.id)
                if cleanup:
                    await asyncio.sleep(constants.SPAM_DELAY)
                    await self.channel.purge(limit=999, check=check)
