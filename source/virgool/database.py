import sqlite3

dbPath = './../../virgool/data.db'

def get_db_connection():
    conn = sqlite3.connect(dbPath)
    return conn

def close_db_connection(conn):
    conn.close()
    pass

def save_episode(conn, hash: str, title: str, sound_url: str, post_url: str, cast_hash, cast_name, status = '', text = ''):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM episodes WHERE hash = ?', (hash,))
    if cursor.fetchone()[0] > 0:
        return
    cursor.execute('INSERT INTO episodes (hash, title, sound_url, post_url, cast_hash, cast_name, status, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                   (hash, title, sound_url, post_url, cast_hash, cast_name, status, text))
    conn.commit()
    pass

def get_episodes(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM episodes')
    return cursor.fetchall()
    pass

def update_episode_status(conn, hash: str, status: str):
    cursor = conn.cursor()
    cursor.execute('UPDATE episodes SET status = ? WHERE hash = ?', (status, hash))
    conn.commit()
    pass

def update_episode_text(conn, hash: str, text: str):
    cursor = conn.cursor()
    cursor.execute('UPDATE episodes SET text = ? WHERE hash = ?', (text, hash))
    conn.commit()
    pass