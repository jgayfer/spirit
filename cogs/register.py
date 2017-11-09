import pickle

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

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you")

        # Prompt user with link to authorize
        auth_url = "https://www.bungie.net/en/OAuth/Authorize?client_id={}&response_type=code&state={}"
        await manager.say(auth_url.format(self.client_id, ctx.author.id), dm=True)

        # Grab user info from the web server
        pickled_info = await self.redis.get(ctx.author.id)
        user_info = pickle.loads(pickled_info)
        bungie_id = user_info.get('membership_id')
        access_token = user_info.get('access_token')
        refresh_token = user_info.get('refresh_token')

        # Save registration info to database
        self.bot.db.update_registration(bungie_id, access_token, refresh_token, ctx.author.id)
