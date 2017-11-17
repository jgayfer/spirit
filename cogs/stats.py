from discord.ext import commands
import discord

import pydest

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Stats:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    @commands.group()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def stats(self, ctx):
        """Display various Destiny 2 character stats"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'stats')

    @stats.command()
    async def pvp(self, ctx, platform=None, username=None):
        """Display Crucible stats for all characters on an account"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await self.get_membership_details(ctx, platform, username)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        else:
            platform_id, membership_id, display_name = membership_details

        # Get PvP stats
        try:
            res = await self.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=[5])
        except:
            await manager.say("Sorry, I can't seem to retrieve your stats right now~")
            return await manager.clear()

        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now--")
            return await manager.clear()

        pvp_stats = res['Response']['allPvP'].get('allTime')

        if not pvp_stats:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()

        time_played = pvp_stats['secondsPlayed']['basic']['displayValue']
        kdr = pvp_stats['killsDeathsRatio']['basic']['displayValue']
        best_weapon = pvp_stats['weaponBestType']['basic']['displayValue']
        games_played = pvp_stats['activitiesEntered']['basic']['displayValue']
        best_kills = pvp_stats['bestSingleGameKills']['basic']['displayValue']
        best_spree = pvp_stats['longestKillSpree']['basic']['displayValue']
        combat_rating = pvp_stats['combatRating']['basic']['displayValue']
        kills = pvp_stats['kills']['basic']['displayValue']
        assists = pvp_stats['assists']['basic']['displayValue']
        deaths = pvp_stats['deaths']['basic']['displayValue']
        kda = str(round((int(kills) + int(assists)) / int(deaths), 2))

        # Can't convert a string of '-' to a float!
        win_ratio = pvp_stats['winLossRatio']['basic']['displayValue']
        if win_ratio != '-':
            win_ratio = float(win_ratio)
            win_rate = str(round(win_ratio / (win_ratio + 1) * 100, 1)) + " %"
        else:
            win_rate = win_ratio

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{} | Crucible Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform_id))
        e.add_field(name='Kills', value=kills, inline=True)
        e.add_field(name='Assists', value=assists, inline=True)
        e.add_field(name='Deaths', value=deaths, inline=True)
        e.add_field(name='KD', value=kdr, inline=True)
        e.add_field(name='KA/D', value=kda, inline=True)
        e.add_field(name='Win Rate', value=win_rate, inline=True)
        e.add_field(name='Best Spree', value=best_spree, inline=True)
        e.add_field(name='Most Kills in a Game', value=best_kills, inline=True)
        e.add_field(name='Favorite Weapon', value=best_weapon, inline=True)
        e.add_field(name='Combat Rating', value=combat_rating, inline=True)
        e.add_field(name='Games Played', value=games_played, inline=True)
        e.add_field(name='Time Played', value=time_played, inline=True)

        await manager.say(e, embed=True, delete=False)
        await manager.clear()


    @stats.command()
    async def pve(self, ctx, platform=None, username=None):
        """Display PvE stats for all characters on an account"""
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await self.get_membership_details(ctx, platform, username)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        else:
            platform_id, membership_id, display_name = membership_details

        # Get PvE stats
        try:
            res = await self.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=[7,4,16,18])
        except pydest.PydestException as e:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        pve_stats = res['Response']

        if not pve_stats:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()

        time_played = pve_stats['allPvE']['allTime']['totalActivityDurationSeconds']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        best_weapon = pve_stats['allPvE']['allTime']['weaponBestType']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_heroic_events = pve_stats['allPvE']['allTime']['heroicPublicEventsCompleted']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_events = pve_stats['allPvE']['allTime']['publicEventsCompleted']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        num_raids = pve_stats['raid']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['raid']) else 0
        raid_time = pve_stats['raid']['allTime']['totalActivityDurationSeconds']['basic']['displayValue'] if len(pve_stats['raid']) else 0
        num_nightfall = pve_stats['nightfall']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['nightfall']) else 0
        num_strikes = pve_stats['allStrikes']['allTime']['activitiesCleared']['basic']['displayValue'] if len(pve_stats['allStrikes']) else 0
        fastest_nightfall = pve_stats['nightfall']['allTime']['fastestCompletionMs']['basic']['displayValue'] if len(pve_stats['nightfall']) else 0
        kills = pve_stats['allPvE']['allTime']['kills']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        assists = pve_stats['allPvE']['allTime']['assists']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0
        deaths = pve_stats['allPvE']['allTime']['deaths']['basic']['displayValue'] if len(pve_stats['allPvE']) else 0

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{} | PvE Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform_id))
        e.add_field(name='Kills', value=kills, inline=True)
        e.add_field(name='Assists', value=assists, inline=True)
        e.add_field(name='Deaths', value=deaths, inline=True)
        e.add_field(name='Strikes', value=num_strikes, inline=True)
        e.add_field(name='Nightfalls', value=num_nightfall, inline=True)
        e.add_field(name='Fastest Nightfall', value=fastest_nightfall, inline=True)
        e.add_field(name='Public Events', value=num_events, inline=True)
        e.add_field(name='Heroic Public Events', value=num_heroic_events, inline=True)
        e.add_field(name='Favorite Weapon', value=best_weapon, inline=True)
        e.add_field(name='Total Raid Time', value=raid_time, inline=True)
        e.add_field(name='Raids', value=num_raids, inline=True)
        e.add_field(name='Time Played', value=time_played, inline=True)

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
            display_name = username

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
                    display_name = info.get('bliz_name')
                elif platform_id == 1:
                    membership_id = info.get('xbox_id')
                    display_name = info.get('xbox_name')
                elif platform_id == 2:
                    membership_id = info.get('psn_id')
                    display_name = info.get('psn_name')

                if not membership_id:
                    return "Oops, you don't have a connected account of that type."

            else:
                return ("You must first register your Destiny 2 account with the "
                      + "`{}register` command.".format(ctx.prefix))

        return platform_id, membership_id, display_name
