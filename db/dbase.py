import json

import MySQLdb


class DBase:

    with open('credentials.json') as f:
        credentials = json.load(f)
        dsn = (credentials["dbhost"], credentials["dbuser"],
               credentials["dbpass"], credentials["dbname"])

    def __init__(self):
        self.conn = MySQLdb.connect(*self.dsn)
        self.cur = self.conn.cursor()
        self.conn.set_character_set('utf8mb4')
        self.cur.execute('SET NAMES utf8mb4;')
        self.cur.execute('SET CHARACTER SET utf8mb4;')
        self.cur.execute('SET character_set_connection=utf8mb4;')

    def __enter__(self):
        return DBase()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_roster(self, guild_id):
        sql = """
              SELECT username, role, timezone
              FROM roster
              WHERE (role != '' OR timezone != '')
              AND guild_id = %s
              ORDER BY role;
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()

    def update_role(self, username, role, guild_id):
        sql = """
               INSERT INTO roster (username, role, guild_id)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE role = %s;
               """
        self.cur.execute(sql, (username, role, guild_id, role))
        self.conn.commit()

    def update_timezone(self, username, timezone, guild_id):
        sql = """
               INSERT INTO roster (username, timezone, guild_id)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE timezone = %s;
               """
        self.cur.execute(sql, (username, timezone, guild_id, timezone))
        self.conn.commit()

    def create_event(self, title, start_time, timezone, guild_id, description, max_members):
        sql = """
              INSERT INTO events (title, start_time, timezone, guild_id, description, max_members)
              VALUES (%s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE title = %s;
              """
        rows = self.cur.execute(sql, (title, start_time, timezone, guild_id, description, max_members, title))
        self.conn.commit()
        return rows

    def get_events(self, guild_id):
        sql = """
              SELECT title as e, description, start_time, timezone, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = e
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = e
                AND user_event.attending = 0)
                AS declined,
                max_members
              FROM events
              WHERE events.guild_id = %s
              GROUP BY title, description, start_time, timezone
              ORDER BY start_time DESC;
              """
        self.cur.execute(sql, (guild_id, guild_id, guild_id))
        return self.cur.fetchall()

    def update_attendance(self, username, guild_id, attending, title, last_updated):
        sql = """
              INSERT INTO user_event (username, guild_id, title, attending, last_updated)
              VALUES (%s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE attending = %s, last_updated = %s;
              """
        self.cur.execute(sql, (username, guild_id, title, attending, last_updated, attending, last_updated))
        self.conn.commit()

    def get_event(self, guild_id, title):
        sql = """
              SELECT title, description, start_time, timezone, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = %s
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = %s
                AND user_event.attending = 0)
                AS declined,
                max_members
              FROM events
              WHERE guild_id = %s
              AND title = %s;
              """
        self.cur.execute(sql, (guild_id, title, guild_id, title, guild_id, title))
        return self.cur.fetchall()

    def delete_event(self, guild_id, title):
        sql = """
              DELETE FROM events
              WHERE guild_id = %s
              AND title = %s;
              """
        affected_count = self.cur.execute(sql, (guild_id, title))
        self.conn.commit()
        if affected_count == 1:
            return True

    def add_guild(self, guild_id):
        sql = """
              INSERT INTO guilds (guild_id)
              VALUES (%s);
              """
        self.cur.execute(sql, (guild_id,))
        self.conn.commit()

    def remove_guild(self, guild_id):
        sql = """
              DELETE FROM guilds
              WHERE guild_id = %s;
              """
        self.cur.execute(sql, (guild_id,))
        self.conn.commit()

    def add_user(self, username):
        sql = """
              INSERT INTO users (username)
              VALUES (%s)
              ON DUPLICATE KEY UPDATE username = %s;
              """
        self.cur.execute(sql, (username, username))
        self.conn.commit()

    def remove_user(self, username):
        sql = """
              DELETE FROM users
              WHERE username = %s;
              """
        self.cur.execute(sql, (username,))
        self.conn.commit()

    def set_prefix(self, guild_id, prefix):
        sql = """
              UPDATE guilds
              SET prefix = %s
              WHERE guild_id = %s;
              """
        self.cur.execute(sql, (prefix, guild_id))
        self.conn.commit()

    def get_prefix(self, guild_id):
        sql = """
              SELECT prefix
              FROM guilds
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()[0][0]

    def get_cleanup(self, guild_id):
        sql = """
              SELECT clear_spam
              FROM guilds
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()[0][0]

    def toggle_cleanup(self, guild_id):
        sql = """
              UPDATE guilds
              SET clear_spam = !clear_spam
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        self.conn.commit()

    def update_registration(self, platform, membership_id, username):
        sql = """
              INSERT into users (platform, membership_id, username)
              VALUES (%s, %s, %s)
              ON DUPLICATE KEY UPDATE platform = %s, membership_id = %s
              """
        self.cur.execute(sql, (platform, membership_id, username, platform, membership_id))
        self.conn.commit()
