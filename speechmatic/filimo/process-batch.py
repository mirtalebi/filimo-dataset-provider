import sqlite3
import os
import threading
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError

API_KEY = input('api key:')

def write_to_output(data, output):
  with open(output, 'w') as f:
    f.write(str(data))


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



def get_data_from_speechmatic(predestination, audioName, API_KEY, DIRECTORY_INDEX):
  LANGUAGE = "fa"

  settings = ConnectionSettings(
      url="https://asr.api.speechmatics.com/v2",
      auth_token=API_KEY,
  )

  conf = {
      "type": "transcription",
      "transcription_config": {
          "language": LANGUAGE,
          "operating_point": "enhanced"
      }
  }

  with BatchClient(settings) as client:
      try:
          job_id = client.submit_job(
              audio=f"content/filimo/{predestination}/{audioName}",
              transcription_config=conf,
          )
          print(f'{DIRECTORY_INDEX}\t{audioName}: job {job_id} submitted successfully, waiting for transcript')
          transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
          # To see the full output, try setting transcription_format='json-v2'.
          write_to_output(transcript, f"content/filimo/{predestination}/{audioName.split('.')[0]}.sm.json")
          print(f'{DIRECTORY_INDEX}\t{audioName}: DONE')
      except HTTPStatusError as e:
          if e.response.status_code == 401:
              print('Invalid API key - Check your API_KEY at the top of the code!')
          elif e.response.status_code == 400:
              print(e.response.json()['detail'])
          else:
              raise e
          


def proccess_item(audioName, API_KEY, DIRECTORY_INDEX, semaphore):
  with semaphore:
    row = check_invalidation(audioName)
    if not row:
        print(f"{DIRECTORY_INDEX}\t{audioName}: Error - doesnt exist in database!")
        return
    
    if not row[7] == 'VALID':
        print(f"{DIRECTORY_INDEX}\t{audioName}: Error - is invalid")
        return
    
    if check_already_exists(row[4], audioName):
        print(f"{DIRECTORY_INDEX}\t{audioName}: Error - has already exists")
        return
    get_data_from_speechmatic(row[4], audioName,API_KEY, DIRECTORY_INDEX)



def process(API_KEY):
  DIRECTORY_INDEX = 0
  
  for root, dirs, files in os.walk('content/filimo'):
    print(f"Directory: {root}")
    DIRECTORY_INDEX = DIRECTORY_INDEX + 1
    max_threads = 10
    semaphore = threading.Semaphore(max_threads)
    threads = []
    for file in files:
      if "mp3" in file:
        thread = threading.Thread(target=proccess_item, args=(file, API_KEY, DIRECTORY_INDEX, semaphore))
        threads.append(thread)
        thread.start()
        # proccess_item()
        
    for thread in threads:
        thread.join()
  
  

process(API_KEY)