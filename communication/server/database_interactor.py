import logging
import sqlite3
import time

import database_constants

class DatabaseInteractor:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def initializeDatabase(self, database_location):
        try:
            logging.debug("Trying to find database at: {}".format(database_location))
            logging.debug(sqlite3.version)
            self.connection = sqlite3.connect(database_location)
        except sqlite3.Error as err:
            logging.debug("Error connecting to database: {}".format(err))
            return False
        else:
            if self.connection:
                self.cursor = self.connection.cursor()
                logging.debug("Database cursor initialized.")
                return True

    def getTableHeaders(self, table_name):
        return self.cursor.execute("PRAGMA ({})".format(table_name))

    def dump(self, date_epoch, table_name):
        data = self.cursor.execute("SELECT * from {}".format(table_name))

        return data

    def writeRow(self, data, table_name):
        logging.debug(type(data.get(database_constants.CONST_DATE)))

        sqlite_insert_with_param = "INSERT INTO '{}' ('{}', '{}', '{}') VALUES (?, ?, ?);".format(
                                    table_name,
                                    database_constants.CONST_DATE,
                                    #database_constants.CONST_BATTERY_STATUS,
                                    database_constants.CONST_CARBON_DIOXIDE,
                                    database_constants.CONST_DISTANCE,
                                    database_constants.CONST_HUMIDITY,
                                    database_constants.CONST_PANEL_TEMPERATURE_ONE,
                                    database_constants.CONST_PANEL_TEMPERATURE_TWO,
                                    database_constants.CONST_PANEL_TEMPERATURE_THREE,
                                    database_constants.CONST_PANEL_TEMPERATURE_FOUR,
                                    database_constants.CONST_PANEL_TEMPERATURE_FIVE,
                                    database_constants.CONST_PANEL_TEMPERATURE_SIX,
                                    database_constants.CONST_POWER_OUTPUT,
                                    database_constants.CONST_PRESSURE,
                                    database_constants.CONST_TEMPERATURE,
                                    database_constants.CONST_TVOC)

        data_tuple = (data.get(database_constants.CONST_DATE), 
                #data.get(database_constants.CONST_BATTERY_STATUS),
                data.get(database_constants.CONST_CARBON_DIOXIDE),
                data.get(database_constants.CONST_DISTANCE),
                data.get(database_constants.CONST_HUMIDITY),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_ONE),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_TWO),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_THREE),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_FOUR),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_FIVE),
                data.get(database_constants.CONST_PANEL_TEMPERATURE_SIX),
                data.get(database_constants.CONST_POWER_OUTPUT),
                data.get(database_constants.CONST_PRESSURE),
                data.get(database_constants.CONST_TEMPERATURE),
                data.get(database_constants.CONST_TVOC))

        try:
            self.cursor.execute(sqlite_insert_with_param, data_tuple)

            self.connection.commit()
        except Exception as err:
            logging.info("Unable to write to database properly.")
            logging.debug("Error message: {}".format(err))
