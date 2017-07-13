from discord.ext import commands
from database import DBase
import json

bot = commands.Bot(command_prefix='!')

@bot.command(pass_context=True)
async def role(ctx, role):
    user = str(ctx.message.author)
    role = role.lower().title()
    if role == "Titan" or role == "Warlock" or role == "Hunter":
        with DBase() as db:
            db.update_roster(user, role)
        await bot.say(ctx.message.author.mention + ": Your role has been updated!")
    else:
        await bot.say(ctx.message.author.mention + ": Oops! Role must be one of: Titan, Hunter, Warlock")

@bot.command()
async def roster():
    with DBase() as db:
        roster = db.get_roster()
        if roster:
            message = ""
            for row in roster:
                message += ("%s - %s\n" % (row[0],row[1]))
            await bot.say(message)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials['token']
    bot.run(token)
