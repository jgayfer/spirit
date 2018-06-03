class PvEStats:
    """This class represents the general PvE stats for a Destiny 2 character (or set of characters)
    
    Args:
        pve_stats: The 'response' portion of the JSON returned from the D2 'GetHistoricalStats' endpoint
                   with modes 7,4,16,17,18,46,47 (given as a dictionary).
    """
        
    def __init__(self, pve_stats):
        
        # General PvE stats
        if len(pve_stats['allPvE']):
            self.time_played = pve_stats['allPvE']['allTime']['totalActivityDurationSeconds']['basic']['displayValue']
            self.best_weapon = pve_stats['allPvE']['allTime']['weaponBestType']['basic']['displayValue'] 
            self.kills = pve_stats['allPvE']['allTime']['kills']['basic']['displayValue'] 
            self.assists = pve_stats['allPvE']['allTime']['assists']['basic']['displayValue'] 
            self.deaths = pve_stats['allPvE']['allTime']['deaths']['basic']['displayValue'] 
            self.event_count = pve_stats['allPvE']['allTime']['publicEventsCompleted']['basic']['displayValue'] 
            self.heroic_event_count = pve_stats['allPvE']['allTime']['heroicPublicEventsCompleted']['basic']['displayValue'] 
        else:
            self.time_played = '-' 
            self.best_weapon = '-'
            self.kills = 0
            self.assists = 0
            self.deaths = 0
            self.event_count = 0
            self.heroic_event_count = 0

        # Strike stats
        if len(pve_stats['allStrikes']):
            self.strike_count = pve_stats['allStrikes']['allTime']['activitiesCleared']['basic']['displayValue']     
        else:
            self.strike_count = 0

        # Raid stats
        if len(pve_stats['raid']):
            self.raid_count = pve_stats['raid']['allTime']['activitiesCleared']['basic']['displayValue']
            self.raid_time = pve_stats['raid']['allTime']['totalActivityDurationSeconds']['basic']['displayValue'] 
        else:
            self.raid_count = 0
            self.raid_time = '-'

        # Nightfall stats
        self.nightfall_count = self._sum_nightfalls(pve_stats)
        self.fastest_nightfall = self._find_fastest_nightfall(pve_stats)


    def _find_fastest_nightfall(self, pve_stats):
        times = {}
        if len(pve_stats['nightfall']):
            times['nightfall'] = pve_stats['nightfall']['allTime']['fastestCompletionMs']['basic']['value']
        if len(pve_stats['heroicNightfall']):
            times['heroicNightfall'] = pve_stats['heroicNightfall']['allTime']['fastestCompletionMs']['basic']['value']
        if len(pve_stats['scored_nightfall']):
            times['scored_nightfall'] = pve_stats['scored_nightfall']['allTime']['fastestCompletionMs']['basic']['value']
        if len(pve_stats['scored_heroicNightfall']):
            times['scored_heroicNightfall'] = pve_stats['scored_heroicNightfall']['allTime']['fastestCompletionMs']['basic']['value']

        non_zero_times = {k:v for (k,v) in times.items() if v > 0} 
        print(non_zero_times)
        return pve_stats[min(non_zero_times, key=non_zero_times.get)]['allTime']['fastestCompletionMs']['basic']['displayValue']
    

    def _sum_nightfalls(self, pve_stats):
        count = 0
        if len(pve_stats['nightfall']):
            count += pve_stats['nightfall']['allTime']['activitiesCleared']['basic']['value']
        if len(pve_stats['heroicNightfall']):
            count += pve_stats['heroicNightfall']['allTime']['activitiesCleared']['basic']['value']
        if len(pve_stats['scored_nightfall']):
            count += pve_stats['scored_nightfall']['allTime']['activitiesCleared']['basic']['value']
        if len(pve_stats['scored_heroicNightfall']):
            count += pve_stats['scored_heroicNightfall']['allTime']['activitiesCleared']['basic']['value']

        return int(count)
