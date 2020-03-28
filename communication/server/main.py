import argparse
import logging
import requests
import json
import time

import database_constants
from database_interactor import DatabaseInteractor
from server import CapstoneTCPServer

def main():
    default_database_name = "capstone.db"
    default_database_location = ""
    default_host_name = "localhost"
    default_port = 28460
    default_table_name = "sensors_data"
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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')

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

        if not database_connected:
            print("Connecting to database....")
            if database_interactor.initializeDatabase(database_file):
                database_connected = True
                logging.info("Connected to the database.")
            else:
                logging.info("Failed to connect to the database.")

        if server_connected and database_connected:
            logging.debug("Receiving data....")
            data = tcp_server.receive(2)
            if data:
                type = int.from_bytes(data, 'little')

                header_data = tcp_server.receive(24)
                header =  int.from_bytes(header_data, 'little')

                logging.debug("Message length: {}".format(header))

                body_data = tcp_server.receive(header)
                if body_data:
                    if type == 10:
                        read_data = json.loads(body_data.decode('utf-8'))
                        logging.debug(json.dumps(read_data, sort_keys=True, indent=4))

                        database_interactor.writeRow(read_data, default_table_name)
                    elif type == 20:
                        logging.debug("Reading image file...")
                        try:
                            image_file = open("panel_image.jpg", "wb")
                            image_file.write(body_data)
                            image_file.close()
                        except Exception as err:
                            logging.info("Failed to write image file to panel_image.jpg.")
                            logging.debug("Error Message: {}".format(err))

if __name__ == '__main__':
    main()