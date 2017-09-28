from discord.ext import commands
import discord

from cogs.utils.messages import MessageManager
from cogs.utils import constants


class Stats:

    def __init__(self, bot, destiny):
        self.bot = bot
        self.destiny = destiny


    @commands.group()
    async def stats(self, ctx):
        """Display various Destiny 2 character stats"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'stats')

    @stats.command()
    async def pvp(self, ctx):
        """Display Crucible stats for all characters on an account"""
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

        # Get display name
        res = await self.destiny.api.get_profile(platform, membership_id, ['Profiles'])
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        display_name = res['Response']['profile']['data']['userInfo']['displayName']

        # Get PvP stats
        res = await self.destiny.api.get_historical_stats(platform, membership_id, modes=[5])
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        pvp_stats = res['Response']['allPvP'].get('allTime')

        if not len(pvp_stats):
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()

        time_played = pvp_stats['secondsPlayed']['basic']['displayValue']
        kdr = pvp_stats['killsDeathsRatio']['basic']['displayValue']
        kda = pvp_stats['killsDeathsAssists']['basic']['displayValue']
        best_weapon = pvp_stats['weaponBestType']['basic']['displayValue']
        games_played = pvp_stats['activitiesEntered']['basic']['displayValue']
        best_kills = pvp_stats['bestSingleGameKills']['basic']['displayValue']
        best_spree = pvp_stats['longestKillSpree']['basic']['displayValue']
        combat_rating = pvp_stats['combatRating']['basic']['displayValue']
        kills = pvp_stats['kills']['basic']['displayValue']
        assists = pvp_stats['assists']['basic']['displayValue']
        deaths = pvp_stats['deaths']['basic']['displayValue']

        # Can't convert a string of '-' to a float!
        win_ratio = pvp_stats['winLossRatio']['basic']['displayValue']
        if win_ratio != '-':
            win_ratio = float(win_ratio)
            win_rate = str(round(win_ratio / (win_ratio + 1) * 100, 1)) + " %"
        else:
            win_rate = win_ratio

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{} | Crucible Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform))
        e.add_field(name='Kills', value=kills, inline=True)
        e.add_field(name='Assists', value=assists, inline=True)
        e.add_field(name='Deaths', value=deaths, inline=True)
        e.add_field(name='KD Ratio', value=kdr, inline=True)
        e.add_field(name='Efficiency (KAD)', value=kda, inline=True)
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
    async def pve(self, ctx):
        """Display PvE stats for all characters on an account"""
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

        # Get display name
        res = await self.destiny.api.get_profile(platform, membership_id, ['Profiles'])
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        display_name = res['Response']['profile']['data']['userInfo']['displayName']

        # Get PvE stats
        res = await self.destiny.api.get_historical_stats(platform, membership_id, modes=[7,4,16,18])
        if res['ErrorCode'] != 1:
            await manager.say("Sorry, I can't seem to retrieve your stats right now")
            return await manager.clear()
        pve_stats = res['Response']

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
        e.set_author(name="{} | PvE Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform))
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
