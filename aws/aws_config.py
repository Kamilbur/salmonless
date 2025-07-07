import os
import pathlib

home = pathlib.Path(os.environ.get('HOME', '/root'))

with open(home / '.aws/credentials') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('aws_access_key_id'):
            os.environ['AWS_ACCESS_KEY_ID'] = line.split('=')[1].strip()
        if line.startswith('aws_secret_access_key'):
            os.environ['AWS_SECRET_ACCESS_KEY'] = line.split('=')[1].strip()