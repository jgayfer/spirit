from datetime import datetime
import asyncio

from discord.ext import commands
import discord
import pydest

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Destiny:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def nightfall(self, ctx):
        """Display the weekly nightfall info"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        try:
            weekly = await self.destiny.api.get_public_milestones()
        except pydest.PydestException as e:
            await manager.say("Sorry, I can't seem retrieve the nightfall info right now")
            return await manager.clear()

        if weekly['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem retrieve the nightfall info right now")
            return await manager.clear()

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

        await manager.say(e, embed=True, delete=False)
        await manager.clear()
