#!/usr/bin/env python3

"""
Copyright Pure Storage, Inc. 2018. All Rights Reserved

usage: pure1_api_client.py [-h] [-p PASSWORD] [-o OUTPUT]
                           id private_key_file

Retrieves an Access Token for Pure1 Public API

positional arguments:
  id                    application Id displayed on the Pure1 API Registration
                        page (i.e. pure1:apikey:dssf2331sd)
  private_key_file      path to the private key

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        use if private key is encrypted (or use keyboard
                        prompt)
  -o OUTPUT, --output OUTPUT
                        write the access token to a file
"""

from argparse import ArgumentParser
from time import time
from paramiko import RSAKey, ssh_exception
from getpass import getpass
from io import StringIO
import requests
import warnings
import json
import jwt
import sys

TOKEN_EXCHANGE_URL = 'https://api.pure1.purestorage.com/oauth2/1.0/token'


def fatal(message):
    print('Error: {}'.format(message), file=sys.stderr)
    sys.exit(1)


# Token Exchange requires a JWT in the Authorization Bearer header with this format
def generate_id_token(iss, private_key, expire_seconds=10):
    new_jwt = jwt.encode({'iss': iss, 'iat': int(time()), 'exp': int(time()) + expire_seconds},
                         private_key, algorithm='RS256')
    return new_jwt


# Make POST request to Token Exchange and return access token
def get_access_token(id_token):
    # Ignore the "Unverified HTTPS request is being made." warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        data = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token': id_token,
                'subject_token_type': 'urn:ietf:params:oauth:token-type:jwt'}
        response = requests.post(TOKEN_EXCHANGE_URL, data=data, verify=False)
        response.close()
        if response:
            response = response.json()
            if 'access_token' in response:
                return response['access_token']
        fatal('Failed to get proper access token:\n{}'.format(response))


# Load the private key from a file and decrypt if necessary
def get_private_key(file_name, password=None):
    try:
        rsa_key = RSAKey.from_private_key_file(file_name, password)
    except ssh_exception.PasswordRequiredException:
        password = getpass(prompt="Private key password: ")
        return get_private_key(file_name, password)
    except ssh_exception.SSHException:
        fatal('Invalid private key password')
    except FileNotFoundError:
        fatal('Could not find private key file')
    with StringIO() as buf:
        rsa_key.write_private_key(buf)
        return buf.getvalue()


def main():
    # Command-line arguments
    parser = ArgumentParser(description="Retrieves an Access Token for Pure1 Public API")
    parser.add_argument('id', type=str, help="application Id displayed on the Pure1 API Registration page"
                                             " (i.e. pure1:apikey:dssf2331sd)")
    parser.add_argument('private_key_file', type=str, help="path to the private key")
    parser.add_argument('-p', '--password', type=str, help="use if private key is encrypted (or use keyboard prompt)")
    parser.add_argument('-o', '--output', type=str, help="write the access token to a file")
    args = parser.parse_args()

    # Generate a new JWT using id and private key
    pri_key = get_private_key(args.private_key_file, args.password)
    id_token = generate_id_token(args.id, pri_key)

    # Call the Token Exchange
    access_token = get_access_token(id_token)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(access_token)
            print("Access token written to {}".format(f.name))
    else:
        print(access_token)


if __name__ == '__main__':
    main()
