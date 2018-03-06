from datetime import datetime

import discord
import pytz

VERSION = "2.1.1"
BLUE = discord.Colour(3381759)
CLEANUP_DELAY = 4

OWNERS = (118926942404608003, 182759337394044929)
MODS = (118926942404608003, 182759337394044929, 319531083781767169, 169436419918528513)

SOLAR_ICON = 365922485524234240
ARC_ICON = 366298692161896458
VOID_ICON = 366298728048492544

XBOX_ICON = 372186554589773834
PS_ICON = 372186571690082305
BNET_ICON = 372186625880358912

TIME_ZONES = ['ACT', 'ACDT', 'ACST', 'ADT', 'AEDT',
              'AEST', 'AKDT', 'AKST', 'AMT', 'AMST', 'AST', 'AWST',
              'BOT', 'BRT', 'BRST', 'BST', 'CDT', 'CEST', 'CET',
              'CHST', 'CLT', 'CLST', 'COT', 'CST', 'CXT', 'CWST',
              'ECT', 'EDT', 'EEST', 'EST', 'FKST', 'FKT', 'FNT', 'GFT',
              'GMT', 'GMT+1', 'GMT+2', 'GMT+3', 'GMT+4', 'GMT+5', 'GMT+6',
              'GMT+7', 'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12',
              'GMT-1', 'GMT-2', 'GMT-3', 'GMT-4', 'GMT-5', 'GMT-6', 'GMT-7',
              'GMT-8', 'GMT-9', 'GMT-10', 'GMT-11', 'GMT-12',
              'GYT', 'HADT', 'HAST', 'HST', 'HKT', 'IST', 'JST', 'KUYT',
              'LHDT', 'LHST', 'MDT', 'MSD', 'MSK', 'MST', 'NDT',
              'NFT', 'NST', 'NZST', 'NZDT', 'PDT', 'PST', 'PET', 'PYT', 'PYST',
              'SAMT', 'SDT', 'SRT', 'SST',
              'UTC', 'UTC+1', 'UTC+2', 'UTC+3', 'UTC+4', 'UTC+5', 'UTC+6',
              'UTC+7', 'UTC+8', 'UTC+9', 'UTC+10', 'UTC+11', 'UTC+12',
              'UTC-1', 'UTC-2', 'UTC-3', 'UTC-4', 'UTC-5', 'UTC-6', 'UTC-7',
              'UTC-8', 'UTC-9', 'UTC-10', 'UTC-11', 'UTC-12',
              'UYST', 'UYT', 'VET', 'WDT', 'WEST', 'WET', 'WST', 'YST', 'YDT']

RELEASE_DATES = [
                 ("PC Beta", datetime(2017, 8, 28, tzinfo=pytz.timezone('US/Pacific'))),
                 ("Console Release", datetime(2017, 9, 6, tzinfo=pytz.timezone('US/Pacific'))),
                 ("Console Raid", datetime(2017, 9, 13, tzinfo=pytz.timezone('US/Pacific'))),
                 ("PC Release", datetime(2017, 10, 24, tzinfo=pytz.timezone('US/Pacific'))),
                 ("Curse of Osiris", datetime(2017, 12, 5, tzinfo=pytz.timezone('US/Pacific')))
                ]

PLATFORMS = {'bnet': 4, 'xbox': 1, 'ps': 2}
PLATFORM_URLS = {1: 'https://i.imgur.com/DVskgVl.jpg', 2: 'https://i.imgur.com/nFv0wtf.png', 4: 'https://i.imgur.com/pMA45Vc.png'}

ELEMENTS = {2: 'https://i.imgur.com/pR2hu13.png', 3: 'https://i.imgur.com/paWpNGd.png', 4: 'https://i.imgur.com/RHDetvb.png'}
