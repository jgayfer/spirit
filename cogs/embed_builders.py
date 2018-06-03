import discord

from cogs.utils import constants


def pvp_stats_embed(stats, title, display_name, platform_id):
    e = discord.Embed(color=constants.BLUE)
    e.set_author(name="{} | {}".format(display_name, title), icon_url=constants.PLATFORM_URLS.get(platform_id))
    e.add_field(name='Kills', value=stats.kills, inline=True)
    e.add_field(name='Assists', value=stats.assists, inline=True)
    e.add_field(name='Deaths', value=stats.deaths, inline=True)
    e.add_field(name='KD', value=stats.kdr, inline=True)
    e.add_field(name='KA/D', value=stats.kda, inline=True)
    e.add_field(name='Win Rate', value=stats.win_rate, inline=True)
    e.add_field(name='Best Spree', value=stats.best_spree, inline=True)
    e.add_field(name='Most kills in a Game', value=stats.best_kills, inline=True)
    e.add_field(name='Favorite Weapon', value=stats.best_weapon, inline=True)
    e.add_field(name='Combat Rating', value=stats.combat_rating, inline=True)
    e.add_field(name='Games Played', value=stats.games_played, inline=True)
    e.add_field(name='Time Played', value=stats.time_played, inline=True)
    return e


def pve_stats_embed(stats, display_name, platform_id):
    e = discord.Embed(colour=constants.BLUE)
    e.set_author(name="{} | PvE Stats".format(display_name), icon_url=constants.PLATFORM_URLS.get(platform_id))
    e.add_field(name='Kills', value=stats.kills, inline=True)
    e.add_field(name='Assists', value=stats.assists, inline=True)
    e.add_field(name='Deaths', value=stats.deaths, inline=True)
    e.add_field(name='Strikes', value=stats.strike_count, inline=True)
    e.add_field(name='Nightfalls', value=stats.nightfall_count, inline=True)
    e.add_field(name='Fastest Nightfall', value=stats.fastest_nightfall, inline=True)
    e.add_field(name='Public Events', value=stats.event_count, inline=True)
    e.add_field(name='Heroic Public Events', value=stats.heroic_event_count, inline=True)
    e.add_field(name='Favorite Weapon', value=stats.best_weapon, inline=True)
    e.add_field(name='Total Raid Time', value=stats.raid_time, inline=True)
    e.add_field(name='Raids', value=stats.raid_count, inline=True)
    e.add_field(name='Time Played', value=stats.time_played, inline=True)
    return e
