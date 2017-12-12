def get_event_role(ctx):
    """Return the event role, if it exists"""
    result = ctx.bot.db.get_event_role_id(ctx.guild.id)

    if result:
        for role in ctx.guild.roles:
            if role.id == result.get('event_role_id'):
                return role


def get_event_delete_role(ctx):
    """Return the event delete role, if it exists"""
    result = ctx.bot.db.get_event_delete_role_id(ctx.guild.id)

    if result:
        for role in ctx.guild.roles:
            if role.id == result.get('event_delete_role_id'):
                return role


def cleanup_is_enabled(ctx):
    """Return true is message cleanup is enabled on the given guild"""
    return ctx.bot.db.get_cleanup(ctx.guild.id).get('clear_spam')
