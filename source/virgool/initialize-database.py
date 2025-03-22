import sqlite3

dbPath = './../../virgool/data.db'

try:
   
    # Connect to DB and create a cursor
    sqliteConnection = sqlite3.connect(dbPath)
    cursor = sqliteConnection.cursor()
 
    # Create a table
    cursor.execute('''CREATE TABLE episodes( 
    hash TEXT, 
    title TEXT, 
    sound_url TEXT, 
    post_url TEXT,
    cast_hash TEXT,
    cast_name TEXT,
    status TEXT
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