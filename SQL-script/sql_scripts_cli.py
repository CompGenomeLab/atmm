import shutil

from database_connection import DatabaseConnector
from database import Database
from utils import read_json_credentials
import argparse
import os
from database_manager import  ForceUpdateTable, UpdateTable, AddTable


def parse_arguments():
    parser = argparse.ArgumentParser(description="Database connection")
    parser.add_argument('--creds', '-c', type=str, required=True, help='Path to the JSON credentials file')
    parser.add_argument('--filepath', '-fp', type=str, required=True,
                        help='Full path of the expected TSV file with two columns: sequence and score (JSON format)')
    parser.add_argument('--header', '-he', action='store_true',
                        help='If a header exists in the first line of the input file, add -he to the command')
    parser.add_argument('--operation', '-op', type=str, required=True,
                        help='Type U to update an existing table in the database (on conflict -md5sum- do nothing), '
                             'type UF to force update (on conflict -md5sum- update the scores with the new one) or '
                             'type A to add a new table.')
    parser.add_argument('--table-name', '-n', type=str, required=True,
                        help='Exact name of the dataset you want to add/update')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    creds = read_json_credentials(args.creds)

    # Use the `DatabaseConnector` class to handle the connection
    with DatabaseConnector(creds) as db_connection:
        session = db_connection.engine

        # Place the rest of your code here, using the `session` object for database operations
        db = Database(session)
        if args.operation.lower() == 'a':
            manager = AddTable(db, args)
            manager.execute()
        elif args.operation.lower() == 'u':
            manager = UpdateTable(db, args)
            manager.execute()
        elif args.operation.lower() == 'uf':
            manager = ForceUpdateTable(db, args)
            manager.execute()
        else:
            print('Typo error: --operation should be only A, U, or UF')
    working_dir = os.path.dirname(args.filepath)
    md5sum_sequence_file_path = os.path.join(working_dir, 'sequence_md5sum.tsv')
    md5sum_score_json_file_path = os.path.join(working_dir, 'md5sum_score_json.tsv')
    os.remove(md5sum_score_json_file_path)
    os.remove(md5sum_sequence_file_path)


