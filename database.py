import sqlite3

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    return conn

def close_db_connection(conn):
    conn.close()
    pass

def save_movie(conn, id: str, key: str, type: str, title: str):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM movies WHERE ID = ?', (id,))
    if cursor.fetchone()[0] > 0:
        return
    cursor.execute('INSERT INTO movies (ID, KEY, TYPE, TITLE) VALUES (?, ?, ?, ?)', (id, key, type, title))
    conn.commit()
    pass