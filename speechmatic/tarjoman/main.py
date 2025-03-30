
import tarfile
from huggingface_hub import hf_hub_download
import os
import threading
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError
from utils import SingletonLogger
import stamina
import datetime
from huggingface_hub import HfFileSystem
fs = HfFileSystem()


logger = SingletonLogger().get_logger()
API_KEY = input('api key:')

def download_batch(name):
  name_without_ext = (name.split('/')[-1]).split('.')[0]
  hf_hub_download(repo_id="farsi-asr/filimo-chunked-asr-dataset", filename=name, repo_type="dataset", local_dir=f"content")
  tar = tarfile.open("content/" + name)
  tar.extractall(path=f"content/{name_without_ext}/")
  tar.close()
  print("batch " + name + " downloaded")



def write_to_output(data, output):
  with open(output, 'w') as f:
    f.write(str(data))

def check_already_exists(predestination, audioName):
  audioName = audioName.split('.')[0]
  return os.path.exists(f"content/{predestination}/{audioName}.sm.json")


@stamina.retry(attempts=3)
def get_data_from_speechmatic(predestination, audioName, API_KEY):
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
              audio=f"content/{predestination}/{audioName}",
              transcription_config=conf,
          )
          print(f'\t{audioName}: job {job_id} submitted successfully, waiting for transcript')
          transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
          write_to_output(transcript, f"content/{predestination}/{audioName.split('.')[0]}.sm.json")
          print(f'\t{audioName}: DONE')
          logger.info(f"{audioName}: DONE")
      except HTTPStatusError as e:
          if e.response.status_code == 401:
              logger.error(f"Invalid API key - Check your API_KEY at the top of the code!: {str(e)}")
          elif e.response.status_code == 400:
              logger.error(f"{audioName} - Error 400 : {str(e.response.json())}")
          else:
              logger.error(f"{audioName} - Error UNKNOWNn : {str(e)}")
    


def proccess_item(predestination, audioName, API_KEY, DIRECTORY_INDEX, semaphore):
  with semaphore:
    if check_already_exists(predestination, audioName):
        print(f"{DIRECTORY_INDEX}\t{audioName}: Skip - has already exists")
        return
    get_data_from_speechmatic(predestination, audioName,API_KEY, DIRECTORY_INDEX)

def proccess_batch(name, semaphore):
    with semaphore:
        download_batch(name)
        name_without_ext = (name.split('/')[-1]).split('.')[0]
        for root, dirs, files in os.walk(f'content/{name_without_ext}'):
            print(f"Directory: {root}")
            DIRECTORY_INDEX = DIRECTORY_INDEX + 1
            max_threads = 60
            semaphore = threading.Semaphore(max_threads)
            threads = []
            for file in files:
                if "mp3" in file:
                    thread = threading.Thread(target=proccess_item, args=(name_without_ext, file, API_KEY, DIRECTORY_INDEX, semaphore))
                    threads.append(thread)
                    thread.start()
                
            for thread in threads:
                thread.join()


def proccess():
    max_threads = 1
    semaphore = threading.Semaphore(max_threads)
    threads = []
    fileList = fs.ls("datasets/farsi-asr/PerSets-tarjoman-chunked", detail=True)
    for file in fileList:
        if ".tar.gz" in file['name'] and file['last_commit'].date.replace(tzinfo=datetime.timezone.utc) < datetime.datetime(2025, 3, 30, 0,0,0, tzinfo=datetime.timezone.utc):
            thread = threading.Thread(target=proccess_batch, args=(file['name'].split('/')[-1], semaphore))
            threads.append(thread)
            thread.start()
            print(file)
    for thread in threads:
        thread.join()

proccess()