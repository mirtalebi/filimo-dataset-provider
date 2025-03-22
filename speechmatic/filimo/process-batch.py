import sqlite3
import os
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError

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



def get_data_from_speechmatic(predestination, audioName):
  API_KEY = "Ypb08Mu1y4im5i0QapmqSihldZh5tqvF"
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
          print(f'\t{audioName}: job {job_id} submitted successfully, waiting for transcript')
          transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
          # To see the full output, try setting transcription_format='json-v2'.
          write_to_output(transcript, f"content/filimo/{predestination}/{audioName.split('.')[0]}.sm.json")
          print(f'\t{audioName}: DONE')
      except HTTPStatusError as e:
          if e.response.status_code == 401:
              print('Invalid API key - Check your API_KEY at the top of the code!')
          elif e.response.status_code == 400:
              print(e.response.json()['detail'])
          else:
              raise e
          


def proccess_item(audioName):
  row = check_invalidation(audioName)
  if not row:
    print(f"\t{audioName}: Error - doesnt exist in database!")
    return
  
  if not row[7] == 'VALID':
    print(f"\t{audioName}: Error - is invalid")
    return
  
  if check_already_exists(row[4], audioName):
    print(f"\t{audioName}: Error - has already exists")
    return

  get_data_from_speechmatic(row[4], audioName)



def process():
  for root, dirs, files in os.walk('content/filimo'):
    print(f"Directory: {root}")
    for file in files:
      proccess_item(file)


process()