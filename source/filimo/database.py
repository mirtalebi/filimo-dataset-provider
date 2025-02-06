import sqlite3

dbPath = './../../filimo/data.db'

def get_db_connection():
    conn = sqlite3.connect(dbPath)
    return conn

def close_db_connection(conn):
    conn.close()
    pass

def save_movie(conn, id: str, key: str, type: str, title: str, serial_id = '', serial_title = '', status = ''):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM movies WHERE ID = ?', (id,))
    if cursor.fetchone()[0] > 0:
        return
    cursor.execute('INSERT INTO movies (ID, KEY, TYPE, TITLE, SERIAL_ID, SERIAL_TITLE, STATUS) VALUES (?, ?, ?, ?, ?, ?, ?)', (id, key, type, title, serial_id, serial_title, status))
    conn.commit()
    pass

def get_movies(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies')
    return cursor.fetchall()
    pass

def update_movie_status(conn, key: str, status: str):
    cursor = conn.cursor()
    cursor.execute('UPDATE movies SET STATUS = ? WHERE KEY = ?', (status, key))
    conn.commit()
    pass