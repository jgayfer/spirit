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
            else:
                #armor
                pass

            paginator.add_embed(e)

        if not paginator.length:
            await manager.say("I didn't find any items that match your search.")
            return await manager.clear()

        await paginator.paginate()
        await manager.clear()


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
        wep_type = item['itemTypeDisplayName']
        info_field += "\n**Type:** {}".format(wep_type)
        attack = stats['1480404414']['value']
        info_field += "\n**Attack:** {}".format(attack)
        magazine = stats['3871231066']['value']
        info_field += "\n**Magazine:** {}".format(magazine)
        rpm = stats['4284893193']['value']
        info_field += "\n**RPM:** {}".format(rpm)
        embed.add_field(name="Stats", value=info_field, inline=True)

        # Stats field
        stats_field = ""
        impact = stats['4043523819']['value']
        stats_field += "\n**Impact:** {}".format(impact)
        wep_range = stats['1240592695']['value']
        stats_field += "\n**Range:** {}".format(wep_range)
        stability = stats['155624089']['value']
        stats_field += "\n**Stability:** {}".format(stability)
        reload_speed = stats['4188031367']['value']
        stats_field += "\n**Reload Speed:** {}".format(reload_speed)
        handling = stats['943549884']['value']
        stats_field += "\n**Handling:** {}".format(handling)
        embed.add_field(name="\u200B", value=stats_field, inline=True)

        return embed
