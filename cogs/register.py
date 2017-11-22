import pickle
import asyncio

from discord.ext import commands
import discord
import aioredis

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Register:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def register(self, ctx):
        """Register your Destiny 2 account with the bot

        This command will let the bot know which Destiny 2 profile to associate with your Discord
        profile. Registering is a prerequisite to using any commands that require knowledge of your
        Destiny 2 profile.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        template = "https://www.bungie.net/en/OAuth/Authorize?client_id={}&response_type=code&state={}"
        auth_url = template.format(self.bot.bungie_client_id, ctx.author.id)
        bliz_name, xbox_name, psn_name, bliz_id, xbox_id, psn_id = (None,)*6

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you.")

        # Prompt user with link to Bungie.net OAuth authentication
        e = discord.Embed(colour=constants.BLUE)
        e.title = "Click Here to Register"
        e.url = auth_url
        e.description = ("Click the above link to register your Bungie.net account with Spirit. "
                       + "Registering will allow Spirit to access your connected Destiny "
                       + "2 accounts.")
        registration_msg = await manager.say(e, embed=True, dm=True)

        # Wait for user info from the web server via Redis
        res = await self.redis.subscribe(ctx.author.id)
        tsk = asyncio.ensure_future(self.wait_for_msg(res[0]))
        try:
            user_info = await asyncio.wait_for(tsk, timeout=90)
        except asyncio.TimeoutError:
            await manager.say("I'm not sure where you went. We can try this again later.", dm=True)
            await registration_msg.delete()
            return await manager.clear()
        await ctx.channel.trigger_typing()

        # Save OAuth credentials and bungie ID
        bungie_id = user_info.get('membership_id')
        access_token = user_info.get('access_token')
        refresh_token = user_info.get('refresh_token')
        self.bot.db.update_registration(bungie_id, access_token, refresh_token, ctx.author.id)

        # Fetch platform specific display names and membership IDs
        try:
            res = await self.bot.destiny.api.get_membership_data_by_id(bungie_id)
        except:
            await manager.say("I can't seem to connect to Bungie right now. Try again later.", dm=True)
            await registration_msg.delete()
            return await manager.clear()

        if res['ErrorCode'] != 1:
            await manager.say("Oops, something went wrong during registration. Please try again.", dm=True)
            await registration_msg.delete()
            return await manager.clear()

        for entry in res['Response']['destinyMemberships']:
            if entry['membershipType'] == 4:
                bliz_name = entry['displayName']
                bliz_id = entry['membershipId']
            elif entry['membershipType'] == 1:
                xbox_name = entry['displayName']
                xbox_id = entry['membershipId']
            elif entry['membershipType'] == 2:
                psn_name = entry['displayName']
                psn_id = entry['membershipId']

        bungie_name = res['Response']['bungieNetUser']['displayName']
        self.bot.db.update_display_names(ctx.author.id, bungie_name, bliz_name, xbox_name, psn_name)
        self.bot.db.update_membership_ids(ctx.author.id, bliz_id, xbox_id, psn_id)

        # Get references to platform emojis from Spirit Support server
        platform_reactions = []
        if bliz_name:
            platform_reactions.append(self.bot.get_emoji(constants.BNET_ICON))
        if xbox_name:
            platform_reactions.append(self.bot.get_emoji(constants.XBOX_ICON))
        if psn_name:
            platform_reactions.append(self.bot.get_emoji(constants.PS_ICON))

        # Display message with prompts to select a preferred platform
        e = self.registered_embed(bungie_name, bliz_name, xbox_name, psn_name)
        platform_msg = await manager.say(e, embed=True, dm=True)
        await registration_msg.delete()

        # If only one account is connected, don't display reactions
        platform_names = (bliz_name, xbox_name, psn_name)
        if self.num_non_null_entries(platform_names) == 1:
            return await manager.clear()

        func = self.add_reactions(platform_msg, platform_reactions)
        self.bot.loop.create_task(func)

        def check_reaction(reaction, user):
            if reaction.message.id == platform_msg.id and user == ctx.author:
                for emoji in platform_reactions:
                    if reaction.emoji == emoji:
                        return True

        # Wait for platform reaction from user
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
        except asyncio.TimeoutError:
            await manager.say("I'm not sure where you went. We can try this again later.", dm=True)
            return await manager.clear()

        # Save preferred platform
        platform = constants.PLATFORMS.get(reaction.emoji.name)
        self.bot.db.update_platform(ctx.author.id, platform)

        # Update message with preferred platform
        e = self.registered_embed(bungie_name, bliz_name, xbox_name, psn_name, footer=True, platform=platform)
        await platform_msg.edit(embed=e)

        return await manager.clear()


    def registered_embed(self, bungie_name, bliz_name, xbox_name, psn_name, footer=False, platform=None):
        """Create the embed that displays a user's connected accounts"""
        names = (bliz_name, xbox_name, psn_name)
        e = discord.Embed(colour=constants.BLUE)
        e.title = "Registration Complete"

        if self.num_non_null_entries(names) != 1:
            e.description = "Please select your preferred platform. You can always change it by registering again!"
        else:
            e.description = "As you have only one connected account, it has been set as your preferred platform."

        # If a preferred platform is already set, display it in bold
        if platform == 4:
            bliz_name = "**{}**".format(bliz_name)
        elif platform == 1:
            xbox_name = "**{}**".format(xbox_name)
        elif platform == 2:
            psn_name = "**{}**".format(psn_name)

        # Display connected accounts
        accounts = ""
        accounts += "{} {}\n".format(str(self.bot.get_emoji(constants.BNET_ICON)), bliz_name) if bliz_name else ''
        accounts += "{} {}\n".format(str(self.bot.get_emoji(constants.XBOX_ICON)), xbox_name) if xbox_name else ''
        accounts += "{} {}".format(str(self.bot.get_emoji(constants.PS_ICON)), psn_name) if psn_name else ''
        e.add_field(name="Connected Accounts", value=accounts)

        if footer:
            e.set_footer(text="Your preferred platform has been set!")

        return e


    def num_non_null_entries(self, list):
        """Count the number of non null entries in a list"""
        count = 0
        for entry in list:
            if entry:
                count += 1
        return count


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
