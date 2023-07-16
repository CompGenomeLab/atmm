import argparse
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def parse_arguments():
    """
    Parse command-line arguments related to database connection.

    Returns:
        argparse.Namespace: Parsed arguments. Currently includes dbpath.
    """
    parser = argparse.ArgumentParser(description="Database connection")
    parser.add_argument('--dbpath', '-dp', type=str, required=True)
    return parser.parse_args()


def _read_json_credentials(json_path):
    """
    Read JSON credentials from a file.

    Args:
        json_path (str): Path to the JSON file containing the credentials.

    Returns:
        dict: Dictionary containing the credentials.
    """
    with open(json_path, "r") as f:
        credentials = json.loads(f.read())
        print(credentials)
    return credentials


class DatabaseConnector:
    def __init__(self, db_credentials):
        """
        Initialize DatabaseConnector with the provided credentials.

        Args:
            db_credentials (dict): Dictionary containing the credentials.
        """
        self.creds = db_credentials
        self.engine = None

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.

        Returns:
            sqlalchemy.engine.Engine: Database engine.
        """
        try:
            self.engine = create_engine(
                f'postgresql://{self.creds["PG_UN"]}:{self.creds["PG_DB_PW"]}@{self.creds["LOCALHOST"]}:{5432}/{self.creds["PG_DB_NAME"]}')
        except Exception as e:
            print(f'Connection Has Failed: {str(e)}')
            return None
        print("Connection Successful")
        return self.engine

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        Returns:
            DatabaseConnector: The current instance of DatabaseConnector.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.

        Args:
            exc_type (BaseException): The type of exception that caused the context to be exited.
            exc_val (BaseException): The instance of exception that caused the context to be exited.
            exc_tb (traceback): A traceback object encapsulating the call stack at the point
                                where the exception originally occurred.
        """
        self.close()

    def close(self):
        """
        Close the connection to the PostgreSQL database.
        """
        if self.engine:
            self.engine.dispose()


# Parse the arguments
args = parse_arguments()
db_credentials_file = args.dbpath

# Connect to the database and create a session
db_connector = DatabaseConnector(_read_json_credentials(db_credentials_file))
engine = db_connector.connect()
session = Session(engine)
