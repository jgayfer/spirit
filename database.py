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
