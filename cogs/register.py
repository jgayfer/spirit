import pickle
import asyncio

from discord.ext import commands
import discord
import aioredis

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Register:

    def __init__(self, bot, destiny, client_id):
        self.bot = bot
        self.destiny = destiny
        self.client_id = client_id


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def register(self, ctx):
        """Register your Destiny 2 account with the bot

        This command will let the bot know which Destiny 2 profile to associate with your Discord
        profile. Registering is a prerequisite to using any commands that require knowledge of your
        Destiny 2 profile.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you")

        # Prompt user with link to authorize
        auth_url = "https://www.bungie.net/en/OAuth/Authorize?client_id={}&response_type=code&state={}"
        await manager.say(auth_url.format(self.client_id, ctx.author.id), dm=True)

        # Wait for user info from the web server via Redis
        res = await self.redis.subscribe(ctx.author.id)
        tsk = asyncio.ensure_future(self.wait_for_msg(res[0]))
        try:
            user_info = await asyncio.wait_for(tsk, timeout=30)
        except asyncio.TimeoutError:
            await manager.say("Timeout")
            return await manager.clear()

        # Parse response
        bungie_id = user_info.get('membership_id')
        access_token = user_info.get('access_token')
        refresh_token = user_info.get('refresh_token')

        # Save registration info to database
        self.bot.db.update_registration(bungie_id, access_token, refresh_token, ctx.author.id)


    async def on_connect(self):
        """Initialize Redis connection when bot loads"""
        self.redis = await aioredis.create_redis(('localhost', 6379))


    async def wait_for_msg(self, ch):
        """Wait for a message on the specified Redis channel"""
        while (await ch.wait_message()):
            pickled_msg = await ch.get()
            return pickle.loads(pickled_msg)
