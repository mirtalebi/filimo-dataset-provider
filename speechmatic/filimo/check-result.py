from tqdm import tqdm
import os
import sqlite3


def check_invalidation(audioName):
  conn = sqlite3.connect('content/data.db')
  cursor = conn.cursor()

  cursor.execute(f"SELECT * FROM audio_chunks where audio='{audioName}'")
  rows = cursor.fetchall()
  conn.close()

  for row in rows:
    return row



def check_already_exists(predestination, audioName):
  audioName = audioName.split('.')[0]
  return os.path.exists(f"content/filimo/{predestination}/{audioName}.sm.json")


DIRECTORY_INDEX = 0
for root, dirs, files in os.walk('content/filimo'):
    print(f"Directory: {root}")
    DIRECTORY_INDEX = DIRECTORY_INDEX + 1
    for i in tqdm (range (len(files)), desc="Loading..."):
      file = files[i]
      if "mp3" in file:
        row = check_invalidation(file)
        if not row:
            continue
        
        if not row[7] == 'VALID':
            continue
        
        if not check_already_exists(row[4], file):
            print(f"{DIRECTORY_INDEX}\t{file}: Error - has already exists")
            break
           