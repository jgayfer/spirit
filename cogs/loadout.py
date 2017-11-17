from datetime import datetime
from discord.ext import commands
import discord

import pydest

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Loadout:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def loadout(self, ctx, platform=None, username=None):
        """Display a Guardian's loadout

        In order to use this command for your own Guardian, you must first register your Destiny 2
        account with the bot via the register command.

        `loadout` - Display your Guardian's loadout (preferred platform)
        \$`loadout xbox` - Display your Guardian's loadout on Xbox
        \$`loadout bnet Asal#1502` - Display Asal's Guardian's loadout on Battle.net
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await self.get_membership_details(ctx, platform, username)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        else:
            platform_id, membership_id = membership_details

        # Attempt to fetch character information from Bungie.net
        try:
            res = await self.destiny.api.get_profile(platform_id, membership_id, ['characters', 'characterEquipment', 'profiles'])
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
        e.set_author(name=char_name, icon_url=constants.PLATFORM_URLS.get(platform_id))
        e.description = char_info
        e.set_thumbnail(url=emblem_url)
        e.add_field(name='Weapons', value=weapons_info, inline=True)
        e.add_field(name='Armor', value=armor_info, inline=True)

        await manager.say(e, embed=True, delete=False)
        await manager.clear()


    async def get_membership_details(self, ctx, platform, username):
        """Get the platform_id, membership_id, and display name for a user

           Note that platform and username can be None, in which case the credentials
           for the user in the database are used"""

        # User wants stats for another Guardian
        if username:

            if platform not in constants.PLATFORMS.keys():
                return "Platform must be one of `bnet`, `xbox`, or `ps`"

            platform_id = constants.PLATFORMS.get(platform)

            # Try and fetch account data from Bungie.net
            try:
                res = await self.destiny.api.search_destiny_player(platform_id, username)
            except pydest.PydestException as e:
                return "I can't seem to connect to Bungie right now. Try again later."

            if res['ErrorCode'] != 1:
                return "I can't seem to connect to Bungie right now. Try again later."

            # Get a single membership ID for the given credentials (if one exists)
            membership_id = None
            if len(res['Response']) == 1:
                membership_id = res['Response'][0]['membershipId']
            elif len(res['Response']) > 1:
                for entry in res['Response']:
                    if username == entry['displayName']:
                        membership_id = entry['membershipId']
                        break

            if not membership_id:
                return "Sorry, I couldn't find the Guardian you're looking for."

        # User wants a loadout for their own Guardian
        else:
            info = self.bot.db.get_d2_info(ctx.author.id)
            if info:

                # If platform wasn't given, use the user's preferred platform
                if not platform:
                    platform_id = info.get('platform')

                # Otherwise, use the platform provided by the user (assuming it's valid)
                else:
                    if platform not in constants.PLATFORMS.keys():
                        return "Platform must be one of `bnet`, `xbox`, or `ps`"
                    platform_id = constants.PLATFORMS.get(platform)

                if platform_id == 4:
                    membership_id = info.get('bliz_id')
                elif platform_id == 1:
                    membership_id = info.get('xbox_id')
                elif platform_id == 2:
                    membership_id = info.get('psn_id')

                if not membership_id:
                    return "Oops, you don't have a connected account of that type."

            else:
                return ("You must first register your Destiny 2 account with the "
                      + "`{}register` command.".format(ctx.prefix))

        return platform_id, membership_id
