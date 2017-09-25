import json
import pymysql.cursors

class DBase:

    def __init__(self, credentials_file):
        with open(credentials_file) as f:
            credentials = json.load(f)
        info = (credentials["dbhost"], credentials["dbuser"],
                credentials["dbpass"], credentials["dbname"])

        self.connection = pymysql.connect(host=info[0],
                                          user=info[1],
                                          password=info[2],
                                          db=info[3],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)


    def add_guild(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT INTO guilds (guild_id)
                  VALUES (%s)
                  ON DUPLICATE KEY UPDATE guild_id = %s;
                  """
            affected_count = cursor.execute(sql, (guild_id, guild_id))
        self.connection.commit()
        return affected_count


    def add_user(self, user_id):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT INTO users (user_id)
                  VALUES (%s)
                  ON DUPLICATE KEY UPDATE user_id = %s;
                  """
            affected_count = cursor.execute(sql, (user_id, user_id))
        self.connection.commit()
        return affected_count


    def create_event(self, title, start_time, timezone, guild_id, description, max_members, user_id):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT INTO events (title, start_time, timezone, guild_id, description, max_members, user_id)
                  VALUES (%s, %s, %s, %s, %s, %s, %s)
                  ON DUPLICATE KEY UPDATE title = %s;
                  """
            affected_count = cursor.execute(sql, (title, start_time, timezone, guild_id, description, max_members, user_id, title))
        self.connection.commit()
        return affected_count


    def delete_event(self, guild_id, title):
        with self.connection.cursor() as cursor:
            sql = """
                  DELETE FROM events
                  WHERE guild_id = %s
                  AND title = %s;
                  """
            affected_count = cursor.execute(sql, (guild_id, title))
        self.connection.commit()
        return affected_count


    def get_cleanup(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT clear_spam
                  FROM guilds
                  WHERE guild_id = %s
                  """
            cursor.execute(sql, (guild_id,))
            result = cursor.fetchone()
        return result


    def get_d2_info(self, user_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT platform, membership_id
                  FROM users
                  WHERE user_id = %s
                  """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
        return result


    def get_event(self, guild_id, title):
        with self.connection.cursor() as cursor:
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
            cursor.execute(sql, (guild_id, title, guild_id, title, guild_id, title))
            result = cursor.fetchone()
        return result


    def get_event_creator(self, guild_id, title):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT user_id
                  FROM events
                  WHERE guild_id = %s
                  AND title = %s;
                  """
            cursor.execute(sql, (guild_id, title))
            result = cursor.fetchone()
        return result


    def get_event_delete_role_id(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT event_delete_role_id
                  FROM guilds
                  WHERE guild_id = %s
                  """
            cursor.execute(sql, (guild_id,))
            result = cursor.fetchone()
        return result


    def get_event_role_id(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT event_role_id
                  FROM guilds
                  WHERE guild_id = %s
                  """
            cursor.execute(sql, (guild_id,))
            result = cursor.fetchone()
        return result


    def get_events(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT title as title, description, start_time, timezone, user_id, (
                    SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
                    FROM user_event
                    WHERE user_event.guild_id = %s
                    AND user_event.title = title
                    AND user_event.attending = 1)
                    AS accepted, (
                    SELECT GROUP_CONCAT(DISTINCT user_id ORDER BY last_updated)
                    FROM user_event
                    WHERE user_event.guild_id = %s
                    AND user_event.title = title
                    AND user_event.attending = 0)
                    AS declined,
                    max_members
                  FROM events
                  WHERE events.guild_id = %s
                  GROUP BY title, description, start_time, timezone
                  ORDER BY start_time DESC;
                  """
            cursor.execute(sql, (guild_id, guild_id, guild_id))
            result = cursor.fetchall()
        return result


    def get_guilds(self):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT * FROM guilds;
                  """
            cursor.execute(sql)
            result = cursor.fetchall()
        return result


    def get_prefix(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT prefix
                  FROM guilds
                  WHERE guild_id = %s;
                  """
            cursor.execute(sql, (guild_id,))
            result = cursor.fetchone()
        return result


    def get_roster(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  SELECT user_id, role, timezone
                  FROM roster
                  WHERE (role != '' OR timezone != '')
                  AND guild_id = %s
                  ORDER BY role;
                  """
            cursor.execute(sql, (guild_id,))
            result = cursor.fetchall()
        return result


    def remove_guild(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  DELETE FROM guilds
                  WHERE guild_id = %s;
                  """
            affected_count = cursor.execute(sql, (guild_id,))
        self.connection.commit()
        return affected_count


    def remove_user(self, user_id):
        with self.connection.cursor() as cursor:
            sql = """
                  DELETE FROM users
                  WHERE user_id = %s;
                  """
            affected_count = cursor.execute(sql, (user_id,))
        self.connection.commit()
        return affected_count


    def set_event_delete_role_id(self, guild_id, event_delete_role_id):
        with self.connection.cursor() as cursor:
            sql = """
                  UPDATE guilds
                  SET event_delete_role_id = %s
                  WHERE guild_id = %s;
                  """
            affected_count = cursor.execute(sql, (event_delete_role_id, guild_id))
        self.connection.commit()
        return affected_count


    def set_event_role_id(self, guild_id, event_role_id):
        with self.connection.cursor() as cursor:
            sql = """
                  UPDATE guilds
                  SET event_role_id = %s
                  WHERE guild_id = %s;
                  """
            affected_count = cursor.execute(sql, (event_role_id, guild_id))
        self.connection.commit()
        return affected_count


    def set_prefix(self, guild_id, prefix):
        with self.connection.cursor() as cursor:
            sql = """
                  UPDATE guilds
                  SET prefix = %s
                  WHERE guild_id = %s;
                  """
            affected_count = cursor.execute(sql, (prefix, guild_id))
        self.connection.commit()
        return affected_count


    def toggle_cleanup(self, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                  UPDATE guilds
                  SET clear_spam = !clear_spam
                  WHERE guild_id = %s
                  """
            affected_count = cursor.execute(sql, (guild_id,))
        self.connection.commit()
        return affected_count


    def update_attendance(self, user_id, guild_id, attending, title, last_updated):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT INTO user_event (user_id, guild_id, title, attending, last_updated)
                  VALUES (%s, %s, %s, %s, %s)
                  ON DUPLICATE KEY UPDATE attending = %s, last_updated = %s;
                  """
            affected_count = cursor.execute(sql, (user_id, guild_id, title, attending, last_updated, attending, last_updated))
        self.connection.commit()
        return affected_count


    def update_role(self, user_id, role, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                   INSERT INTO roster (user_id, role, guild_id)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE role = %s;
                   """
            affected_count = cursor.execute(sql, (user_id, role, guild_id, role))
        self.connection.commit()
        return affected_count


    def update_registration(self, platform, membership_id, user_id):
        with self.connection.cursor() as cursor:
            sql = """
                  INSERT into users (platform, membership_id, user_id)
                  VALUES (%s, %s, %s)
                  ON DUPLICATE KEY UPDATE platform = %s, membership_id = %s
                  """
            affected_count = cursor.execute(sql, (platform, membership_id, user_id, platform, membership_id))
        self.connection.commit()
        return affected_count


    def update_timezone(self, user_id, timezone, guild_id):
        with self.connection.cursor() as cursor:
            sql = """
                   INSERT INTO roster (user_id, timezone, guild_id)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE timezone = %s;
                   """
            affected_count = cursor.execute(sql, (user_id, timezone, guild_id, timezone))
        self.connection.commit()
        return affected_count
