from db.dbase import DBase

def is_event(message):
    """Check if a message contains event data"""
    if message.embeds[0]:
        embed = message.embeds[0]
        return (message.channel.name == 'upcoming-events'
                and 'fields' in embed
                and 'name' in embed['fields'][0]
                and 'name' in embed['fields'][1]
                and 'name' in embed['fields'][2]
                and embed['fields'][0].get("name") == "Time"
                and embed['fields'][1].get("name") == "Accepted"
                and embed['fields'][2].get("name") == "Declined")

def is_admin(bot, ctx):
    """Check if the user had admin privileges"""
    if ctx.message.channel.is_private:
        with DBase() as db:
            rows = db.get_server(str(ctx.message.author))
            if rows and len(rows) == 1:
                pass #check perms
    else:
        if ctx.message.author.server_permissions.administrator:
            return True
