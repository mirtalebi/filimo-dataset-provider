import sqlite3

dbPath = './../../filimo/data.db'

try:
   
    # Connect to DB and create a cursor
    sqliteConnection = sqlite3.connect(dbPath)
    cursor = sqliteConnection.cursor()
 
    # Create a table
    cursor.execute('''CREATE TABLE movies( 
    ID TEXT, 
    KEY TEXT, 
    TYPE TEXT, 
    TITLE TEXT,
    SERIAL_ID TEXT,
    SERIAL_TITLE TEXT,
    STATUS TEXT
                   );''') 
 
    # Close the cursor
    cursor.close()
 
# Handle errors
except sqlite3.Error as error:
    print('Error occurred - ', error)
 
# Close DB Connection irrespective of success
# or failure
finally:
   
    if sqliteConnection:
        sqliteConnection.close()
        print('SQLite Connection closed')