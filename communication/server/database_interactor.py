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
        # current_data = self.cursor.execute("SELECT * from {} where {} = {}".format(table_name, 
        #         database_constants.CONST_DATE, data.date))
        # if current_data:
        #     self.cursor.execute("UPDATE {} SET {} = {} {} = {}".format(table_name, 
        #             database_constants.CONST_HUMIDITY, data.humidity, 
        #             database_constants.CONST_TEMPERATURE, data.temperature))
        # else:
        logging.debug(type(data.get(database_constants.CONST_DATE)))

        sqlite_insert_with_param = "INSERT INTO '{}' ('{}', '{}', '{}') VALUES (?, ?, ?);".format(
                                    table_name,
                                    database_constants.CONST_DATE,
                                    database_constants.CONST_HUMIDITY,
                                    database_constants.CONST_TEMPERATURE)

        insert_tuple = (data.get(database_constants.CONST_DATE), 
                data.get(database_constants.CONST_HUMIDITY), 
                data.get(database_constants.CONST_TEMPERATURE))

        self.cursor.execute(sqlite_insert_with_param, insert_tuple)

        self.connection.commit()
