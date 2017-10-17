import asyncio

from discord.ext import commands
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants
from cogs.utils.paginator import Paginator


BASE_URL = 'https://www.bungie.net'

class Item:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    @commands.command()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def item(self, ctx, *, search_term):
        """Search for a Destiny 2 item"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        paginator = Paginator(self.bot, ctx)
        await ctx.channel.trigger_typing()

        try:
            res = await self.destiny.api.search_destiny_entities('DestinyInventoryItemDefinition', search_term)
        except pydest.PydestException as e:
            await manager.say("Sorry, I can't seem to search for items right now")
            return await manager.clear()

        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to search for items right now")
            return await manager.clear()

        # Check how many results were found - we need at least one
        num_results = res['Response']['results']['totalResults']
        if num_results == 0:
            await manager.say("I didn't find any items that match your search.")
            return await manager.clear()

        # Iterate through each result, and add them to the paginator if valid type
        for i, entry in enumerate(res['Response']['results']['results']):

            item_hash = entry['hash']
            item = await self.destiny.decode_hash(item_hash, 'DestinyInventoryItemDefinition')

            # If item isn't a weapon or armor piece, skip to the next one
            if item['itemType'] not in (2, 3):
                continue

            e = discord.Embed()
            e.title = item['displayProperties']['name']
            e.description = "*{}*".format(item['displayProperties']['description'])
            e.set_thumbnail(url=BASE_URL + item['displayProperties']['icon'])

            # Set embed color based on item rarity
            item_rarity = int(item['inventory']['tierType'])
            if item_rarity == 2:
                e.color = discord.Color.light_grey()
            elif item_rarity == 3:
                e.color = discord.Color.dark_green()
            elif item_rarity == 4:
                e.color = discord.Color.blue()
            elif item_rarity == 5:
                e.color = discord.Color.dark_purple()
            elif item_rarity == 6:
                e.color = discord.Color.gold()
            else:
                e.color = constants.BLUE

            # Add armor/weapon specific information
            if item['itemType'] == 3:
                e = self.embed_weapon(e, item)
                e = await self.embed_perks(e, item, 4241085061)
            else:
                e = self.embed_armor(e, item)
                e = await self.embed_perks(e, item, 2518356196)

            paginator.add_embed(e)

        if not paginator.length:
            await manager.say("I didn't find any items that match your search.")
            return await manager.clear()

        await paginator.paginate()
        await manager.clear()


    def embed_armor(self, embed, item):
        """Add armor specific attributes to item embed"""
        stats = item['stats']['stats']

        # Basic stats
        info_field = ""
        if item.get('itemTypeDisplayName'):
            slot = item['itemTypeDisplayName']
            info_field += "\n**Slot:** {}".format(slot)
        if stats.get('3897883278'):
            min_defense = stats['3897883278']['minimum']
            max_defense = stats['3897883278']['maximum']
            info_field += "\n**Defense:** {}-{}".format(min_defense, max_defense)

        if not info_field:
            info_field = "\u200B"
        embed.add_field(name="Stats", value=info_field, inline=True)

        # Mobility, Resilience, Recovery
        stats_field = ""
        if stats.get('2996146975'):
            mobility = stats['2996146975']['value']
            stats_field += "\n**Mobility:** {}".format(mobility) if mobility else "\u200B"
        if stats.get('392767087'):
            resilience = stats['392767087']['value']
            stats_field += "\n**Resilience:** {}".format(resilience) if resilience else "\u200B"
        if stats.get('1943323491'):
            recovery = stats['1943323491']['value']
            stats_field += "\n**Recovery:** {}".format(recovery) if recovery else "\u200B"

        if not stats_field:
            stats_field = "\u200B"
        embed.add_field(name="\u200B", value=stats_field, inline=True)

        return embed


    def embed_weapon(self, embed, item):
        """Add weapon specific attributes to item embed"""
        damage_type = item['defaultDamageType']
        if damage_type == 2:
            damage_emoji = self.bot.get_emoji(constants.ARC_ICON)
        elif damage_type == 3:
            damage_emoji = self.bot.get_emoji(constants.SOLAR_ICON)
        elif damage_type == 4:
            damage_emoji = self.bot.get_emoji(constants.VOID_ICON)
        else:
            damage_emoji = None
        embed.title += str(damage_emoji) if damage_emoji else ""

        stats = item['stats']['stats']

        # Basic info field
        info_field = ""
        if item.get('itemTypeDisplayName'):
            wep_type = item['itemTypeDisplayName']
            info_field += "\n**Type:** {}".format(wep_type)
        if stats.get('1480404414'):
            min_attack = stats['1480404414']['minimum']
            max_attack = stats['1480404414']['maximum']
            info_field += "\n**Attack:** {}-{}".format(min_attack, max_attack)
        if stats.get('3871231066'):
            magazine = stats['3871231066']['value']
            info_field += "\n**Magazine:** {}".format(magazine)
        if stats.get('4284893193'):
            rpm = stats['4284893193']['value']
            info_field += "\n**RPM:** {}".format(rpm)

        if not info_field:
            info_field = "\u200B"
        embed.add_field(name="Stats", value=info_field, inline=True)

        # Stats field
        stats_field = ""
        if stats.get('4043523819'):
            impact = stats['4043523819']['value']
            stats_field += "\n**Impact:** {}".format(impact)
        if stats.get('1240592695'):
            wep_range = stats['1240592695']['value']
            stats_field += "\n**Range:** {}".format(wep_range)
        if stats.get('155624089'):
            stability = stats['155624089']['value']
            stats_field += "\n**Stability:** {}".format(stability)
        if stats.get('4188031367'):
            reload_speed = stats['4188031367']['value']
            stats_field += "\n**Reload Speed:** {}".format(reload_speed)
        if stats.get('943549884'):
            handling = stats['943549884']['value']
            stats_field += "\n**Handling:** {}".format(handling)

        if not stats_field:
            stats_field = "\u200B"
        embed.add_field(name="\u200B", value=stats_field, inline=True)

        return embed


    async def embed_perks(self, embed, item, perk_hash):
        """Add perks to item embed object"""
        if not item.get('sockets'):
            return embed

        # Get indexes of perks
        perk_indexes = []
        socket_categories = item['sockets']['socketCategories']
        for category in socket_categories:
            if category['socketCategoryHash'] == perk_hash:
                perk_indexes = category['socketIndexes']
                break

        # Decode perk info and add to embed
        perks_field = ""
        for index in perk_indexes:
            perk_text = await self.format_perk(item, index)
            perks_field += "\n{}".format(perk_text) if perk_text else "\u200B"
        if perks_field:
            embed.add_field(name="Perks", value=perks_field)

        return embed


    async def format_perk(self, item, index):
        """Formulate a textual representation of a perk and it's options (if it has them)"""
        perk_options = item['sockets']['socketEntries'][index]['reusablePlugItems']

        # Don't display perks that have multiple options (for now)
        if len(perk_options) > 1:
            return None
        else:
            return await self.decode_perk(perk_options[0]['plugItemHash'])


    async def decode_perk(self, perk_hash):
        """Decode a single perk"""
        perk = await self.destiny.decode_hash(perk_hash, 'DestinyInventoryItemDefinition')
        name = perk['displayProperties']['name']
        split = perk['displayProperties']['description'].split('\n')

        if split[0].isupper() and len(split) > 1:
            description = split[1].rstrip('\n')
        else:
            description = perk['displayProperties']['description'].rstrip('\n')
        description = description.split('\n  •')[0]

        return "**{}:** {}".format(name, description)
