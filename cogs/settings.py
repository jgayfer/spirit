from discord.ext import commands

from db.query_wrappers import get_event_role, get_event_delete_role, cleanup_is_enabled
from cogs.utils.message_manager import MessageManager
from cogs.utils.format import format_role_name


class Settings:

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    async def settings(self, ctx):
        """Manage the bot's server specific settings (Manage Server only)"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, 'settings')


    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, new_prefix):
        """
        Change the server's command prefix (Manage Server only)
        """
        manager = MessageManager(ctx)

        if len(new_prefix) > 5:
            await manager.send_message("Prefix must be less than 6 characters.")
            return await manager.clean_messages()

        self.bot.db.set_prefix(ctx.guild.id, new_prefix)
        await manager.send_message("Command prefix has been changed to " + new_prefix)
        return await manager.clean_messages()


    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(ctx)
            await manager.send_message("Oops! You didn't provide a new prefix.")
            await manager.clean_messages()


    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def seteventrole(self, ctx, *, event_role):
        """Set the lowest role that is able to create events (Manage Server only)

        By default, creating events requires the user to have Manage Server permissions.
        But if an event role is set, then any user that is of the event role or higher may
        create events.

        **Note:** Mentioning the role directly with this command will not work. You must provide
        only the name of the role without mentioning it. The role name is also case sensitive!
        """
        manager = MessageManager(ctx)

        guild_event_role = None
        for role in ctx.guild.roles:
            if role.name in (event_role, "@{}".format(event_role)):
                guild_event_role = role

        if not guild_event_role:
            await manager.send_message("I couldn't find a role called **{}** on this server.\n\n".format(event_role)
                            + "Note that you must provide only the name of the role. "
                            + "Mentioning it with the @ sign won't work. The role name is also "
                            + "case sensitive!")
            return await manager.clean_messages()

        self.bot.db.set_event_role_id(ctx.guild.id, guild_event_role.id)
        await manager.send_message("The event role has been set to: **{}**".format(format_role_name(guild_event_role)))
        return await manager.clean_messages()


    @seteventrole.error
    async def seteventrole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(ctx)
            event_role = get_event_role(ctx)

            if not event_role:
                role_display = 'None (anyone can make events)'
            else:
                role_display = format_role_name(event_role)

            await manager.send_message("The current event role is: **{}**\n\n".format(role_display)
                            + "To change the event role, use '{}settings seteventrole <role_name>'".format(ctx.prefix))
            await manager.clean_messages()


    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def seteventdeleterole(self, ctx, *, event_role):
        """Set the lowest role that is able to delete events (Manage Server only)

        By default, deleting an event requires the user to have Manage Server permissions (or be the
        user who created the event). But if an event delete role is set, then any user that is of
        the event delete role or higher may delete events.

        **Note:** Mentioning the role directly with this command will not work. You must provide
        only the name of the role without mentioning it. The role name is also case sensitive!
        """
        manager = MessageManager(ctx)

        guild_event_delete_role = None
        for role in ctx.guild.roles:
            if role.name in (event_role, "@{}".format(event_role)):
                guild_event_delete_role = role

        if not guild_event_delete_role:
            await manager.send_message("I couldn't find a role called **{}** on this server.\n\n".format(event_role)
                            + "Note that you must provide only the name of the role. "
                            + "Mentioning it with the @ sign won't work. The role name is also "
                            + "case sensitive!")
            return await manager.clean_messages()

        self.bot.db.set_event_delete_role_id(ctx.guild.id, guild_event_delete_role.id)
        await manager.send_message("The event delete role has been set to: **{}**".format(format_role_name(guild_event_delete_role)))
        return await manager.clean_messages()


    @seteventdeleterole.error
    async def seteventdeleterole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(ctx)
            event_role = get_event_delete_role(ctx)

            if not event_role:
                role_display = '**None** (only Manage Sever members can delete events)'
            else:
                role_display = format_role_name(event_role)

            await manager.send_message("The current event delete role is: {}\n\n".format(role_display)
                            + "To change the event delete role, use '{}settings seteventdeleterole <role_name>'".format(ctx.prefix))
            await manager.clean_messages()


    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def togglecleanup(self, ctx):
        """
        Toggle command message cleanup on/off (Manage Server only)

        When enabled, command message spam will be deleted a few seconds
        after a command has been invoked. This feature is designed to
        keep bot related spam to a minimum. Only non important messages will
        be deleted if this is enabled; messages like the help message or the
        roster, for example, will not be removed.
        """
        manager = MessageManager(ctx)

        self.bot.db.toggle_cleanup(ctx.guild.id)
        cleanup_status_text = 'enabled' if cleanup_is_enabled(ctx) else 'disabled'

        await manager.send_message("Command message cleanup is now *{}*".format(cleanup_status_text))
        return await manager.clean_messages()
