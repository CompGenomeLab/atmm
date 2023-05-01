import argparse
import json
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Database connection")
    parser.add_argument('--sshpath', '-sp', type=str, required=False)
    parser.add_argument('--dbpath', '-dp', type=str, required=True)
    parser.add_argument('--sshtunnel', '-s', type=bool, required=True)

    return parser.parse_args()


def _read_json_credentials(json_path):
    with open(json_path, "r") as f:
        credentials = json.loads(f.read())
        print(credentials)
    return credentials


class SSHTunnel:
    def __init__(self, ssh_credentials):
        self.server = SSHTunnelForwarder((ssh_credentials['ipaddress'], int(ssh_credentials['SSH port'])),
                                         ssh_username=ssh_credentials["User_name"],
                                         ssh_password=ssh_credentials["password"],
                                         remote_bind_address=('localhost', 5432))

    def ssh_tunnel_starter(self):
        self.server.start()
        return self.server.local_bind_port

    def ssh_tunnel_stop(self):
        self.server.stop()


def _connect_server(local_bind_port, db_credentials):
    engine = create_engine(
        f'postgresql://{db_credentials["database_user"]}:{db_credentials["database_password"]}@{"localhost"}:{local_bind_port}/{db_credentials["database_name"]}'
    )
    return engine


if __name__ == '__main__':
    args = parse_arguments()
    use_sshtunnel = args.sshtunnel

    if use_sshtunnel is True:
        ssh_credentials_file = args.sshpath
        db_credentials_file = args.dbpath
        ssh_tunnel = SSHTunnel(_read_json_credentials(ssh_credentials_file))
        local_port = ssh_tunnel.ssh_tunnel_starter()
        session = Session(_connect_server(str(local_port),
                                          _read_json_credentials(db_credentials_file)))
    else:
        db_credentials_file = args.dbpath
        session = Session(_connect_server(5432, _read_json_credentials(db_credentials_file)))

    db = Database(session)