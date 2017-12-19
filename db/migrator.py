import re
import glob
import os
import sys


PATH_TO_MIGRATIONS = 'db/migrations'
MIGRATION_EXTENSION = 'sql'

class Migrator:

    def __init__(self, db):
        self.db = db


    def _add_all_migration_logs(self):
        for file_path in self._sorted_migration_paths():
            self.db.add_migration_log(os.path.basename(file_path))


    def _apply_and_log_migrations(self):
        migration_paths = self._migrations_to_apply()
        for file_path in migration_paths:
            sql = self._read_sql_from_file(file_path)
            self.db.execute_sql(sql)
            self.db.add_migration_log(os.path.basename(file_path))


    def _create_migrations_table(self):
        if not self.db.table_exists('migrations'):
            self.db.create_migrations_table()
            self._add_all_migration_logs()


    def _get_number(self, file_name):
        m = re.search('\d+', file_name)
        return int(m.group(0))


    def _get_last_executed_migration_id(self):
        res = self.db.get_last_executed_migration()
        if res:
            file_name = res.get('script_name')
            return self._get_number(file_name)
        else:
            return -1


    def _read_sql_from_file(self, file_path):
        sql_file = open(file_path, 'r')
        sql = sql_file.read()
        sql_file.close()
        return sql


    def _migrations_to_apply(self):
        migrations_to_apply = []
        last_executed_migration_id = self._get_last_executed_migration_id()

        for file_path in self._sorted_migration_paths():
            if self._get_number(os.path.basename(file_path)) > last_executed_migration_id:
                migrations_to_apply.append(file_path)

        return migrations_to_apply


    def migrate(self):
        self._create_migrations_table()
        self._apply_and_log_migrations()


    def _sorted_migration_paths(self):
        sortset = []
        sorted_migrations = []
        filemap = {}

        for file_path in glob.glob(os.path.join(PATH_TO_MIGRATIONS, '*.%s' % MIGRATION_EXTENSION)):
            migration_id = self._get_number(os.path.basename(file_path))
            sortset.append(migration_id)
            filemap[migration_id] = file_path

        sortset.sort()
        for key in sortset:
            sorted_migrations.append(filemap[key])

        return sorted_migrations
