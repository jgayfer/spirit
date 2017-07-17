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
        sql = '''SELECT a.username, a.role
                 FROM users a, user_server b, servers c
                 WHERE a.username = b.username
                 AND b.server_id = c.server_id
                 AND c.server_id = "{0}";'''.format(server_id)
        self.cur.execute(sql)
        if self.cur.rowcount != 0:
            return self.cur.fetchall()
        else:
            return False

    def update_roster(self, user, role, server_id):
        self.cur.execute("INSERT INTO roles VALUES('%s', '%s', '%s') ON DUPLICATE KEY UPDATE role='%s'" % (user, role, server_id, role))
        self.conn.commit()
