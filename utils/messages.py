import asyncio

import discord

import utils.constants as constants


def delete_all(message):
    """Helper function used to delete messages"""
    return True;


async def clear_messages(bot, messages):
    """Delete messages after a delay"""
    await asyncio.sleep(constants.SPAM_DELAY)
    for message in messages:
        await bot.delete_message(message)


class MessageManager:

    def __init__(self, bot, user, channel):
        self.bot = bot
        self.user = user
        self.channel = channel
        self.messages = []

    async def say_and_wait(self, content):
        """Send a message and wait for user's response"""
        msg = await self.bot.send_message(self.channel, content)
        self.messages.append(msg)
        res = await self.bot.wait_for_message(author=self.user)
        self.messages.append(res)

        if res.content.startswith('!'):
            err = await self.bot.send_message(self.channel, self.user.mention + ": You cannot do that right now")
            self.messages.append(err)
            self.say_and_wait(content)
        else:
            return res

    async def say(self, content):
        """Send a single message"""
        msg = await self.bot.send_message(self.channel, content)
        self.messages.append(msg)

    async def clear(self):
        """Delete all messages"""
        await clear_messages(self.bot, self.messages)
