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
        sql = """SELECT a.username, a.role
                 FROM users a, user_server b, servers c
                 WHERE a.username = b.username
                 AND b.server_id = c.server_id
                 AND c.server_id = '{0}';
                 """.format(server_id)
        self.cur.execute(sql)
        return self.cur.fetchall()

    def update_roster(self, username, role, server_id, server_name):

        sql = []
        sql.append("""INSERT INTO users VALUES ('{0}', '{1}')
                      ON DUPLICATE KEY UPDATE role = '{1}';
                      """.format(username, role))
        sql.append("""INSERT INTO servers VALUES ('{0}', '{1}')
                      ON DUPLICATE KEY UPDATE server_id = '{0}';
                      """.format(server_id, server_name))
        sql.append("""INSERT INTO user_server VALUES ('{0}', '{1}')
                      ON DUPLICATE KEY UPDATE username = '{0}';
                      """.format(username, server_id))

        for query in sql:
            self.cur.execute(query)
        self.conn.commit()
