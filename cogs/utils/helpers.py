from cogs.utils import constants


async def get_membership_details(bot, ctx, username, platform):
    """Get the platform_id, membership_id, and display name for a user

       Note that platform and username can be None, in which case the credentials
       for the user in the database are used"""

    # User wants credentials for a Guardian who is registered with Spirit
    if username and ctx.message.mentions:

        user_id = ctx.message.mentions[0].id
        info = bot.db.get_d2_info(user_id)

        if info:

            # If platform wasn't given, use the preferred platform
            if not platform:
                platform_id = info.get('platform')

            # Otherwise, use the platform provided by the user (assuming it's valid)
            else:
                if platform not in constants.PLATFORMS.keys():
                    return "Platform must be one of `bnet`, `xbox`, or `ps`"
                platform_id = constants.PLATFORMS.get(platform)

            if platform_id == 4:
                membership_id = info.get('bliz_id')
                display_name = info.get('bliz_name')
            elif platform_id == 1:
                membership_id = info.get('xbox_id')
                display_name = info.get('xbox_name')
            elif platform_id == 2:
                membership_id = info.get('psn_id')
                display_name = info.get('psn_name')

            if not membership_id:
                return "Oops, that user doesn't have a connected account of that type"

        else:
            return ("That user hasn't registered with me yet. They can do so "
                  + "with the `{}register` command.".format(ctx.prefix))


    # User wants credentials for a Guardian who has NOT registered with Spirit
    elif username and not ctx.message.mentions:

        if platform not in constants.PLATFORMS.keys():
            return "Platform must be one of `bnet`, `xbox`, or `ps`"

        platform_id = constants.PLATFORMS.get(platform)
        display_name = username

        # Try and fetch account data from Bungie.net
        try:
            res = await bot.destiny.api.search_destiny_player(platform_id, username)
        except pydest.PydestException as e:
            return "I can't seem to connect to Bungie right now. Try again later."

        if res['ErrorCode'] != 1:
            return "I can't seem to connect to Bungie right now. Try again later."

        # Get a single membership ID for the given credentials (if one exists)
        membership_id = None
        if len(res['Response']) == 1:
            membership_id = res['Response'][0]['membershipId']
        elif len(res['Response']) > 1:
            for entry in res['Response']:
                if username == entry['displayName']:
                    membership_id = entry['membershipId']
                    break

        if not membership_id:
            return "Sorry, I couldn't find the Guardian you're looking for."

    # User wants credentials for their own Guardian
    else:
        info = bot.db.get_d2_info(ctx.author.id)
        if info:

            # If platform wasn't given, use the user's preferred platform
            if not platform:
                platform_id = info.get('platform')

            # Otherwise, use the platform provided by the user (assuming it's valid)
            else:
                if platform not in constants.PLATFORMS.keys():
                    return "Platform must be one of `bnet`, `xbox`, or `ps`"
                platform_id = constants.PLATFORMS.get(platform)

            if platform_id == 4:
                membership_id = info.get('bliz_id')
                display_name = info.get('bliz_name')
            elif platform_id == 1:
                membership_id = info.get('xbox_id')
                display_name = info.get('xbox_name')
            elif platform_id == 2:
                membership_id = info.get('psn_id')
                display_name = info.get('psn_name')

            if not membership_id:
                return "Oops, you don't have a connected account of that type."

        else:
            return ("You must first register your Destiny 2 account with the "
                  + "`{}register` command.".format(ctx.prefix))

    return platform_id, membership_id, display_name
