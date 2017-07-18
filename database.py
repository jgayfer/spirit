import MySQLdb

class DBase:

    dsn = ("localhost","root","0perator","Spirit")

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
        sql = """SELECT user_event.event_id, title, description, start_time, time_zone, (
                   SELECT GROUP_CONCAT(username)
                   FROM user_event
                   WHERE user_event.event_id = event_id
                   AND user_event.attending = 1)
                   AS accepted, (
                   SELECT GROUP_CONCAT(username)
                   FROM user_event
                   WHERE user_event.event_id = event_id
                   AND user_event.attending = 0)
                   AS declined
                 FROM user_event, events
                 WHERE events.server_id = {0}
                 GROUP BY event_id, title, description, start_time, time_zone;
                 """.format(server_id)
        self.cur.execute(sql)
        return self.cur.fetchall()
