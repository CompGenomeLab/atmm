import argparse
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def parse_arguments():
    parser = argparse.ArgumentParser(description="Database connection")
    parser.add_argument('--dbpath', '-dp', type=str, required=True)
    return parser.parse_args()


def _read_json_credentials(json_path):
    with open(json_path, "r") as f:
        credentials = json.loads(f.read())
        print(credentials)
    return credentials


class DatabaseConnector:
    def __init__(self, db_credentials):
        self.creds = db_credentials
        self.engine = None

    def connect(self):
        try:
            self.engine = create_engine(
                f'postgresql://{self.creds["PG_UN"]}:{self.creds["PG_DB_PW"]}@{self.creds["LOCALHOST"]}:{5432}/{self.creds["PG_DB_NAME"]}')
        except Exception as e:
            print(f'Connection Has Failed: {str(e)}')
            return None
        print("Connection Successful")
        return self.engine

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.engine:
            self.engine.dispose()

# Parse the arguments
args = parse_arguments()
db_credentials_file = args.dbpath

# Connect to the database and create a session
db_connector = DatabaseConnector(_read_json_credentials(db_credentials_file))
engine = db_connector.connect()
session = Session(engine)
