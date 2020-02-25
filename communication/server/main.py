import argparse
import logging
import requests
import json
import time

from database_interactor import DatabaseInteractor
from server import CapstoneTCPServer

def main():
    default_database_name = "capstone.db"
    default_database_location = ""
    default_host_name = "localhost"
    default_port = 28460
    default_timeout = 300

    parser = argparse.ArgumentParser(description='Lul.')
    parser.add_argument('-s', '--server', dest='host_name', action='store',
                            default=default_host_name,
                            help='Host name for TCP server. Defaults to localhost.')
    parser.add_argument('-p', '--port', dest='port', action='store',
                            type=int, default=default_port,
                            help='Port for TCP server. Defaults to 28460')
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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')

    host_name = arg_results.host_name
    port = arg_results.port
    timeout = arg_results.timeout

    if arg_results.database_location.endswith("/"):
        database_file = arg_results.database_location + arg_results.database_name
    else:
        database_file = arg_results.database_location + "/" + arg_results.database_name

    database_interactor = DatabaseInteractor()
    tcp_server = CapstoneTCPServer(host_name, port, timeout)

    database_connected = False
    server_connected = False

    while True:
        # Initializating server
        logging.info(server_connected)

        if not server_connected:
            logging.info("Initializing server....")
            if tcp_server.initializeSocket():
                server_connected = True
                logging.info("Successfully initialized server.")
            else:
                logging.info("Failed to initialize server or accept a connection within the specified timeout.")

        # if not database_connected:
        #     print("Connecting to database....")
        #     if database_interactor.initializeDatabase(database_file):
        #         database_connected = True
        #         logging.info("Connected to the database.")
        #     else:
        #         logging.info("Failed to connect to the database.")
        time.sleep( 5 )

        data = {
            "temperature": 18
        }

        data_bytes = json.dumps(data).encode('utf-8')

        if server_connected:
                header = tcp_server.receive(2)
                if header:
                    read_data = json.loads(data.decode('utf-8'))
                    logging.info("Read data: " + str(read_data.get("temperature")))

if __name__ == '__main__':
    main()