from discord.ext import commands
import discord

import pydest
import json

from cogs.utils.message_manager import MessageManager
from cogs.utils import constants, helpers

class Clan:
    class RewardEntry:
        name = ""
        earned = False
        reward_hash = 0
        
        def __init__(self, rhash, earned):
            self.reward_hash = rhash
            self.earned = earned


        def __str__(self):
            return "reward hash={} | name={} | earned={}".format(self.reward_hash,self.name, self.earned)


        def set_name(self, name):
            self.name = name

        
        def __len__(self):
            return len(self.name)


    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def clan(self, ctx, username=None, platform=None):
        """Display a Destiny 2 clan
        
        In order to use this command for your own clan, you must first register your Destiny 2
        account with the bot via the register command.

        'clan' - Display your clan
        """

        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()

        platform_id, membership_id, display_name = membership_details

        try:
            res = await self.bot.destiny.api.get_groups_for_member(platform_id, membership_id)
        except:
            await manager.send_message("Sorry, I can't seem to retrieve that clan right now")
            return await manager.clean_messages()

        if res['ErrorCode'] != 1:
            await manager.send_message("Sorry I can't seem to retrieve that clan right now")
            return await manager.clean_messages()

        group_id = res['Response']['results'][0]['member']['groupId']

        try:
            ms = await self.bot.destiny.api.get_weekly_milestones(group_id)
            ms_def = await self.bot.destiny.api.get_weekly_milestone_definitions(ms['Response']['milestoneHash'])
        except:
            await manager.send_message("Sorry, I can't seem to retrieve that clan right now")
            return await manager.clean_messages()

        clan_stats = res['Response']['results'][0]['group']
        motto = clan_stats['motto'].strip()
        name = clan_stats['name'].strip()
        about = clan_stats['about'].strip()
        call_sign = clan_stats['clanInfo']['clanCallsign'].strip()
        mc = str(clan_stats['memberCount']).strip()
        lvl = str(clan_stats['clanInfo']['d2ClanProgressions']['584850370']['level']).strip()
        weekly = clan_stats['clanInfo']['d2ClanProgressions']['584850370']['weeklyProgress']
        weekly_cap = clan_stats['clanInfo']['d2ClanProgressions']['584850370']['weeklyLimit']
        next_lvl_prog = clan_stats['clanInfo']['d2ClanProgressions']['584850370']['progressToNextLevel']
        next_lvl = clan_stats['clanInfo']['d2ClanProgressions']['584850370']['nextLevelAt']
        weekly_prog = str(weekly) + '/' + str(weekly_cap)
        clan_prog = str(next_lvl_prog) + '/' + str(next_lvl)
        milestones = ""

        reward_hash = ms['Response']['rewards'][0]['rewardCategoryHash']
        reward_list = []
        for item in ms['Response']['rewards'][0]['entries']:
            reward_list.append(Clan.RewardEntry(item['rewardEntryHash'], item['earned']))
    
        for item in ms_def['Response']['rewards'][str(reward_hash)]['rewardEntries']:
            # name match up
            for entry in reward_list:
                if str(entry.reward_hash) == str(item):
                    entry.set_name(ms_def['Response']['rewards'][str(reward_hash)]['rewardEntries'][str(item)]['rewardEntryIdentifier'])

        for entry in reward_list:
            if entry.name == 'nightfall':
                milestones += '{0: <18}'.format(entry.name.title())
                milestones += ":white_check_mark:" if entry.earned else ":x:" 

            elif entry.name == 'trials':
                milestones += '\t\t{0: <20}'.format(entry.name.title())
                milestones += ":white_check_mark:\n\n" if entry.earned else ":x:\n\n" 

            elif entry.name == 'raid':
                milestones += '{0: <20}'.format(entry.name.title())
                milestones += ":white_check_mark:" if entry.earned else ":x:" 

            elif entry.name == 'pvp':
                milestones += ' \t\t{0: <20}'.format(entry.name.title())
                milestones += ":white_check_mark:\n\n" if entry.earned else ":x:\n\n"

        e = discord.Embed(colour=constants.BLUE)
        e.set_author(name="{}".format(name))
        e.add_field(name='Motto', value=motto, inline=True)
        e.add_field(name='About', value=about, inline=True)
        e.add_field(name='Callsign', value =call_sign, inline=True)
        e.add_field(name='Number of Members', value=mc, inline=True)
        e.add_field(name='Level', value=lvl, inline=True)
        e.add_field(name='Weekly clan progression', value=weekly_prog, inline=True)
        e.add_field(name='Progression to next clan level', value=clan_prog, inline=True)
        e.add_field(name='Milestones', value=milestones, inline=False)

        await manager.send_embed(e)
        await manager.clean_messages()
