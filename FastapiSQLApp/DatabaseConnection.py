from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
import json

Base = declarative_base()


# This is an example of a json credentials file, all information are required, and the order of the information is
# important
#	{"ssh_credentials":{
#        "ipaddress": "xxx",
#        "SSH port": 22,
#        "User_name": "xxx",
#        "password": "xxx"
#    }}
# database_credentials":{
#        "port": 5432,
#        "database_name": "xxx",
#        "database_user": "xxx",
#        "database_password": "xxx"
#
#    }
#    }


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


def _read_json_credentials(json_path):
    with open(json_path, "r") as f:
        credentials = json.loads(f.read())
        print(credentials)
    return credentials


def _connect_server(local_bind_port, db_credentials):
    engine = create_engine(
        f'postgresql://{db_credentials["database_user"]}:{db_credentials["database_password"]}@{"localhost"}:{local_bind_port}/{db_credentials["database_name"]}'
    )
    return engine


try:
    use_sshtunnel = int(input("If you want to use sshtunnel please type '1' else '0'."))
    if use_sshtunnel == 0 or use_sshtunnel == 1:
        print("Valid input.")
        if use_sshtunnel == 1:
            ssh_credentials_file = input("Please enter ssh credentials file.")
            db_credentials_file = input("Please enter db credentials file path.")
            ssh_tunnel = SSHTunnel(_read_json_credentials(ssh_credentials_file))
            local_port = ssh_tunnel.ssh_tunnel_starter()
            session = Session(_connect_server(str(local_port),
                                              _read_json_credentials(db_credentials_file)))
        else:
            db_credentials_file = input("Please enter db credentials file path.")
            session = Session(_connect_server(5432, _read_json_credentials(db_credentials_file)))
except ValueError:
    raise Exception("Invalid input.")
