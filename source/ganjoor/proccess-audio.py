import sqlite3
import requests
import os

def get_data_from_db(db_path = 'data.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute a query to retrieve data
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    return data

db_path = 'data.db'
data = get_data_from_db(db_path)
for row in data:
    id, poemId, poemFullTitle, poemFullUrl, audioTitle, audioArtist, audioArtistUrl, mp3Url, xmlText, downloaded = row
    
    if (downloaded == 1):
        continue

    url = "https://i.ganjoor.net/ak/5000-fz-1532962519.mp3"
    # Create the directory if it doesn't exist
    os.makedirs('../../ganjoor/' + audioArtist, exist_ok=True)

    # Download the audio file
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join('../../ganjoor/' + audioArtist, f'{id}.mp3')
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # Update the database to set downloaded to 1
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE data SET downloaded = 1 WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        
    else:
        print(f'Failed to download {url}')
    
    print(f'{id}: {poemFullTitle} - {audioTitle} by {audioArtist}')