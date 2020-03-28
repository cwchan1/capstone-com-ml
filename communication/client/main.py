import argparse
import datetime
import logging
import requests
import json
import socket
import time

import database_constants
from sensors import Sensors

def packData(date, battery_status, carbon_dioxide, distance, humidity, panel_temp_one,
                panel_temp_two, panel_temp_three, panel_temp_four, panel_temp_five, panel_temp_six,
                power_output, pressure, temperature, tvoc):
    data_dict = {
        database_constants.CONST_DATE: date,
        database_constants.CONST_BATTERY_STATUS: battery_status,
        database_constants.CONST_CARBON_DIOXIDE: carbon_dioxide,
        database_constants.CONST_DISTANCE: distance,
        database_constants.CONST_HUMIDITY: humidity,
        database_constants.CONST_PANEL_TEMPERATURE_ONE: panel_temp_one,
        database_constants.CONST_PANEL_TEMPERATURE_TWO: panel_temp_two,
        database_constants.CONST_PANEL_TEMPERATURE_THREE: panel_temp_three,
        database_constants.CONST_PANEL_TEMPERATURE_FOUR: panel_temp_four,
        database_constants.CONST_PANEL_TEMPERATURE_FIVE: panel_temp_five,
        database_constants.CONST_PANEL_TEMPERATURE_SIX: panel_temp_six,
        database_constants.CONST_POWER_OUTPUT: power_output,
        database_constants.CONST_PRESSURE: pressure,
        database_constants.CONST_TEMPERATURE: temperature,
        database_constants.CONST_TVOC: tvoc
    }

    return data_dict

def main():
    default_database_name = "capstone.db"
    default_database_location = ""
    default_host_name = "localhost"
    default_port = 28460
    default_timeout = 300

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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')

    host_name = arg_results.host_name
    port = arg_results.port
    timeout = arg_results.timeout

    server_connected = False

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client_address = (host_name, port)

    sensors = Sensors()

    while True:
        if not server_connected:
            logging.info("Connecting....")
            try:
                client.connect( client_address )
            except socket.error as msg:
                logging.info("Error connecting to server with error message: " + msg.strerror)
                time.sleep(0.1)
                continue
            else:
                server_connected = True
                logging.info("Connected to server.")
        else:
            date = str(datetime.datetime.now())
            
            data = sensors.run()
            data[database_constants.CONST_DATE] = date

            data_bytes = json.dumps(data).encode('utf-8')
            
            type = 10 # data type
            type_data = type.to_bytes(2, byteorder='little')

            length = len(data_bytes).to_bytes(24, byteorder='little')

            buffer_byte_array = bytearray()
            # 24 Bytes Header for full length
            buffer_byte_array.extend(type_data)
            buffer_byte_array.extend(length)
            buffer_byte_array.extend(data_bytes)
            logging.debug("Sending: " + str(buffer_byte_array))

            client.send(bytes(buffer_byte_array))

            type = 20 # image type
            type_data = type.to_bytes(2, byteorder='little')

            try:
                image_file = open("/home/pi/PVCT/image.jpg", "rb")
                image_bytes = image_file.read()

                length = len(image_bytes).to_bytes(24, byteorder='little')

                buffer_byte_array = bytearray()
                # 24 Bytes Header for full length
                buffer_byte_array.extend(type_data)
                buffer_byte_array.extend(length)
                buffer_byte_array.extend(image_bytes)
                logging.debug("Sending image")

                image_file.close()
            except Exception as err:
                logging.info("Failed to send image file.")
                logging.debug("Error message: {}".format(err))

        time.sleep(10)

if __name__ == '__main__':
    main()