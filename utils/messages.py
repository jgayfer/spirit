import asyncio

import discord


def delete_all(message):
    """Helper function used to delete messages"""
    return True;


async def clear_messages(bot, messages):
    """Delete messages after a delay"""
    await asyncio.sleep(4)
    for message in messages:
        await bot.delete_message(message)
