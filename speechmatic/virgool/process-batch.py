import sqlite3
import os
import threading
import requests
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError
from utils import SingletonLogger

logger = SingletonLogger().get_logger()
API_KEY = input('api key:')

def write_to_output(data, output):
  with open(output, 'w') as f:
    f.write(str(data))


def get_data():
  conn = sqlite3.connect('data.db')
  cursor = conn.cursor()

  cursor.execute(f"SELECT * FROM episodes")
  rows = cursor.fetchall()
  conn.close()
  
  return rows



def check_sm_already_exists(cast_hash, episode_hash):
  audioName = audioName.split('.')[0]
  return os.path.exists(f"content/{cast_hash}/{episode_hash}.sm.json")



def download_file(cast_hash, episode_hash ,url):
  ext = url.split('.')[-1]
  if (os.path.exists(f"content/{cast_hash}/{episode_hash}.{ext}")):
     return True
  
  try:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    with open(f'content/{cast_hash}/{episode_hash}.{ext}', 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192): #chunk size is 8KB
            if chunk:  # filter out keep-alive new chunks
                file.write(chunk)

    print(f"File downloaded successfully and saved to: content/{cast_hash}/{episode_hash}.{ext}")
    return True

  except requests.exceptions.RequestException as e:
      print(f"Error downloading file: {e}")
      return False
  except OSError as e:
      print(f"Error saving file: {e}")
      return False




def get_data_from_speechmatic(cast_hash, episode_hash ,url, API_KEY):
  ext = url.split('.')[-1]
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
              audio=f"content/{cast_hash}/{episode_hash}.{ext}",
              transcription_config=conf,
          )
          print(f'{cast_hash}\t{episode_hash}: job {job_id} submitted successfully, waiting for transcript')
          transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
          write_to_output(transcript, f"content/{cast_hash}/{episode_hash}.sm.json")
          print(f'{cast_hash}\t{episode_hash}: DONE')
          logger.info(f"{episode_hash}: DONE")
      except HTTPStatusError as e:
          if e.response.status_code == 401:
              logger.error(f"Invalid API key - Check your API_KEY at the top of the code!: {str(e)}")
          elif e.response.status_code == 400:
              logger.error(f"{episode_hash} - Error 400 : {str(e.response.json())}")
          else:
              logger.error(f"{episode_hash} - Error UNKNOWNn : {str(e)}")
          


def proccess_item(API_KEY, episodeHash, url , castHash, semaphore):
  with semaphore:
    res = download_file(castHash, episodeHash, url)
    if not res:
        print(f"{castHash}\t{episodeHash}: Skip - can't download")
        return
    
    if check_sm_already_exists(castHash, episodeHash):
        print(f"{castHash}\t{episodeHash}: Skip - has already exists")
        return
    get_data_from_speechmatic(castHash, episodeHash, url, API_KEY)



def process(API_KEY):
  data = get_data()

  max_threads = 60
  semaphore = threading.Semaphore(max_threads)
  threads = []

  for row in data:
    episodeHash = row[0]
    url = row[2]
    castHash = row[4]
    thread = threading.Thread(target=proccess_item, args=(API_KEY, episodeHash, url, castHash, semaphore))
    threads.append(thread)
    thread.start()

  for thread in threads:
    thread.join()
  

process(API_KEY)