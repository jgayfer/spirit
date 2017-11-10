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
            await manager.say("Registration instructions have been messaged to you.")

        template = "https://www.bungie.net/en/OAuth/Authorize?client_id={}&response_type=code&state={}"
        auth_url = template.format(self.client_id, ctx.author.id)

        e = discord.Embed(colour=constants.BLUE)
        e.title = "Click here to register"
        e.url = auth_url
        e.description = ("Click the above link to register your Bungie.net account with Spirit. "
                       + "Registering will allow Spirit to access your connected Destiny "
                       + "2 accounts.")
        await manager.say(e, embed=True, dm=True)

        # Wait for user info from the web server via Redis
        res = await self.redis.subscribe(ctx.author.id)
        tsk = asyncio.ensure_future(self.wait_for_msg(res[0]))
        try:
            user_info = await asyncio.wait_for(tsk, timeout=30)
        except asyncio.TimeoutError:
            await manager.say("Timeout")
            return await manager.clear()
        await ctx.channel.trigger_typing()

        bungie_id = user_info.get('membership_id')
        access_token = user_info.get('access_token')
        refresh_token = user_info.get('refresh_token')

        self.bot.db.update_registration(bungie_id, access_token, refresh_token, ctx.author.id)

        try:
            res = await self.destiny.api.get_bungie_net_user_by_id(bungie_id)
        except:
            await manager.say("I can't seem to connect to Bungie right now. Try again later.", dm=True)
            return await manager.clear()

        if res['ErrorCode'] != 1:
            await manager.say("Oops, something went wrong during registration. Please try again.")
            return await manager.clear()

        res_content = res['Response']
        bungie_name = res_content['displayName']
        bliz_name = res_content['blizzardDisplayName'] if 'blizzardDisplayName' in res_content else None
        xbox_name = res_content['xboxDisplayName'] if 'xboxDisplayName' in res_content else None
        psn_name = res_content['psnDisplayName'] if 'psnDisplayName' in res_content else None

        self.bot.db.update_display_names(ctx.author.id, bungie_name, bliz_name, xbox_name, psn_name)

        bliz_id = None
        xbox_id = None
        psn_id = None

        if bliz_name:
            try:
                res = await self.destiny.api.search_destiny_player(4, bliz_name)
            except pydest.PydestException as e:
                await manager.say("I can't seem to connect to Bungie right now. Try again later.", dm=True)
                return await manager.clear()
            bliz_id = res['Response'][0]['membershipId']

        if xbox_name:
            try:
                res = await self.destiny.api.search_destiny_player(1, xbox_name)
            except pydest.PydestException as e:
                await manager.say("I can't seem to connect to Bungie right now. Try again later.", dm=True)
                return await manager.clear()
            xbox_id = res['Response'][0]['membershipId']

        if psn_name:
            try:
                res = await self.destiny.api.search_destiny_player(4, psn_name)
            except pydest.PydestException as e:
                await manager.say("I can't seem to connect to Bungie right now. Try again later.", dm=True)
                return await manager.clear()
            psn_id = res['Response'][0]['membershipId']

        self.bot.db.update_membership_ids(ctx.author.id, bliz_id, xbox_id, psn_id)


        platform_reactions = (self.bot.get_emoji(constants.XBOX_ICON),
                              self.bot.get_emoji(constants.PS_ICON),
                              self.bot.get_emoji(constants.BNET_ICON))

        platform_msg = await manager.say("Registration complete!\n\nPlease select your preferred platform.")

        func = self.add_reactions(platform_msg, platform_reactions)
        self.bot.loop.create_task(func)

        def check_reaction(reaction, user):
            if reaction.message.id == platform_msg.id and user == ctx.author:
                for emoji in platform_reactions:
                    if reaction.emoji == emoji:
                        return True

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
        except asyncio.TimeoutError:
            await manager.say("I'm not sure where you went. We can try this again later.", dm=True)
            return await manager.clear()
        platform = constants.PLATFORMS.get(reaction.emoji.name)

        self.bot.db.update_platform(ctx.author.id, platform)
        await manager.say("Your preferred platform has been updated!")


    async def on_connect(self):
        """Initialize Redis connection when bot loads"""
        self.redis = await aioredis.create_redis(('localhost', 6379))


    async def add_reactions(self, message, reactions):
        """Add platform reactions to message"""
        for icon in reactions:
            await message.add_reaction(icon)


    async def wait_for_msg(self, ch):
        """Wait for a message on the specified Redis channel"""
        while (await ch.wait_message()):
            pickled_msg = await ch.get()
            return pickle.loads(pickled_msg)
