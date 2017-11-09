import pickle

from discord.ext import commands
import discord
import aioredis

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Register:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    async def on_ready(self):
        """Initialize Redis connection when bot loads"""
        self.redis = await aioredis.create_redis(('localhost', 6379))


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def register(self, ctx):
        """Register your Destiny 2 account with the bot

        This command will let the bot know which Destiny 2 profile to associate with your Discord
        profile. Registering is a prerequisite to using any commands that require knowledge of your
        Destiny 2 profile.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        await manager.say("https://www.bungie.net/en/OAuth/Authorize?client_id=21849&response_type=code&state={}".format(ctx.author.id))

        # Wait for message from the web server
        pickled_info = await self.redis.get(ctx.author.id)
        user_info = pickle.loads(pickled_info)
