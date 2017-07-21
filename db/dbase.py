from utils.admin import load_credentials
import MySQLdb
import json

class DBase:

    credentials = load_credentials()
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
        sql = """SELECT username, role
                 FROM roles
                 WHERE roles.server_id = {0};
                 """.format(server_id)
        self.cur.execute(sql)
        return self.cur.fetchall()


    def update_roster(self, username, role, server_id):
        sql = []
        sql.append("""INSERT INTO users (username)
                      VALUES ('{0}')
                      ON DUPLICATE KEY UPDATE username = '{0}';
                      """.format(username))
        sql.append("""INSERT INTO roles (username, server_id, role)
                      VALUES ('{0}', '{1}', '{2}')
                      ON DUPLICATE KEY UPDATE role = '{2}';
                      """.format(username, server_id, role))
        for query in sql:
            self.cur.execute(query)
        self.conn.commit()


    def create_event(self, title, start_time, time_zone, server_id, description):
        sql = """INSERT INTO events (title, start_time, time_zone, server_id, description)
                 VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')
                 """.format(title, start_time, time_zone, server_id, description)
        self.cur.execute(sql)
        self.conn.commit()


    def get_events(self, server_id):
        sql = """SELECT events.event_id as e, title, description, start_time, time_zone, (
                   SELECT GROUP_CONCAT(DISTINCT username)
                   FROM user_event, events
                   WHERE user_event.event_id = e
                   AND events.server_id = {0}
                   AND user_event.attending = 1)
                   AS accepted, (
                   SELECT GROUP_CONCAT(DISTINCT username)
                   FROM user_event, events
                   WHERE user_event.event_id = e
                   AND events.server_id = {0}
                   AND user_event.attending = 0)
                   AS declined
                 FROM events
                 WHERE events.server_id = {0}
                 GROUP BY event_id, title, description, start_time, time_zone;
                 """.format(server_id)
        self.cur.execute(sql)
        return self.cur.fetchall()


    def update_attendance(self, username, event_id, attending):
        sql = []
        sql.append("""INSERT INTO users (username)
                      VALUES ('{0}')
                      ON DUPLICATE KEY UPDATE username = '{0}';
                      """.format(username))
        sql.append("""INSERT INTO user_event (username, event_id, attending)
                      VALUES ('{0}', '{1}', '{2}')
                      ON DUPLICATE KEY UPDATE attending = '{2}';
                      """.format(username, event_id, attending))
        for query in sql:
            self.cur.execute(query)
        self.conn.commit()


    def get_event(self, event_id):
        sql = """SELECT title, description, start_time, time_zone, (
                   SELECT GROUP_CONCAT(DISTINCT username)
                   FROM user_event
                   WHERE event_id = {0}
                   AND user_event.attending = 1)
                   AS accepted, (
                   SELECT GROUP_CONCAT(DISTINCT username)
                   FROM user_event
                   WHERE event_id = {0}
                   AND user_event.attending = 0)
                   AS declined
                 FROM events
                 WHERE event_id = {0};
                 """.format(event_id)
        self.cur.execute(sql)
        return self.cur.fetchall()


    def delete_event(self, event_id):
        sql = """DELETE FROM events
                 WHERE event_id = {0}
                 """.format(event_id)
        affected_count = self.cur.execute(sql)
        self.conn.commit()
        return affected_count
