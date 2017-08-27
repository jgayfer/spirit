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
            self.api_key = json.load(f)['d2-api-key']


    @commands.command()
    async def register(self, ctx):
        """Register your Destiny 2 account with the bot"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you")

        platform = None
        while not platform:
            res = await manager.say_and_wait("Enter your platform (pc, xbox, or ps):", dm=True)
            platforms = {'PC': 4, 'XBOX': 1, 'PS': 2}
            platform = platforms.get(res.content.upper())
            if not platform:
                await manager.say("Invalid platform.", dm=True)

        act = await manager.say_and_wait("Enter your exact account name:", dm=True)

        with pydest.API(self.api_key) as destiny:
            res = await destiny.search_destiny_player(platform, act.content)

        act_exists = False
        if res['ErrorCode'] == 1:
            act_exists = True
            membership_id = res['Response'][0]['membershipId']

        if not act_exists:
            await manager.say("An account with that name doesn't seem to exist.", dm=True)
        else:
            await manager.say("Account successfully registered!")
            with DBase() as db:
                db.add_user(str(ctx.author))
                db.update_registration(platform, membership_id, str(ctx.author))

        return await manager.clear()
