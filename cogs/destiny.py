import asyncio
import json

from discord.ext import commands
import discord
import pydest

from db.dbase import DBase
from cogs.utils.messages import delete_all, MessageManager


class Destiny:

    def __init__(self, bot):
        self.bot = bot
        with open('credentials.json') as f:
            api_key = json.load(f)['d2-api-key']
        self.destiny = pydest.Pydest(api_key)


    @commands.command()
    async def register(self, ctx):
        """Register your Destiny 2 account with the bot"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you")

        await manager.say("Registering your Destiny 2 account with me will allow "
                        + "you to invoke commands that use information from your "
                        + "public Destiny 2 profile.", dm=True)

        platform = None
        while not platform:
            res = await manager.say_and_wait("Enter your platform (**xbox** or **playstation**):", dm=True)
            platforms = {'PC': 4, 'XBOX': 1, 'PLAYSTATION': 2}
            platform = platforms.get(res.content.upper())
            if not platform:
                await manager.say("Invalid platform. Try again.", dm=True)

        act = await manager.say_and_wait("Enter your exact **account name**:", dm=True)
        res = await self.destiny.api.search_destiny_player(platform, act.content)

        if res['ErrorCode'] == 1 and len(res['Response']) > 0:
            act_exists = True
            membership_id = res['Response'][0]['membershipId']
        else:
            act_exists = False

        if not act_exists:
            await manager.say("An account with that name doesn't seem to exist.", dm=True)
        else:
            await manager.say("Account successfully registered!", dm=True)
            with DBase() as db:
                db.add_user(str(ctx.author))
                db.update_registration(platform, membership_id, str(ctx.author))

        return await manager.clear()
