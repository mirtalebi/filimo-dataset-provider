import sqlite3

dbPath = './../../ganjoor/data.db'

try:
   
    # Connect to DB and create a cursor
    sqliteConnection = sqlite3.connect(dbPath)
    cursor = sqliteConnection.cursor()
 
    # Create a table
    cursor.execute('''CREATE TABLE poet( 
    ID TEXT, 
    NAME TEXT, 
    URL TEXT);''') 

    cursor.execute('''CREATE TABLE poem( 
    ID TEXT, 
    TITLE TEXT, 
    POET_ID TEXT,
    HTML TEXT,
    URL TEXT);''') 

    cursor.execute('''CREATE TABLE recitations( 
    ID TEXT, 
    TITLE TEXT, 
    POEM_ID TEXT,
    MP3 TEXT,
    XML TEXT);''') 
 
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