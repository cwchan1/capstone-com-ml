import argparse
import logging
import requests
import json

# main

default_host_name = "localhost"
default_port = 20005

parser = argparse.ArgumentParser(description='Lul.')
parser.add_argument('--host', dest='host_name', action='store_const',
                    default=default_host_name,
                    help='Host name for TCP server')
parser.add_argument('--port', dest='port', action='store_const',
                    type=int, default=default_port,
                    help='Host name for TCP server')
parser.add_argument('--verbose', dest='verbose',
                    help='Display debug messages')

args = parser.parse_args()

debug_mode = False
if args.verbose:
    debug_mode = True

