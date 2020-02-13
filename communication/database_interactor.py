import sqlite3
import time

from database_constants import DatabaseConstants

class DatabaseInteractor:
    def __init__(self, database_connection, database_cursor):
        self.connection = database_connection
        self.cursor = database_cursor

    def getTableHeaders(self, table_name):
        return self.cursor.execute("PRAGMA ({})".format(table_name))

    def readRows(self, date_epoch, table_name):
        if isinstance(date_epoch, str):
            time_to_read = int(date_epoch)
        elif isinstance(date_epoch, float):
            time_to_read = round(date_epoch)
        else:
            time_to_read = date_epoch
        
        rows = self.cursor.execute("SELECT * from {} where {} = {}".format(table_name, 
                DatabaseConstants.CONST_DATE, time_to_read))

        return rows

    def write(self, data, table_name):
        current_data = self.cursor.execute("SELECT * from {} where {} = {}".format(table_name, 
                DatabaseConstants.CONST_DATE, data.date))
        if current_data:
            self.cursor.execute("UPDATE {} SET {} = {} {} = {}".format(table_name, 
                    DatabaseConstants.CONST_HUMIDITY, data.humidity, 
                    DatabaseConstants.CONST_TEMPERATURE, data.temperature))
        else:
            self.cursor.execute("INSERT INTO {} VALUES ({}, {}, {})".format(table_name,
                    data.date, data.humidity, data.temperature))
