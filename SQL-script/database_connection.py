from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder


class DatabaseConnector:
    def __init__(self, creds):
        self.creds = creds
        self.ssh_tunnel = None
        self.engine = None

    def connect(self):


        try:
            print('Connecting to the PostgresSQL Database...')

            self.ssh_tunnel = SSHTunnelForwarder(
                self.creds["SSH_HOST"],
                ssh_port=self.creds["SSH_PORT"],
                ssh_username=self.creds["SSH_UN"],
                ssh_password=self.creds["SSH_PKEY"],
                remote_bind_address=('localhost', 5432)
            )

            self.ssh_tunnel.start()

            self.engine = create_engine(
                f'postgresql://{self.creds["PG_UN"]}:{self.creds["PG_DB_PW"]}@{self.creds["LOCALHOST"]}:{self.ssh_tunnel.local_bind_port}/{self.creds["PG_DB_NAME"]}')
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
