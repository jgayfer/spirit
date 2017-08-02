# Spirit

Spirit is a discord bot designed to assist Destiny 2 players with everything from clan management to keeping track of in game events.

To add Spirit to your server, click [here](https://discordapp.com/oauth2/authorize?client_id=335084645743984641&scope=bot&permissions=523344)!

## Getting Started
Below are the steps to run the bot. Ideally you would be doing this for development/testing purposes,
as I would prefer it if you didn't run an instance of the bot; I'd much prefer you just add mine to
your server :)

### Prerequisites
To run the bot, you'll need the following:
- Python3
- Pip
- MySQL

### Running the Bot
Install the required Python modules with Pip
```
pip3 install -r requirements.txt
```
Then create a MySQL database and add the schema located at `db/schema.sql`
```
mysql -u root -p
> create database Spirit;
> exit
mysql -u root -p Spirit < ./db/schema.sql
```

Finally, create a `credentials.json` file at the root level of this project.
It will contain your bot's token as well as your database user, password, host, and name.
```
{
  "token": "token",
  "dbname": "name",
  "dbhost": "host",
  "dbuser": "username",
  "dbpass": "password"
}

```
That's it! The bot can now be run with with
```
python3 spirit.py
```

## Built With
- [discord.py](https://github.com/Rapptz/discord.py) - An API wrapper for Discord written in Python
