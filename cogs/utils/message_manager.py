import asyncio

import discord

from cogs.utils.constants import CLEANUP_DELAY
from cogs.utils.checks import is_private_channel
from db.query_wrappers import cleanup_is_enabled


class MessageManager:

    def __init__(self, ctx):
        self.ctx = ctx
        self.messages_to_clean = [ctx.message]


    def add_messages_to_clean(self, messages):
        """Add a list of messages to be cleaned"""
        self.messages_to_clean.extend(messages)


    async def clean_messages(self):
        """Delete messages marked for cleaning"""
        def message_needs_cleaning(message):
            if message.id in [m.id for m in self.messages_to_clean]:
                return True

        if not is_private_channel(self.ctx.channel) and cleanup_is_enabled(self.ctx):
            await asyncio.sleep(CLEANUP_DELAY)
            await self.ctx.channel.purge(limit=999, check=message_needs_cleaning)


    async def get_next_message(self):
        """Get the next message sent by the user in ctx.channel
           Raises: asyncio.TimeoutError
        """
        def is_channel_message(message):
            return message.author == self.ctx.author and message.channel == self.ctx.channel

        return await self.ctx.bot.wait_for('message', check=is_channel_message, timeout=120)


    async def get_next_private_message(self):
        """Get the next private message sent by the user
           Raises: asyncio.TimeoutError
        """
        def is_private_message(message):
            return message.author.dm_channel == self.ctx.author.dm_channel

        return await self.ctx.bot.wait_for('message', check=is_private_message, timeout=120)


    async def send_embed(self, embed):
        """Send an embed message to the user on ctx.channel"""
        if is_private_channel(self.ctx.channel):
            msg = await self.send_private_embed(embed)
        else:
            msg = await self.ctx.channel.send(embed=embed)
        return msg


    async def send_message(self, message_text):
        """Send a message to the user on ctx.channel"""
        if is_private_channel(self.ctx.channel):
            msg = await self.send_private_message("{}".format(message_text))
        else:
            msg = await self.ctx.channel.send("{}: {}".format(self.ctx.author.mention, message_text))
            self.messages_to_clean.append(msg)
        return msg


    async def send_private_embed(self, embed):
        """Send an private embed message to the user"""
        return await self.ctx.author.send(embed=embed)


    async def send_private_message(self, message_text):
        """Send a private message to the user"""
        return await self.ctx.author.send("{}".format(message_text))
