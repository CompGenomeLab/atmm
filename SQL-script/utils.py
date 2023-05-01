import json
import hashlib


def read_json_credentials(json_path):
    with open(json_path, "r") as f:
        credentials = json.load(f)
    return credentials


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


def file_reader(file_name):
    for row in open(file_name, "r"):
        yield row.strip()
