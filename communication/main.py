import argparse
import logging
import requests
import json

from server import CapstoneTCPServer

# main

default_host_name = "localhost"
default_port = 20005

parser = argparse.ArgumentParser(description='Lul.')
parser.add_argument('-h', '--host', dest='host_name',
                    default=default_host_name,
                    help='Host name for TCP server')
parser.add_argument('-p', '--port', dest='port',
                    type=int, default=default_port,
                    help='Port for TCP server')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Display debug messages')

args = parser.parse_args()

debug_mode = False
if args.verbose:
    debug_mode = True

host_name = args.host_name
port = args.port
timeout = 1

print(debug_mode, host_name, port)

# initialization

tcp_server = CapstoneTCPServer(host_name, port, timeout)

while True:
    tcp_server.initializeSocket()