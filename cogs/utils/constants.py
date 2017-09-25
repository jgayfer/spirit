from datetime import datetime

import discord
import pytz

VERSION = "1.3.2"
BLUE = discord.Colour(3381759)
SPAM_DELAY = 4

OWNERS = (118926942404608003, 182759337394044929)
MODS = (118926942404608003, 182759337394044929, 319531083781767169)
SERVERS_NO_COUNT = (264445053596991498, 110373943822540800, 349975342884061187)

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
                 ("PC Release", datetime(2017, 10, 24, tzinfo=pytz.timezone('US/Pacific')))
                ]

PLATFORMS = {'PC': 4, 'XBOX': 1, 'PLAYSTATION': 2}
PLATFORM_URLS = {1: 'https://i.imgur.com/DVskgVl.jpg', 2: 'https://i.imgur.com/nFv0wtf.png'}
