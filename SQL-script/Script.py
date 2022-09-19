import hashlib
import psycopg2
from psycopg2 import Error
import os
import argparse


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


def file_reader(file_name):
    for row in open(file_name, "r"):
        yield row.split('\n')[0]


class Database:
    def __init__(self, username, password, database):
        self.username = username
        self.password = password
        self.database = database
        try:
            self.connection = psycopg2.connect(user=f"{self.username}",
                                               password=f"{self.password}",
                                               host="localhost",
                                               database=f"{self.database}")
            self.cursor = self.connection.cursor()

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def currently_existing_tables(self):
        self.cursor.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema = 'public'""")

        table_names = []
        for table in self.cursor.fetchall():
            table_names.append(table[0])
        return table_names

    def query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query is executed")
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        print("PostgreSQL connection is closed")

    class TableAlreadyExists(Exception):
        def __init__(self, message='The table you want to create is already exists'):
            self.message = message

        def __str__(self):
            return self.message

    class TableCannotBeFound(Exception):
        def __init__(self, message='The table you want to update cannot be found'):
            self.message = message

        def __str__(self):
            return self.message


parser = argparse.ArgumentParser(description='Add tsv sequence-score file to the sql database')
parser.add_argument('--filepath', '-fp', type=str, help='full path of the expected tsv file with two columns: sequence and score', required=True)
parser.add_argument('--username', '-u', type=str, help='postgresql username', required=True)
parser.add_argument('--password', '-p', type=str, help='postgresql password', required=True)
parser.add_argument('--dbname', '-db', type=str, help='name of the database to be altered', required=True)
parser.add_argument('--operation', '-op', type=str, help='Type U if you want to update an existing table in the database (on conflict -md5sum- do nothing), type UF if you want to force update (on conflict -md5sum- update the scores with the new one) or A if you want to add a new table.', required=True)
parser.add_argument('--tablename', '-n', type=str, help='exact name of the dataset you want to add/update', required=True)
args = parser.parse_args()

db = Database(username=args.username, password=args.password, database=args.dbname)

with open('sequence_md5sum.tsv', mode='w') as f, open('score_md5sum.tsv', mode='w') as m:
    f.write('md5sum\tsequence\n')
    m.write('md5sum\tscores\n')
    for row in file_reader(args.filepath):
        if row.startswith('sequence'):
            continue
        sp = row.split('\t')
        f.write(f'{hash_seq(sp[0])}\t{sp[0]}\n')
        m.write(f'{hash_seq(sp[0])}\t{sp[1]}\n')


if args.operation.lower() == 'a':
    if args.tablename in db.currently_existing_tables():
        os.remove('sequence_md5sum.tsv')
        os.remove('score_md5sum.tsv')
        raise db.TableAlreadyExists
    else:
        create_md5sum_table = '''CREATE TABLE temp (md5sum VARCHAR(128) NOT NULL, sequence TEXT NOT NULL);'''
        db.query(create_md5sum_table)
        simp_path = 'sequence_md5sum.tsv'
        abs_path = os.path.abspath(simp_path)
        dump_md5 = rf'''COPY temp FROM '{abs_path}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV HEADER;'''
        db.query(dump_md5)
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        db.query(insert_query)
        drop_table = '''DROP TABLE temp;'''
        db.query(drop_table)
        create_temp_data_table = f'''CREATE TABLE templ (
                                md5sum VARCHAR(128) NOT NULL,
                                scores JSONb not null; '''
        db.query(create_temp_data_table)
        create_data_table = f'''CREATE TABLE {args.tablename} (
                                md5sum VARCHAR(128) UNIQUE NOT NULL,
                                scores JSONb not null,
                                FOREIGN KEY (md5sum)
                                REFERENCES seq_md5sum (md5sum)); '''
        db.query(create_data_table)
        simp_path = 'score_md5sum.tsv'
        abs_path2 = os.path.abspath(simp_path)
        dump_data_to_temp = rf'''COPY templ FROM '{abs_path2}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV header QUOTE E'\b' ESCAPE '\';'''
        db.query(dump_data_to_temp)
        dump_data = rf'''insert into {args.tablename} select distinct * from templ on conflict (md5sum) do nothing;'''
        db.query(dump_data)
        drop_table = '''DROP TABLE templ;'''
        db.query(drop_table)
        db.close_connection()


elif args.operation.lower() == 'u':
    if args.tablename not in db.currently_existing_tables():
        os.remove('sequence_md5sum.tsv')
        os.remove('score_md5sum.tsv')
        raise db.TableCannotBeFound
    else:
        create_md5sum_table = '''CREATE TABLE temp (md5sum VARCHAR(128) NOT NULL, sequence TEXT NOT NULL);'''
        db.query(create_md5sum_table)
        simp_path = 'sequence_md5sum.tsv'
        abs_path = os.path.abspath(simp_path)
        dump_md5 = rf'''COPY temp FROM '{abs_path}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV HEADER;'''
        db.query(dump_md5)
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        db.query(insert_query)
        drop_table = '''DROP TABLE temp;'''
        db.query(drop_table)
        create_data_table = f'''CREATE TABLE temp (
                                md5sum VARCHAR(128) NOT NULL,
                                scores JSONb not null); '''
        db.query(create_data_table)
        simp_path = 'score_md5sum.tsv'
        abs_path2 = os.path.abspath(simp_path)
        dump_data = rf'''COPY temp FROM '{abs_path2}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV header QUOTE E'\b' ESCAPE '\';'''
        db.query(dump_data)
        insert_data = f'''insert into {args.tablename}(md5sum, scores)
                      select distinct * from temp
                      on conflict (md5sum) do nothing;'''
        db.query(insert_data)
        drop_table2 = '''DROP TABLE temp;'''
        db.query(drop_table2)
        db.close_connection()

elif args.operation.lower() == 'uf':
    if args.tablename not in db.currently_existing_tables():
        os.remove('sequence_md5sum.tsv')
        os.remove('score_md5sum.tsv')
        raise db.TableCannotBeFound
    else:
        create_md5sum_table = '''CREATE TABLE temp (md5sum VARCHAR(128) NOT NULL, sequence TEXT NOT NULL);'''
        db.query(create_md5sum_table)
        simp_path = 'sequence_md5sum.tsv'
        abs_path = os.path.abspath(simp_path)
        dump_md5 = rf'''COPY temp FROM '{abs_path}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV HEADER;'''
        db.query(dump_md5)
        insert_query = '''insert into seq_md5sum select distinct * from temp on conflict (md5sum) do nothing;'''
        db.query(insert_query)
        drop_table = '''DROP TABLE temp;'''
        db.query(drop_table)
        create_data_table = f'''CREATE TABLE temp (
                                md5sum VARCHAR(128) NOT NULL,
                                scores JSONb not null); '''
        db.query(create_data_table)
        simp_path = 'score_md5sum.tsv'
        abs_path2 = os.path.abspath(simp_path)
        dump_data = rf'''COPY temp FROM '{abs_path2}' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV header QUOTE E'\b' ESCAPE '\';'''
        db.query(dump_data)
        insert_data = f'''insert into {args.tablename}(md5sum, scores)
                      select distinct * from temp
                      on conflict (md5sum) do update set scores = EXCLUDED.scores;'''
        db.query(insert_data)
        drop_table2 = '''DROP TABLE temp;'''
        db.query(drop_table2)
        db.close_connection()

else:
    print('Typo error: --operation should be only A, U or UF')

os.remove('sequence_md5sum.tsv')
os.remove('score_md5sum.tsv')
