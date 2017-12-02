from discord.ext import commands
import discord

import pydest

from cogs.utils.messages import MessageManager
from cogs.utils import constants, helpers

####### DEBUGGING ############
import json


class Stats:

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def stats(self, ctx):
        """Display various Destiny 2 stats"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'stats')


    @stats.command()
    async def pvp(self, ctx, username=None, platform=None):
        """Display PvP stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats pvp` - Display your PvP stats (preferred platform)
        \$`stats pvp Asal#1502 bnet` - Display Asal's PvP stats on Battle.net
        \$`stats pvp @user` - Display a registered user's PvP stats (preferred platform)
        \$`stats pvp @user bnet` - Display a registered user's PvP stats on Battle.net
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        else:
            platform_id, membership_id, display_name = membership_details

        # Get PvP stats
        try:
            res = await self.bot.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=[5])
        except:
            await manager.say("Sorry, I can't seem to retrieve those stats right now~")
            return await manager.clear()

        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve those stats right now--")
            return await manager.clear()

        pvp_stats = res['Response']['allPvP'].get('allTime')

        if not pvp_stats:
            await manager.say("Sorry, I can't seem to retrieve those stats right now- -")
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
            win_rate = str(round(win_ratio / (win_ratio + 1) * 100, 1)) + "%"
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
    async def pve(self, ctx, username=None, platform=None):
        """Display PvE stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats pve` - Display your PvE stats (preferred platform)
        \$`stats pve Asal#1502 bnet` - Display Asal's PvE stats on Battle.net
        \$`stats pve @user` - Display a registered user's PvE stats (preferred platform)
        \$`stats pve @user bnet` - Display a registered user's PvE stats on Battle.net
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        else:
            platform_id, membership_id, display_name = membership_details

        # Get PvE stats
        try:
            res = await self.bot.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=[7,4,16,18])
        except pydest.PydestException as e:
            await manager.say("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clear()
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clear()
        pve_stats = res['Response']

        if not pve_stats:
            await manager.say("Sorry, I can't seem to retrieve those stats right now")
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


    @stats.command()
    async def trials(self, ctx, username=None, platform=None):
        """Display Trials stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats trials` - Display your Trials stats (preferred platform)
        \$`stats trials Asal#1502 bnet` - Display Asal's Trials stats on Battle.net
        \$`stats trials @user` - Display a registered user's Trials stats (preferred platform)
        \$`stats trials @user bnet` - Display a registered user's Trials stats on Battle.net
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, ctx.prefix, [ctx.message])
        await ctx.channel.trigger_typing()

        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        if isinstance(membership_details, str):
            await manager.say(membership_details)
            return await manager.clear()
        
        platform_id, membership_id, display_name = membership_details        
        
        try:
            res = await self.bot.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=[39])

            if res['ErrorCode'] != 1: 
                await manager.say("Sorry, I can't seem to retrieve those stats right now")
                return await manager.clear()

            trials_stats = res['Response']['trialsofthenine'].get('allTime')
            with open('res.json', 'w') as outfile:
                json.dump(res['Response'], outfile)
            
            #| time played | KDR | best weapon | games played | most kills in sg | longest spree | combar rating | kills | assists | deaths | kda 

            time_played = trials_stats['secondsPlayed']['basic']['displayValue']
            kdr = trials_stats['killsDeathsRatio']['basic']['displayValue']
            best_weapon = trials_stats['weaponBestType']['basic']['displayValue']
            games_played = trials_stats['activitiesEntered']['basic']['displayValue']
            best_kills = trials_stats['bestSingleGameKills']['basic']['displayValue']
            best_spree = trials_stats['longestKillSpree']['basic']['displayValue']
            combat_rating = trials_stats['combatRating']['basic']['displayValue']
            kills = trials_stats['kills']['basic']['displayValue']
            assists = trials_stats['assists']['basic']['displayValue']
            deaths = trials_stats['deaths']['basic']['displayValue']
            kda = str(round((int(kills) + int(assists)) /int(deaths), 2))
            win_ratio = trials_stats['winLossRatio']['basic']['displayValue']
            if win_ratio != '-':
                win_ratio = float(win_ratio)
                win_rate = str(round(win_ratio / (win_ratio + 1) * 100, 1)) + "%"
            else:
                win_rate = win_ratio
            
            e = discord.Embed(color=constants.BLUE)
            e.set_author(name="{} | Trials of the Nine stats".format(display_name),
            icon_url=constants.PLATFORM_URLS.get(platform_id))
            e.add_field(name='Kills', value=kills, inline=True)
            e.add_field(name='Assists', value=assists, inline=True)
            e.add_field(name='Deaths', value=deaths, inline=True)
            e.add_field(name='KD', value=kdr, inline=True)
            e.add_field(name='KA/D', value=kda, inline=True)
            e.add_field(name='Win Rate', value=win_rate, inline=True)
            e.add_field(name='Best Spree', value=best_spree, inline=True)
            e.add_field(name='Most kills in a Game', value=best_kills, inline=True)
            e.add_field(name='Favorite Weapon', value=best_weapon, inline=True)
            e.add_field(name='Combat Rating', value=combat_rating, inline=True)
            e.add_field(name='Games Played', value=games_played, inline=True)
            e.add_field(name='Time Played', value=time_played, inline=True)

            await manager.say(e, embed=True, delete=False)
            await manager.clear()

        except:
            await manager.say("Sorry, I can't seem to retrieve those stats right now~")
            return await manager.clear()