from discord.ext import commands
import discord

import pydest

from cogs.utils.message_manager import MessageManager
from cogs.utils import constants, helpers
from cogs.embed_builders import pvp_stats_embed, pve_stats_embed
from cogs.models.pvp_stats import PvPStats
from cogs.models.pve_stats import PvEStats


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
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        pvp_stats_json = (await self.get_stats(platform_id, membership_id, [5]))['allPvP']['allTime']
        if not pvp_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        pvp_stats = PvPStats(pvp_stats_json)
        await manager.send_embed(pvp_stats_embed(pvp_stats, "Crucible Stats", display_name, platform_id))
        await manager.clean_messages()


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
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        pve_stats_json = await self.get_stats(platform_id, membership_id, [7,4,16,17,18,46,47])
        if not pve_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        pve_stats = PvEStats(pve_stats_json) 
        await manager.send_embed(pve_stats_embed(pve_stats, display_name, platform_id))
        await manager.clean_messages()


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
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        trials_stats_json = (await self.get_stats(platform_id, membership_id, [39]))['trialsofthenine'].get('allTime')
        if not trials_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        trials_stats = PvPStats(trials_stats_json)
        await manager.send_embed(pvp_stats_embed(trials_stats, "Trials of the Nine Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def ib(self, ctx, username=None, platform=None):
        """Display Iron Banner stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats ib` - Display your Iron Banner stats (preferred platform)
        \$`stats ib Asal#1502 bnet` - Display Asal's Iron Banner stats on Battle.net
        \$`stats ib @user` - Display a registered user's Iron Banner stats (preferred platform)
        \$`stats ib @user bnet` - Display a registered user's Iron Banner stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        ib_stats_json = (await self.get_stats(platform_id, membership_id, [19]))['ironBanner'].get('allTime')
        if not ib_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        ib_stats = PvPStats(ib_stats_json)
        await manager.send_embed(pvp_stats_embed(ib_stats, "Iron Banner Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def rumble(self, ctx, username=None, platform=None):
        """Display Rumble stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats rumble` - Display your Rumble stats (preferred platform)
        \$`stats rumble Asal#1502 bnet` - Display Asal's Rumble stats on Battle.net
        \$`stats rumble @user` - Display a registered user's Rumble stats (preferred platform)
        \$`stats rumble @user bnet` - Display a registered user's Rumble stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        rumble_stats_json = (await self.get_stats(platform_id, membership_id, [48]))['rumble'].get('allTime')
        if not rumble_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        rumble_stats = PvPStats(rumble_stats_json)
        await manager.send_embed(pvp_stats_embed(rumble_stats, "Rumble Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def doubles(self, ctx, username=None, platform=None):
        """Display Doubles stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats doubles` - Display your Doubles stats (preferred platform)
        \$`stats doubles Asal#1502 bnet` - Display Asal's Doubles stats on Battle.net
        \$`stats doubles @user` - Display a registered user's Doubles stats (preferred platform)
        \$`stats doubles @user bnet` - Display a registered user's Doubles stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        doubles_stats_json = (await self.get_stats(platform_id, membership_id, [49]))['allDoubles'].get('allTime')
        if not doubles_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        doubles_stats = PvPStats(doubles_stats_json)
        await manager.send_embed(pvp_stats_embed(doubles_stats, "Doubles Stats", display_name, platform_id))
        await manager.clean_messages()


    @stats.command()
    async def mayhem(self, ctx, username=None, platform=None):
        """Display Mayhem stats across all characters on an account

        In order to use this command for your own account, you must first register your Destiny 2
        account with the bot via the register command.

        `stats mayhem` - Display your Mayhem stats (preferred platform)
        \$`stats mayhem Asal#1502 bnet` - Display Asal's Mayhem stats on Battle.net
        \$`stats mayhem @user` - Display a registered user's Mayhem stats (preferred platform)
        \$`stats mayhem @user bnet` - Display a registered user's Mayhem stats on Battle.net
        """
        manager = MessageManager(ctx)
        await ctx.channel.trigger_typing()

        # Get membership details. This depends on whether or not a platform or username were given.
        membership_details = await helpers.get_membership_details(self.bot, ctx, username, platform)

        # If there was an error getting membership details, display it
        if isinstance(membership_details, str):
            await manager.send_message(membership_details)
            return await manager.clean_messages()
        else:
            platform_id, membership_id, display_name = membership_details

        mayhem_stats_json = (await self.get_stats(platform_id, membership_id, [25]))['allMayhem'].get('allTime')
        if not mayhem_stats_json:
            await manager.send_message("Sorry, I can't seem to retrieve those stats right now")
            return await manager.clean_messages()

        mayhem_stats = PvPStats(mayhem_stats_json)
        await manager.send_embed(pvp_stats_embed(mayhem_stats, "Mayhem Stats", display_name, platform_id))
        await manager.clean_messages()


    async def get_stats(self, platform_id, membership_id, modes):
        try:
            res = await self.bot.destiny.api.get_historical_stats(platform_id, membership_id, groups=['general'], modes=modes)
        except:
            return
        if res['ErrorCode'] == 1:
            return res['Response']
