import asyncio
import json
from datetime import datetime

from discord.ext import commands
import discord
import pydest
import pytz

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Destiny:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


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
        """Register your Destiny 2 account with the bot

        This command will let the bot know which Destiny 2 profile to associate with your Discord
        profile. Registering is a prerequisite to using any commands that require knowledge of your
        public Destiny 2 profile.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])

        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await manager.say("Registration instructions have been messaged to you")

        msg_sent = await manager.say("Registering your Destiny 2 account with me will allow "
                                   + "you to invoke commands that use information from your "
                                   + "public Destiny 2 profile.", dm=True)
        if not msg_sent:
            return await manager.clear()

        platform = None
        while not platform:
            res = await manager.say_and_wait("Enter your platform (**xbox** or **playstation**):", dm=True)
            if not res:
                return await manager.clear()
            platform = constants.PLATFORMS.get(res.content.upper())
            if not platform:
                await manager.say("Invalid platform. Try again.", dm=True)

        act = await manager.say_and_wait("Enter your exact **account name**:", dm=True)
        if not act:
            return await manager.clear()

        try:
            res = await self.destiny.api.search_destiny_player(platform, act.content)
        except ValueError as e:
            await manager.say("Invalid account name. If this seems wrong, please contact the developer.")
            return await manager.clear()
        except pydest.PydestException as e:
            await manager.say("I can seem to connect to Bungie right now. Try again later.")
            return await manager.clear()

        act_exists = False
        if res['ErrorCode'] == 1 and len(res['Response']) == 1:
            act_exists = True
            membership_id = res['Response'][0]['membershipId']
        elif res['ErrorCode'] == 1 and len(res['Response']) > 1:
            for entry in res['Response']:
                if act.content == entry['displayName']:
                    act_exists = True
                    membership_id = entry['membershipId']
                    break

        if not act_exists:
            await manager.say("An account with that name doesn't seem to exist.", dm=True)
        else:
            await manager.say("Account successfully registered!", dm=True)
            self.bot.db.add_user(ctx.author.id)
            self.bot.db.update_registration(platform, membership_id, ctx.author.id)

        return await manager.clear()


    @commands.command()
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


    @commands.command()
    async def loadout(self, ctx):
        """Display your last played character's loadout

        In order to use this command, you must first register your Destiny 2 account with the bot
        via the register command.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Check if user has registered their D2 account with the bot
        info = self.bot.db.get_d2_info(ctx.author.id)
        if info:
            platform = info.get('platform')
            membership_id = info.get('membership_id')
        else:
            await manager.say("You must first register your Destiny 2 account with the "
                            + "`{}register` command.".format(ctx.prefix))
            return await manager.clear()

        try:
            res = await self.destiny.api.get_profile(platform, membership_id, ['characters', 'characterEquipment', 'profiles'])
        except pydest.PydestException as e:
            await manager.say("Sorry, I can't seem to retrieve your Guardian right now.")
            return await manager.clear()
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your Guardian right now.")
            return await manager.clear()

        # Determine which character was last played
        chars_last_played = []
        for character_id in res['Response']['characters']['data']:
            last_played_str = res['Response']['characters']['data'][character_id]['dateLastPlayed']
            date_format = '%Y-%m-%dT%H:%M:%SZ'
            last_played = datetime.strptime(last_played_str, date_format)
            chars_last_played.append((character_id, last_played))
        last_played_char_id = max(chars_last_played, key = lambda t: t[1])[0]
        last_played_char = res['Response']['characters']['data'].get(last_played_char_id)

        #######################################
        # ------ Decode Character Info ------ #
        #######################################

        role_dict = await self.destiny.decode_hash(last_played_char['classHash'], 'DestinyClassDefinition')
        role = role_dict['displayProperties']['name']

        gender_dict = await self.destiny.decode_hash(last_played_char['genderHash'], 'DestinyGenderDefinition')
        gender = gender_dict['displayProperties']['name']

        race_dict = await self.destiny.decode_hash(last_played_char['raceHash'], 'DestinyRaceDefinition')
        race= race_dict['displayProperties']['name']

        char_name = res['Response']['profile']['data']['userInfo']['displayName']
        level = last_played_char['levelProgression']['level']
        light = last_played_char['light']
        emblem_url = 'https://www.bungie.net' + last_played_char['emblemPath']

        stats = []
        for stat_hash in ('2996146975', '392767087', '1943323491'):
            stat_dict = await self.destiny.decode_hash(stat_hash, 'DestinyStatDefinition')
            stat_name = stat_dict['displayProperties']['name']
            if stat_hash in last_played_char['stats'].keys():
                stats.append((stat_name, last_played_char['stats'].get(stat_hash)))
            else:
                stats.append((stat_name, 0))

        #######################################
        # ------ Decode Equipment Info ------ #
        #######################################

        weapons = [['Kinetic', '-'], ['Energy', '-'], ['Power', '-']]
        weapons_index = 0

        armor = [['Helmet', '-'], ['Gauntlets', '-'], ['Chest', '-'], ['Legs', '-'], ['Class Item', '-']]
        armor_index = 0

        equipped_items = res['Response']['characterEquipment']['data'][last_played_char_id]['items']
        for item in equipped_items:

            item_dict = await self.destiny.decode_hash(item['itemHash'], 'DestinyInventoryItemDefinition')
            item_name = "{}".format(item_dict['displayProperties']['name'])

            if weapons_index < 3:
                weapons[weapons_index][1] = item_name
                weapons_index += 1

            elif armor_index < 5:
                armor[armor_index][1] = item_name
                armor_index += 1

        #################################
        # ------ Formulate Embed ------ #
        #################################

        char_info = "Level {} {} {} {}  |\N{SMALL BLUE DIAMOND}{}\n".format(level, race, gender, role, light)
        char_info += "{} {}  • ".format(stats[0][1], stats[0][0])
        char_info += "{} {}  • ".format(stats[1][1], stats[1][0])
        char_info += "{} {}".format(stats[2][1], stats[2][0])

        weapons_info = ""
        for weapon in weapons:
            weapons_info += '**{}:** {}  \n'.format(weapon[0], weapon[1])

        armor_info = ""
        for item in armor:
            armor_info += '**{}:** {}\n'.format(item[0], item[1])

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name=char_name, icon_url=constants.PLATFORM_URLS.get(platform))
        e.description = char_info
        e.set_thumbnail(url=emblem_url)
        e.add_field(name='Weapons', value=weapons_info, inline=True)
        e.add_field(name='Armor', value=armor_info, inline=True)

        await manager.say(e, embed=True, delete=False)
        await manager.clear()
