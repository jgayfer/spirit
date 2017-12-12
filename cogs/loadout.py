from datetime import datetime
from discord.ext import commands
import discord

import pydest

from cogs.utils.message_manager import MessageManager
from cogs.utils import constants, helpers


class Loadout:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def loadout(self, ctx, username=None, platform=None):
        """Display a Guardian's loadout

        In order to use this command for your own Guardian, you must first register your Destiny 2
        account with the bot via the register command.

        `loadout` - Display your Guardian's loadout (preferred platform)
        \$`loadout Asal#1502 bnet` - Display Asal's Guardian's loadout on Battle.net
        \$`loadout @user` - Display a registered user's Guardian (preferred platform)
        \$`loadout @user bnet` - Display a registered user's Guardian on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, _ = membership_details

        # Attempt to fetch character information from Bungie.net
        try:
            res = await self.bot.destiny.api.get_profile(platform_id, membership_id, ['characters', 'characterEquipment', 'profiles'])
        except pydest.PydestException as e:
            await manager.send_message("Sorry, I can't seem to retrieve that Guardian right now.")
            return await manager.clean_messages()

        if res['ErrorCode'] != 1:
            await manager.send_message("Sorry, I can't seem to retrieve that Guardian right now.")
            return await manager.clean_messages()

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

        role_dict = await self.bot.destiny.decode_hash(last_played_char['classHash'], 'DestinyClassDefinition')
        role = role_dict['displayProperties']['name']

        gender_dict = await self.bot.destiny.decode_hash(last_played_char['genderHash'], 'DestinyGenderDefinition')
        gender = gender_dict['displayProperties']['name']

        race_dict = await self.bot.destiny.decode_hash(last_played_char['raceHash'], 'DestinyRaceDefinition')
        race= race_dict['displayProperties']['name']

        char_name = res['Response']['profile']['data']['userInfo']['displayName']
        level = last_played_char['levelProgression']['level']
        light = last_played_char['light']
        emblem_url = 'https://www.bungie.net' + last_played_char['emblemPath']

        stats = []
        for stat_hash in ('2996146975', '392767087', '1943323491'):
            stat_dict = await self.bot.destiny.decode_hash(stat_hash, 'DestinyStatDefinition')
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

            item_dict = await self.bot.destiny.decode_hash(item['itemHash'], 'DestinyInventoryItemDefinition')
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

        await manager.send_embed(e)
        await manager.clean_messages()
