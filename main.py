from discord.ext import commands
from database import DBase
import json
import discord

bot = commands.Bot(command_prefix='!')

@bot.command(pass_context=True)
async def role(ctx, role="None"):

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

            members = ""
            roles = ""

            for row in roster:
                members += row[0].split("#")[0] + "\n"
                roles += row[1] + "\n"

            embed_msg = discord.Embed(color=discord.Colour(3381759))
            embed_msg.add_field(name='Member', value=members, inline=True)
            embed_msg.add_field(name='Role', value=roles, inline=True)
            
            await bot.say(embed=embed_msg)

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
