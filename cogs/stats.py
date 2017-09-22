from discord.ext import commands
import discord

from db.dbase import DBase
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
        with DBase() as db:
            entries = db.get_d2_info(ctx.author.id)
        if len(entries) > 0 and entries[0][0] != None and entries[0][1] != None:
            platform = entries[0][0]
            membership_id = entries[0][1]
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

        time_played = pvp_stats['secondsPlayed']['basic']['displayValue']
        kdr = pvp_stats['killsDeathsRatio']['basic']['displayValue']
        kda = pvp_stats['killsDeathsAssists']['basic']['displayValue']
        win_rate = str(float(pvp_stats['winLossRatio']['basic']['displayValue']) * 100) + " %"
        best_weapon = pvp_stats['weaponBestType']['basic']['displayValue']
        games_played = pvp_stats['activitiesEntered']['basic']['displayValue']
        best_kills = pvp_stats['bestSingleGameKills']['basic']['displayValue']
        best_spree = pvp_stats['longestKillSpree']['basic']['displayValue']
        combat_rating = pvp_stats['combatRating']['basic']['displayValue']

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{} | Crucible Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform))

        e.add_field(name='KD Ratio', value=kdr, inline=True)
        e.add_field(name='Efficiency (KDA)', value=kda, inline=True)
        e.add_field(name='Win Rate', value=win_rate, inline=True)
        e.add_field(name='Best Spree', value=best_spree, inline=True)
        e.add_field(name='Most Kills in a Game', value=best_kills, inline=True)
        e.add_field(name='Favorite Weapon', value=best_weapon, inline=True)
        e.add_field(name='Combat Rating', value=combat_rating, inline=True)
        e.add_field(name='Games Played', value=games_played, inline=True)
        e.add_field(name='Time Played', value=time_played, inline=True)

        await manager.say(e, embed=True, delete=False)
        await manager.clear()
