from cogs.utils import helpers


class PvPStats:

    def __init__(self, pvp_stats):
        self.time_played = pvp_stats['secondsPlayed']['basic']['displayValue']
        self.kdr = pvp_stats['killsDeathsRatio']['basic']['displayValue']
        self.best_weapon = pvp_stats['weaponBestType']['basic']['displayValue']
        self.games_played = pvp_stats['activitiesEntered']['basic']['displayValue']
        self.best_kills = pvp_stats['bestSingleGameKills']['basic']['displayValue']
        self.best_spree = pvp_stats['longestKillSpree']['basic']['displayValue']
        self.combat_rating = pvp_stats['combatRating']['basic']['displayValue']
        self.kills = pvp_stats['kills']['basic']['displayValue']
        self.assists = pvp_stats['assists']['basic']['displayValue']
        self.deaths = pvp_stats['deaths']['basic']['displayValue']
        self.kda = str(round((int(self.kills) + int(self.assists)) / int(self.deaths), 2))
        self.win_rate = helpers.calc_win_rate(pvp_stats['winLossRatio']['basic']['displayValue'])
