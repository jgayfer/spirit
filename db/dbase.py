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

    def __enter__(self):
        return DBase()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_roster(self, server_id):
        sql = """
              SELECT username, role
              FROM roles
              WHERE roles.server_id = %s
              ORDER BY role;
              """
        self.cur.execute(sql, (server_id,))
        return self.cur.fetchall()

    def update_roster(self, username, role, server_id):
        sql1 = """
               INSERT INTO users (username)
               VALUES (%s)
               ON DUPLICATE KEY UPDATE username = %s;
               """
        sql2 = """
               INSERT INTO roles (username, server_id, role)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE role = %s;
               """
        self.cur.execute(sql1, (username, username))
        self.cur.execute(sql2, (username, server_id, role, role))
        self.conn.commit()

    def create_event(self, title, start_time, time_zone, server_id, description):
        sql = """
              INSERT INTO events (title, start_time, time_zone, server_id, description)
              VALUES (%s, %s, %s, %s, %s);
              """
        self.cur.execute(sql, (title, start_time, time_zone, server_id, description))
        self.conn.commit()

    def get_events(self, server_id):
        sql = """
              SELECT events.event_id as e, title, description, start_time, time_zone, (
                SELECT GROUP_CONCAT(DISTINCT username)
                FROM user_event, events
                WHERE user_event.event_id = e
                AND events.server_id = %s
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username)
                FROM user_event, events
                WHERE user_event.event_id = e
                AND events.server_id = %s
                AND user_event.attending = 0)
                AS declined
              FROM events
              WHERE events.server_id = %s
              GROUP BY event_id, title, description, start_time, time_zone;
              """
        self.cur.execute(sql, (server_id, server_id, server_id))
        return self.cur.fetchall()

    def update_attendance(self, username, event_id, attending):
        sql1 = """
               INSERT INTO users (username)
               VALUES (%s)
               ON DUPLICATE KEY UPDATE username = %s;
               """
        sql2 = """
               INSERT INTO user_event (username, event_id, attending)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE attending = %s;
               """
        self.cur.execute(sql1, (username, username))
        self.cur.execute(sql2, (username, event_id, attending, attending))
        self.conn.commit()

    def get_event(self, event_id):
        sql = """
              SELECT title, description, start_time, time_zone, (
                SELECT GROUP_CONCAT(DISTINCT username)
                FROM user_event
                WHERE event_id = %s
                AND user_event.attending = 1)
                AS accepted, (
                SELECT GROUP_CONCAT(DISTINCT username)
                FROM user_event
                WHERE event_id = %s
                AND user_event.attending = 0)
                AS declined
              FROM events
              WHERE event_id = %s;
              """
        self.cur.execute(sql, (event_id, event_id, event_id))
        return self.cur.fetchall()

    def delete_event(self, event_id):
        sql = """
              DELETE FROM events
              WHERE event_id = %s;
              """
        affected_count = self.cur.execute(sql, (event_id,))
        self.conn.commit()
        return affected_count

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
