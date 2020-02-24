import sqlite3
import time

database = sqlite3.connect('testing')

database_cursor = database.cursor()

current_time = time.time()

print(current_time)
database_cursor.execute("INSERT INTO field_data VALUES ({}, 5, 10)".format(round(current_time)))

database.commit()

for row in database_cursor.execute("SELECT * from field_data"):
    print(row)

database.close()