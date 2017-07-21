import asyncio
import discord

# Helper function used to delete messages
def delete_all(message):
    return True;

async def clear_messages(bot, messages):
    await asyncio.sleep(4)
    for message in messages:
        await bot.delete_message(message)
