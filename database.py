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

    def get_roster(self, server_id)
        self.cur.execute("SELECT * FROM roster where server_id='%s'" % server_id)
        return self.cur.fetchall()

    def update_roster(self, user, role, server_id):
        self.cur.execute("INSERT INTO roster VALUES('%s', '%s', '%s) ON DUPLICATE KEY UPDATE class='%s'" % (user, role, server_id, role))
        self.conn.commit()
