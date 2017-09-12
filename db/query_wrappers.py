from db.dbase import DBase

def get_event_role(guild):
    """Return the event role, if it exists"""
    with DBase() as db:
        rows = db.get_event_role_id(guild.id)

    if len(rows) and len(rows[0]):
        for role in guild.roles:
            if role.id == rows[0][0]:
                return role
