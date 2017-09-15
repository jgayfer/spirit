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
              SELECT user_id, role, timezone
              FROM roster
              WHERE (role != '' OR timezone != '')
              AND guild_id = %s
              ORDER BY role;
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()

    def update_role(self, user_id, role, guild_id):
        sql = """
               INSERT INTO roster (user_id, role, guild_id)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE role = %s;
               """
        affected_count = self.cur.execute(sql, (user_id, role, guild_id, role))
        self.conn.commit()
        return affected_count

    def update_timezone(self, user_id, timezone, guild_id):
        sql = """
               INSERT INTO roster (user_id, timezone, guild_id)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE timezone = %s;
               """
        affected_count = self.cur.execute(sql, (user_id, timezone, guild_id, timezone))
        self.conn.commit()
        return affected_count

    def create_event(self, title, start_time, timezone, guild_id, description, max_members, user_id):
        sql = """
              INSERT INTO events (title, start_time, timezone, guild_id, description, max_members, user_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE title = %s;
              """
        affected_count = self.cur.execute(sql, (title, start_time, timezone, guild_id, description, max_members, user_id, title))
        self.conn.commit()
        return affected_count

    def get_events(self, guild_id):
        sql = """
              SELECT title as e, description, start_time, timezone, user_id, (
                SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = e
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
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

    def update_attendance(self, user_id, guild_id, attending, title, last_updated):
        sql = """
              INSERT INTO user_event (user_id, guild_id, title, attending, last_updated)
              VALUES (%s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE attending = %s, last_updated = %s;
              """
        affected_count = self.cur.execute(sql, (user_id, guild_id, title, attending, last_updated, attending, last_updated))
        self.conn.commit()
        return affected_count

    def get_event(self, guild_id, title):
        sql = """
              SELECT title, description, start_time, timezone, user_id, (
                SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
                FROM user_event
                WHERE user_event.guild_id = %s
                AND user_event.title = %s
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
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
        return affected_count

    def get_event_creator(self, guild_id, title):
        sql = """
              SELECT user_id
              FROM events
              WHERE guild_id = %s
              AND title = %s;
              """
        self.cur.execute(sql, (guild_id, title))
        return self.cur.fetchall()

    def add_guild(self, guild_id):
        sql = """
              INSERT INTO guilds (guild_id)
              VALUES (%s)
              ON DUPLICATE KEY UPDATE guild_id = %s;
              """
        affected_count = self.cur.execute(sql, (guild_id, guild_id))
        self.conn.commit()
        return affected_count

    def remove_guild(self, guild_id):
        sql = """
              DELETE FROM guilds
              WHERE guild_id = %s;
              """
        affected_count = self.cur.execute(sql, (guild_id,))
        self.conn.commit()
        return affected_count

    def get_guilds(self):
        sql = """
              SELECT * FROM guilds;
              """
        self.cur.execute(sql)
        return self.cur.fetchall()

    def add_user(self, user_id):
        sql = """
              INSERT INTO users (user_id)
              VALUES (%s)
              ON DUPLICATE KEY UPDATE user_id = %s;
              """
        affected_count = self.cur.execute(sql, (user_id, user_id))
        self.conn.commit()
        return affected_count

    def remove_user(self, user_id):
        sql = """
              DELETE FROM users
              WHERE user_id = %s;
              """
        affected_count = self.cur.execute(sql, (user_id,))
        self.conn.commit()
        return affected_count

    def get_d2_info(self, user_id):
        sql = """
              SELECT platform, membership_id
              FROM users
              WHERE user_id = %s
              """
        self.cur.execute(sql, (user_id,))
        return self.cur.fetchall()

    def set_prefix(self, guild_id, prefix):
        sql = """
              UPDATE guilds
              SET prefix = %s
              WHERE guild_id = %s;
              """
        affected_count = self.cur.execute(sql, (prefix, guild_id))
        self.conn.commit()
        return affected_count

    def get_prefix(self, guild_id):
        sql = """
              SELECT prefix
              FROM guilds
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()

    def set_event_role_id(self, guild_id, event_role_id):
        sql = """
              UPDATE guilds
              SET event_role_id = %s
              WHERE guild_id = %s;
              """
        affected_count = self.cur.execute(sql, (event_role_id, guild_id))
        self.conn.commit()
        return affected_count

    def get_event_role_id(self, guild_id):
        sql = """
              SELECT event_role_id
              FROM guilds
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()

    def get_cleanup(self, guild_id):
        sql = """
              SELECT clear_spam
              FROM guilds
              WHERE guild_id = %s
              """
        self.cur.execute(sql, (guild_id,))
        return self.cur.fetchall()

    def toggle_cleanup(self, guild_id):
        sql = """
              UPDATE guilds
              SET clear_spam = !clear_spam
              WHERE guild_id = %s
              """
        affected_count = self.cur.execute(sql, (guild_id,))
        self.conn.commit()
        return affected_count

    def update_registration(self, platform, membership_id, user_id):
        sql = """
              INSERT into users (platform, membership_id, user_id)
              VALUES (%s, %s, %s)
              ON DUPLICATE KEY UPDATE platform = %s, membership_id = %s
              """
        affected_count = self.cur.execute(sql, (platform, membership_id, user_id, platform, membership_id))
        self.conn.commit()
        return affected_count





    def get_all_users(self):
        sql = """SELECT * FROM users;"""
        self.cur.execute(sql)
        return self.cur.fetchall()

    def update_tables(self):
        sql = """ALTER TABLE users ADD COLUMN user_id BIGINT NOT NULL;"""
        self.cur.execute(sql)
        sql = """ALTER TABLE user_event ADD COLUMN user_id BIGINT NOT NULL;"""
        self.cur.execute(sql)
        sql = """ALTER TABLE roster ADD COLUMN user_id BIGINT NOT NULL;"""
        self.cur.execute(sql)
        self.conn.commit()

    def add_id_user(self, username, user_id):
        sql = """UPDATE users SET user_id = %s WHERE username = %s"""
        affected_count = self.cur.execute(sql, (user_id, username))
        self.conn.commit()
        return affected_count

    def add_id_user_event(self, username, user_id):
        sql = """UPDATE user_event SET user_id = %s WHERE username = %s"""
        affected_count = self.cur.execute(sql, (user_id, username))
        self.conn.commit()
        return affected_count

    def add_id_roster(self, username, user_id):
        sql = """UPDATE roster SET user_id = %s WHERE username = %s"""
        affected_count = self.cur.execute(sql, (user_id, username))
        self.conn.commit()
        return affected_count
