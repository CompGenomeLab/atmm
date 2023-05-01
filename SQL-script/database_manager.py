from database import Database
from utils import hash_seq, file_reader
import os


class SequenceDatabaseManager:
    def __init__(self, db, args):
        self.db = db
        self.args = args

    def _prepare_files(self):
        with open('sequence_md5sum.tsv', mode='w') as f, open('md5sum_score_json.tsv', mode='w') as m:
            f.write('md5sum\tsequence\n')
            m.write('md5sum\tscores\n')
            ct = 0
            for row in file_reader(self.args.filepath):
                if self.args.header and ct == 0:
                    ct += 1
                    continue
                sp = row.split('\t')
                f.write(f'{hash_seq(sp[0])}\t{sp[0]}\n')
                m.write(f'{hash_seq(sp[0])}\t{sp[1]}\n')

    def _create_temp_table(self, columns):
        create_temp_table = f'''CREATE TABLE temp ({columns});'''
        self.db.execute_query(create_temp_table)

    def _drop_temp_table(self):
        drop_table = '''DROP TABLE temp;'''
        self.db.execute_query(drop_table)


class AddTable(SequenceDatabaseManager):
    def execute(self):
        self._prepare_files()
        if self.args.table_name in self.db.get_tables():
            raise Database.TableAlreadyExists
        self._prepare_files()
        self.create_main_table()
        self._update_md5sum_table()
        self.db.copy_from_file('md5sum_score_json.tsv', self.args.table_name, header=True)

    def create_main_table(self):
        create_main_table = f'''CREATE TABLE {self.args.table_name} (
                                md5sum TEXT NOT NULL,
                                scores JSONb not null,
                                CONSTRAINT {self.args.table_name}_pkey PRIMARY KEY (md5sum));'''
        self.db.execute_query(create_main_table)

    def _update_md5sum_table(self):
        self._create_temp_table('md5sum TEXT NOT NULL, sequence TEXT NOT NULL')
        self.db.copy_from_file('sequence_md5sum.tsv', 'temp', header=True)
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        self.db.execute_query(insert_query)
        self._drop_temp_table()


class UpdateTable(SequenceDatabaseManager):
    def execute(self, force_update=False):
        if self.args.table_name not in self.db.currently_existing_tables():
            os.remove('sequence_md5sum.tsv')
            os.remove('score_md5sum.tsv')
            raise Database.TableNotFound
        else:
            self._prepare_files()
            self._update_md5sum_table()
            self._update_data_table(force_update)

    def _update_md5sum_table(self):
        self._create_temp_table('md5sum TEXT NOT NULL, sequence TEXT NOT NULL')
        self.db.copy_from_file('sequence_md5sum.tsv', 'temp', header=True)
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        self.db.execute_query(insert_query)
        self._drop_temp_table()

    def _update_data_table(self, force_update=False):
        self._create_temp_table('md5sum TEXT NOT NULL, scores JSONb not null')
        self.db.copy_from_file('score_md5sum.tsv', 'temp', header=True)

        if force_update:
            insert_data = f'''insert into {self.args.table_name}(
                md5sum, scores)
                select distinct * from temp
                on conflict (md5sum) do update set scores = EXCLUDED.scores;'''
        else:
            insert_data = f'''insert into {self.args.table_name}(md5sum, scores)
                              select distinct * from temp
                              on conflict (md5sum) do nothing;'''

        self.db.execute_query(insert_data)
        self._drop_temp_table()


class ForceUpdateTable(UpdateTable):
    def execute(self):
        super().execute(force_update=True)
