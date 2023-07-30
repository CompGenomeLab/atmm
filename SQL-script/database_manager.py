from database import Database
from utils import hash_seq, file_reader
import os
import json


class SequenceDatabaseManager:
    def __init__(self, db, args):
        self.db = db
        self.args = args
        self.working_dir = os.path.dirname(self.args.filepath)
        self.md5sum_sequence_file_path = os.path.join(self.working_dir, 'sequence_md5sum.tsv')
        self.md5sum_score_json_file_path = os.path.join(self.working_dir, 'md5sum_score_json.tsv')

    def _prepare_files(self):
        with open(self.md5sum_sequence_file_path, mode='w') as f, open(self.md5sum_score_json_file_path, mode='w') as m:
            f.write('md5sum\tsequence\n')
            m.write('md5sum\tscores\n')
            ct = 0
            for row in file_reader(self.args.filepath):
                if self.args.header and ct == 0:
                    ct += 1
                    continue
                sp = row.split('\t')
                try:
                    score_json = json.loads(sp[1])
                except json.decoder.JSONDecodeError:
                    raise (ValueError, f'Invalid JSON in line {ct}')

                f.write(f'{hash_seq(sp[0])}\t{sp[0]}\n')
                print(hash_seq(sp[0]), json.dumps(score_json), sep="\t", file=m)

    def _create_temp_table(self, columns):
        columns = ', '.join([f'"{col}"' for col in columns.split(', ')])
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
        self.create_main_table()
        self._update_md5sum_table()
        self.db.copy_from_file_json(self.md5sum_score_json_file_path, self.args.table_name)

    def create_main_table(self):
        create_main_table = f'''CREATE TABLE {self.args.table_name} (
                                md5sum TEXT NOT NULL,
                                scores JSONb not null,
                                CONSTRAINT {self.args.table_name}_pkey PRIMARY KEY (md5sum));'''
        self.db.execute_query(create_main_table)

    def _update_md5sum_table(self):
        self._create_temp_table('md5sum TEXT NOT NULL, sequence TEXT NOT NULL')
        self.db.copy_from_file(self.md5sum_sequence_file_path, 'temp')
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        self.db.execute_query(insert_query)
        self._drop_temp_table()


class UpdateTable(SequenceDatabaseManager):
    def execute(self, force_update=False):
        self._prepare_files()
        if self.args.table_name not in self.db.currently_existing_tables():
            os.remove('sequence_md5sum.tsv')
            os.remove('score_md5sum.tsv')
            raise Database.TableNotFound
        else:
            self._update_md5sum_table()
            self._update_data_table(force_update)

    def _update_md5sum_table(self):
        self._create_temp_table('md5sum TEXT NOT NULL, sequence TEXT NOT NULL')
        self.db.copy_from_file(self.md5sum_sequence_file_path, 'temp')
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        self.db.execute_query(insert_query)
        self._drop_temp_table()

    def _update_data_table(self, force_update=False):
        self._create_temp_table('md5sum TEXT NOT NULL, scores JSONb not null')
        self.db.copy_from_file(self.md5sum_score_json_file_path, 'temp')

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
    def execute(self, force_update=False):
        super().execute(force_update=True)
