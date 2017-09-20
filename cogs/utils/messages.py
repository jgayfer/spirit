import asyncio

import discord

from db.dbase import DBase
from cogs.utils import constants


def delete_all(message):
    """Helper function used to delete messages"""
    return True;


class MessageManager:

    def __init__(self, bot, user, channel, prefix, messages=None):
        self.bot = bot
        self.user = user
        self.channel = channel
        self.prefix = prefix
        if messages:
            self.messages = messages
        else:
            self.messages = []


    async def say_and_wait(self, content, dm=False, mention=True):
        """Send a message and wait for user's response"""
        def check_res(m):
            return m.author == self.user and m.channel == self.channel
        def check_res_dm(m):
            return m.author == self.user and m.channel == self.user.dm_channel

        if dm:
            try:
                await self.user.send(content)
            except:
                if mention and not isinstance(self.channel, discord.abc.PrivateChannel):
                    await self.channel.send("{}: Oops, it looks like I'm not allowed to send you a private message".format(self.user.mention))
                else:
                    await self.channel.send("Oops, it looks like I'm not allowed to send you a private message".format(self.user.mention))
                return None
            try:
                res = await self.bot.wait_for('message', check=check_res_dm, timeout=120)
            except asyncio.TimeoutError as e:
                await self.user.send("I'm not sure where you went. We can try this again later.")
                return None

        else:
            if mention and not isinstance(self.channel, discord.abc.PrivateChannel):
                msg = await self.channel.send("{}: {}".format(self.user.mention, content))
            else:
                msg = await self.channel.send(content)
            self.messages.append(msg)
            try:
                res = await self.bot.wait_for('message', check=check_res, timeout=120)
            except asyncio.TimeoutError as e:
                if mention and not isinstance(self.channel, discord.abc.PrivateChannel):
                    msg = await self.channel.send("{}: I'm not sure where you went. We can try this again later.".format(self.user.mention))
                else:
                    msg = await self.channel.send("I'm not sure where you went. We can try this again later.")
                self.messages.append(msg)
                await self.clear()
                return None

        # If the user responds with a command, we'll need to stop executing and clean up
        if res.content.startswith(self.prefix) or res.content.startswith('!') or res.content.startswith(self.bot.user.mention):
            await self.clear()
            return False
        else:
            self.messages.append(res)
            return res


    async def say(self, content, embed=False, dm=False, delete=True, mention=True):
        """Send a message to the user. Return True on success."""
        if dm:
            try:
                if embed:
                    await self.user.send(embed=content)
                else:
                    await self.user.send(content)
            except:
                if mention and not isinstance(self.channel, discord.abc.PrivateChannel):
                    await self.channel.send("{}: Oops, it looks like I'm not allowed to send you a private message".format(self.user.mention))
                else:
                    await self.channel.send("Oops, it looks like I'm not allowed to send you a private message".format(self.user.mention))
            else:
                return True

        else:
            if embed:
                msg = await self.channel.send(embed=content)
            else:
                if mention and not isinstance(self.channel, discord.abc.PrivateChannel):
                    msg = await self.channel.send("{}: {}".format(self.user.mention, content))
                else:
                    msg = await self.channel.send(content)
            if delete:
                self.messages.append(msg)
            return True


    async def clear(self):
        """Delete messages marked for deletion"""
        def check(message):
            if (message.author in (self.user, self.bot.user)
                and message.id in [m.id for m in self.messages]):
                return True

        if not isinstance(self.channel, discord.abc.PrivateChannel):
            with DBase() as db:
                rows = db.get_cleanup(self.channel.guild.id)

            if len(rows) and len(rows[0]):
                cleanup = rows[0][0]
            else:
                raise ValueError("Could not retrieve 'cleanup' from database")

            if cleanup:
                await asyncio.sleep(constants.SPAM_DELAY)
                await self.channel.purge(limit=999, check=check)
