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
                and embed['fields'][1].get("name").startswith("Accepted")
                and embed['fields'][2].get("name").startswith("Declined"))


def is_admin(user, channel):
    """Check if the user has admin privileges"""
    if channel.permissions_for(user).administrator:
        return True

def is_int(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b
