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

async def is_admin(bot, ctx):
    """Check if the user has admin privileges"""
    if ctx.message.channel.is_private:
        print("private")
        with DBase() as db:
            user = ctx.message.author
            rows = db.get_server(str(user))
            if rows and len(rows) == 1:
                print(rows)
                server_id = rows[0][0]
                server = await bot.get_server(server_id)
                permissions = server.default_channel.permissions_for(user)
    else:
        if ctx.message.author.server_permissions.administrator:
            return True
