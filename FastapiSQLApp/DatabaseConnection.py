import pandas as pd
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import json
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# This is an example of a json credentials file, all information are required, and the order of the information is
# important
# {"credentials" : [
#
#	{"ssh_credentials":{
#        "ipaddress": "xxx",
#        "SSH port": 22,
#        "User_name": "xxx",
#        "password": "xxx"
#    }},
#    {"database_credentials":{
#        "port": 5432,
#        "database_name": "xxx",
#        "database_user": "xxx",
#        "database_password": "xxx"
#
#    }
#    }
# ]
# }

def _read_json_credentials(json_path):
    with open(json_path, "r") as f:
        credentials = json.loads(f.read())
        credentials_list = []
        for i in credentials["credentials"]:
            credentials_list.append(i)
            
    ssh_credentials = credentials_list[0]['ssh_credentials']
    database_credentials = credentials_list[1]['database_credentials']
    
    return database_credentials


# ssh key kullan


def _connect_server(db_credentials):
    #server = SSHTunnelForwarder((ssh_data['ipaddress'], int(ssh_data['SSH port'])),
    #                            ssh_username=ssh_data["User_name"],
    #                            ssh_password=ssh_data["password"],
    #                            remote_bind_address=('localhost', db_credentials['port']))
    #server.start()
    engine =  create_engine(
        f'postgresql://{db_credentials["database_user"]}:{db_credentials["database_password"]}@{"localhost"}:{5432}/{db_credentials["database_name"]}'
    )
    return engine




path = r"/home2/mehmet/FastapiSQLApp/credentials_json.txt"
db = _read_json_credentials(path)

SessionLocal = Session(_connect_server(db))
