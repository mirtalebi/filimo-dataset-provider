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

    # Create the directory if it doesn't exist
    os.makedirs('../../ganjoor/' + audioArtist, exist_ok=True)

    # Download the audio file
    response = requests.get(mp3Url)
    if response.status_code == 200:
        file_path = os.path.join('../../ganjoor/' + audioArtist, f'{id}.mp3')
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f'Failed to download {mp3Url}')
        continue

    # Download the XML file
    response = requests.get(xmlText)
    if response.status_code == 200:
        xml_file_path = os.path.join('../../ganjoor/' + audioArtist, f'{id}.xml')
        with open(xml_file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f'Failed to download {xmlText}')
        continue
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE data SET downloaded = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()