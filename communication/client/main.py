import argparse
import logging
import requests
import json

def main():
    default_database_name = "capstone.db"
    default_database_location = ""
    default_host_name = "localhost"
    default_port = 28460
    default_timeout = 5

    parser = argparse.ArgumentParser(description='Lul.')
    parser.add_argument('--host', dest='host_name', action='store',
                            default=default_host_name,
                            help='Host name of the server. Defaults to localhost.')
    parser.add_argument('-p', '--port', dest='port', action='store',
                            type=int, default=default_port,
                            help='Port for the server. Defaults to 28460')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                            help='Enable verbose and debug messages.')
    parser.add_argument('-t', '--timeout', dest='timeout', action='store',
                            default=default_timeout,
                            help='Timeout for the TCP server socket. Defaults to 5 seconds.')
    parser.add_argument('-d', '--database', dest='database_location', action='store',
                            default=default_database_location,
                            help='Location for the database file. Defaults to present working directory.')
    parser.add_argument('-n', '--name', dest='database_name', action='store',
                            default=default_database_name,
                            help='The name for the database file, Defaults to capstone.db')

    arg_results = parser.parse_args()

    if arg_results.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')

    host_name = arg_results.host_name
    port = arg_results.port
    timeout = arg_results.timeout

if __name__ == '__main__':
    main()