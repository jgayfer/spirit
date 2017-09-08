from datetime import datetime

import discord
import pytz

VERSION = "1.0.3"
BLUE = discord.Colour(3381759)
SPAM_DELAY = 4

TIME_ZONES = ['ACT', 'ACDT', 'ACST', 'ADT', 'AEDT',
              'AEST', 'AKDT', 'AKST', 'AMT', 'AMST', 'AST', 'AWST',
              'BOT', 'BRT', 'BRST', 'BST', 'CDT', 'CEST', 'CET',
              'CHST', 'CLT', 'CLST', 'COT', 'CST', 'CXT', 'CWST',
              'ECT', 'EDT', 'EEST', 'EST', 'FKST', 'FKT', 'FNT', 'GFT',
              'GMT', 'GYT', 'HADT', 'HAST', 'HST', 'IST', 'KUYT',
              'LHDT', 'LHST', 'MDT', 'MSD', 'MSK', 'MST', 'NDT',
              'NFT', 'NST', 'PDT', 'PST', 'PET', 'PYT', 'PYST',
              'SAMT', 'SDT', 'SRT', 'SST', 'UYST', 'UYT', 'VET',
              'WDT', 'WEST', 'WET', 'WST', 'YST', 'YDT' ]

RELEASE_DATES = [("PC Beta", datetime(2017, 8, 28, tzinfo=pytz.timezone('US/Pacific'))),
                 ("Console Release", datetime(2017, 9, 6, tzinfo=pytz.timezone('US/Pacific'))),
                 ("PC Release", datetime(2017, 10, 24, tzinfo=pytz.timezone('US/Pacific')))]

PLATFORM_URLS = {1: 'https://i.imgur.com/DVskgVl.jpg', 2: 'https://i.imgur.com/nFv0wtf.png'}
