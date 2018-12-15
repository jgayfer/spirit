# Spirit

Spirit is a discord bot designed to assist Destiny 2 players with everything from clan management to keeping track of in game events.

Spirit is no longer actively hosted/maintained, but feel free to tweak and run the code yourself!

## Getting Started
Below are the steps to run the bot. Ideally you would be doing this for development/testing purposes,
as I would prefer it if you didn't run an instance of the bot; I'd much prefer you just add mine to
your server :)

### Prerequisites
To run the bot, you'll need the following:
- Python 3.5+
- Pip
- MySQL
- Redis Server (using the default port)
- [Pydest](https://www.github.com/jgayfer/pydest)
- [Spirit Server](https://www.github.com/jgayfer/spirit-server)
- Bungie.net API app

### Running the Bot

**Note:** Before the bot can be run, it's essential that both Pydest and the Spirit Server are installed and setup first.

Install the required Python modules with Pip, as well as the latest version of Discord.py
```
pip3 install -r requirements.txt
python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
```
Then create a MySQL database with support for UTF8mb4 encoding
```
mysql -u root -p
> create database <database_name> character set UTF8mb4 collate utf8mb4_bin
```
 Add the schema located at `db/schema.sql`
```
mysql -u root -p <database_name> < ./db/schema.sql
```

Finally, create a `credentials.json` file at the root level of this project.
```
{
  "token": "token",
  "dbname": "name",
  "dbhost": "host",
  "dbuser": "username",
  "dbpass": "password",
  "d2-api-key": "your-key",
  "client_id": "your-client-id"
}

```
That's it! The bot can now be run with
```
python3 spirit.py
```

If you play on using the `register` command, ensure that Spirit Server is also running.

## Built With
- [discord.py](https://github.com/Rapptz/discord.py) - An API wrapper for Discord written in Python
