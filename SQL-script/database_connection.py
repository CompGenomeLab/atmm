from sqlalchemy import create_engine


class DatabaseConnector:
    def __init__(self, creds):
        self.creds = creds
        self.ssh_tunnel = None
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
        if self.ssh_tunnel:
            self.ssh_tunnel.stop()
