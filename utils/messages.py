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
