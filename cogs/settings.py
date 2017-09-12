import asyncio

from discord.ext import commands
import discord

from db.dbase import DBase
from cogs.utils.messages import MessageManager
from cogs.utils.format import format_role_name


class Settings:

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix):
        """
        Change the server's command prefix (admin only)

        Ex. '!setprefix $'
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        if len(new_prefix) > 5:
            await manager.say("Prefix must be less than 6 characters.")
            return await manager.clear()

        with DBase() as db:
            db.set_prefix(ctx.guild.id, new_prefix)
        await manager.say("Command prefix has been changed to " + new_prefix)
        return await manager.clear()


    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])
            await manager.say("Oops! You didn't provide a new prefix.")
            await manager.clear()


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modrole(self, ctx, *, mod_role):
        """Set the server's mod role (admin only)

        Certain commands, such as creating events, require the user to have a certain privelge.
        By default, the default privilege is Administrator. If a mod role is set, then any user
        that is of the mod role or higher may invoke the previously Administrator only commands.

        **Note:** Mentioning the role directly with this command will not work. You must the name
        of the role without mentioning it.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        guild_mod_role = None
        for role in ctx.guild.roles:
            if role.name in (mod_role, "@{}".format(mod_role)):
                guild_mod_role = role

        if not guild_mod_role:
            await manager.say("I couldn't find a role called **{}** on this server. ".format(mod_role)
                            + "Note that you must provide only the name of the role. "
                            + "Mention it with the @ sign won't work.")
            return await manager.clear()

        with DBase() as db:
            db.set_mod_role_id(ctx.guild.id, guild_mod_role.id)

        await manager.say("The mod role has been set to: **{}**".format(format_role_name(guild_mod_role)))
        return await manager.clear()


    @modrole.error
    async def modrole_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

            with DBase() as db:
                rows = db.get_mod_role_id(ctx.guild.id)

            mod_role = None
            if len(rows[0]):
                for role in ctx.guild.roles:
                    if role.id == rows[0][0]:
                        mod_role = role

            if not mod_role:
                role_display = 'None (Administrator)'
            else:
                role_display = format_role_name(mod_role)

            await manager.say("The current mod role is: **{}**\n\nTo change the mod role, ".format(role_display)
                            + "use `{}modrole <role_name>`".format(ctx.prefix))
            await manager.clear()


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def togglecleanup(self, ctx):
        """
        Toggle command message cleanup on/off (admin only)

        When enabled, command message spam will be deleted a few seconds
        after a command has been invoked. This feature is designed to
        keep bot related spam to a minimum. Only non important messages will
        be deleted if this is enabled; messages like the help message or the
        roster, for example, will not be removed.
        """
        manager = MessageManager(self.bot, ctx.author, ctx.channel, [ctx.message])

        with DBase() as db:
            db.toggle_cleanup(ctx.guild.id)
            cleanup = db.get_cleanup(ctx.guild.id)

        status = 'enabled' if cleanup else 'disabled'
        await manager.say("Command message cleanup is now *{}*".format(status))
        return await manager.clear()
