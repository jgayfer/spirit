import asyncio
import json
from datetime import datetime

from discord.ext import commands
import discord
import pydest
import pytz

from db.dbase import DBase
from cogs.utils.messages import delete_all, MessageManager
from cogs.utils import constants


class Destiny:

    def __init__(self, bot):
        self.bot = bot
        with open('credentials.json') as f:
            api_key = json.load(f)['d2-api-key']
        self.destiny = pydest.Pydest(api_key)


    @commands.command()
    async def countdown(self, ctx):
        """Show time until upcoming Destiny 2 releases"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
        pst_now = datetime.now(tz=pytz.timezone('US/Pacific'))
        text = ""

        for name, date in constants.RELEASE_DATES:
            diff = date - pst_now
            days = diff.days + 1
            if days == 0:
                text += "{}: Today!\n".format(name)
            elif days == 1:
                text += "{}: Tomorrow!\n".format(name)
            elif days > 1:
                text += "{}: {} days\n".format(name, days)

        countdown = discord.Embed(title="Destiny 2 Countdown", color=constants.BLUE)
        countdown.description = text
        await manager.say(countdown, embed=True, delete=False)
        await manager.clear()


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


    @commands.command()
    async def nightfall(self, ctx):
        """Display the currently available nightfalls"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        weekly = await self.destiny.api.get_public_milestones()
        nightfall_hash = weekly['Response']['2171429505']['availableQuests'][0]['activity']['activityHash']
        nightfall = await self.destiny.decode_hash(nightfall_hash, 'DestinyActivityDefinition')

        challenges = ""
        for entry in nightfall['challenges']:
            challenge = await self.destiny.decode_hash(entry['objectiveHash'], 'DestinyObjectiveDefinition')
            challenge_name = challenge['displayProperties']['name']
            challenge_description = challenge['displayProperties']['description']
            challenges += "**{}** - {}\n".format(challenge_name, challenge_description)

        modifiers = ""
        for entry in weekly['Response']['2171429505']['availableQuests'][0]['activity']['modifierHashes']:
            modifier = await self.destiny.decode_hash(entry, 'DestinyActivityModifierDefinition')
            modifier_name = modifier['displayProperties']['name']
            modifier_description = modifier['displayProperties']['description']
            modifiers += "**{}** - {}\n".format(modifier_name, modifier_description)

        e = discord.Embed(title='{}'.format(nightfall['displayProperties']['name']), colour=constants.BLUE)
        e.description = "*{}*".format(nightfall['displayProperties']['description'])
        e.set_thumbnail(url=('https://www.bungie.net' + nightfall['displayProperties']['icon']))
        e.add_field(name='Challenges', value=challenges)
        e.add_field(name='Modifiers', value=modifiers)
        e.timestamp = datetime.now(tz=pytz.timezone('US/Pacific'))

        await manager.say(e, embed=True)
        await manager.clear()
