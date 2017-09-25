def get_event_role(bot, guild):
    """Return the event role, if it exists"""
    result = bot.db.get_event_role_id(guild.id)

    if result:
        for role in guild.roles:
            if role.id == result.get('event_role_id'):
                return role

def get_event_delete_role(bot, guild):
    """Return the event delete role, if it exists"""
    result = bot.db.get_event_delete_role_id(guild.id)

    if result:
        for role in guild.roles:
            if role.id == result.get('event_delete_role_id'):
                return role
