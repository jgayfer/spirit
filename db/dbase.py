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

    def get_roster(self, server_id):
        sql = """
              SELECT username, role
              FROM users
              WHERE role != ''
              AND server_id = %s
              ORDER BY role;
              """
        self.cur.execute(sql, (server_id,))
        return self.cur.fetchall()

    def update_roster(self, username, role, server_id):
        sql = """
               UPDATE users
               SET role = %s
               WHERE username = %s
               AND server_id = %s;
               """
        self.cur.execute(sql, (role, username, server_id))
        self.conn.commit()

    def create_event(self, title, start_time, time_zone, server_id, description):
        sql = """
              INSERT INTO events (title, start_time, time_zone, server_id, description)
              VALUES (%s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE title = %s;
              """
        rows = self.cur.execute(sql, (title, start_time, time_zone, server_id, description, title))
        self.conn.commit()
        return rows

    def get_events(self, server_id):
        sql = """
              SELECT title as e, description, start_time, time_zone, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.server_id = %s
                AND user_event.title = e
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.server_id = %s
                AND user_event.title = e
                AND user_event.attending = 0)
                AS declined
              FROM events
              WHERE events.server_id = %s
              GROUP BY title, description, start_time, time_zone
              ORDER BY start_time DESC;
              """
        self.cur.execute(sql, (server_id, server_id, server_id))
        return self.cur.fetchall()

    def update_attendance(self, username, server_id, attending, title, last_updated):
        sql = """
              INSERT INTO user_event (username, server_id, title, attending, last_updated)
              VALUES (%s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE attending = %s, last_updated = %s;
              """
        self.cur.execute(sql, (username, server_id, title, attending, last_updated, attending, last_updated))
        self.conn.commit()

    def get_event(self, server_id, title):
        sql = """
              SELECT title, description, start_time, time_zone, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.server_id = %s
                AND user_event.title = %s
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username ORDER BY last_updated)
                FROM user_event
                WHERE user_event.server_id = %s
                AND user_event.title = %s
                AND user_event.attending = 0)
                AS declined
              FROM events
              WHERE server_id = %s
              AND title = %s;
              """
        self.cur.execute(sql, (server_id, title, server_id, title, server_id, title))
        return self.cur.fetchall()

    def delete_event(self, server_id, title):
        sql = """
              DELETE FROM events
              WHERE server_id = %s
              AND title = %s;
              """
        affected_count = self.cur.execute(sql, (server_id, title))
        self.conn.commit()
        if affected_count == 1:
            return True

    def add_server(self, server_id):
        sql = """
              INSERT INTO servers (server_id)
              VALUES (%s);
              """
        self.cur.execute(sql, (server_id,))
        self.conn.commit()

    def remove_server(self, server_id):
        sql = """
              DELETE FROM servers
              WHERE server_id = %s;
              """
        self.cur.execute(sql, (server_id,))
        self.conn.commit()

    def get_server(self, username):
        sql = """
              SELECT server_id
              FROM users
              WHERE username = %s;
              """
        self.cur.execute(sql, (username,))
        return self.cur.fetchall()

    def add_user(self, server_id, username):
        sql = """
              INSERT INTO users (server_id, username)
              VALUES (%s, %s)
              ON DUPLICATE KEY UPDATE username = %s;
              """
        self.cur.execute(sql, (server_id, username, username))
        self.conn.commit()

    def set_prefix(self, server_id, prefix):
        sql = """
              UPDATE servers
              SET prefix = %s
              WHERE server_id = %s;
              """
        self.cur.execute(sql, (prefix, server_id))
        self.conn.commit()

    def get_prefix(self, server_id):
        sql = """
              SELECT prefix
              FROM servers
              WHERE server_id = %s
              """
        self.cur.execute(sql, (server_id,))
        return self.cur.fetchall()[0][0]
