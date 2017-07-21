# Spirit

Spirit is a discord bot designed to assist Destiny 2 players with everything from clan management to keeping track of in game events.

To add Spirit to your server, click [here](https://discordapp.com/oauth2/authorize?client_id=335084645743984641&scope=bot&permissions=523344)!

## Running the Bot

First, install the following
- Python3 and Pip
- MySQL database

Next, install the required Python modules with Pip
```
pip3 install -r requirements.txt
```
Then create a MySQL database running with the schema located at `db/schema.sql`

Finally, create a `credentials.json` file at the root level of this project.
It will contain your bot's token, as well as your database user, password, host, and name.
It should look something like this!
```
{
  "token": "token",
  "dbname": "name",
  "dbhost": "host",
  "dbuser: "username",
  "dbpass" "password
}

```
That's it! The bot can be run with with
```
python3 spirit.py
```
