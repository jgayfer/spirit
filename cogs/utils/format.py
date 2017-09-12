def format_role_name(role):
    if role.name.startswith('@'):
        return role.name[1:]
    else:
        return role.name
