
import tarfile
import shutil
from huggingface_hub import hf_hub_download
import os
import threading
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError, HTTPError
from utils import SingletonLogger
import stamina
import datetime
from huggingface_hub import HfFileSystem
from huggingface_hub import HfApi

api = HfApi()
fs = HfFileSystem()

logger = SingletonLogger().get_logger()
API_KEY = input('api key:')

def download_batch(name):
  name_without_ext = (name.split('/')[-1]).split('.')[0]
  hf_hub_download(repo_id="farsi-asr/PerSets-tarjoman-chunked", filename=name, repo_type="dataset", local_dir=f"content")
  tar = tarfile.open("content/" + name)
  tar.extractall(path=f"content/")
  tar.close()
  print("batch " + name + " downloaded")

def count_all_subfolders_os_walk(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory.")
        return -1

    count = 0
    for root, dirnames, filenames in os.walk(directory_path):
        count += len(dirnames)
    return count

def rename_old_tar(filename):
    filename = filename + ".tar.gz"
    os.rename(f"./content/{filename}", f"./content/{filename}.old")

def create_tar_gz(output_filename, source_dir):
    try:
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        print(f"Successfully created {output_filename}")
    except FileNotFoundError:
        print(f"Error: Directory '{source_dir}' not found.")
    except Exception as e:
        print(f"An error occured: {e}")




def write_to_output(data, output):
  with open(output, 'w') as f:
    f.write(str(data))

def check_already_exists(predestination, audioName):
  audioName = audioName.split('.')[0]
  return os.path.exists(f"content/{predestination}/{audioName}.sm.json")


@stamina.retry(on=HTTPError, attempts=3)
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
    


def proccess_item(predestination, audioName, API_KEY, semaphore):
  with semaphore:
    if check_already_exists(predestination, audioName):
        # print(f"\t{audioName}: Skip - has already exists")
        return
    get_data_from_speechmatic(predestination, audioName,API_KEY)

def proccess_batch(name, semaphore):
    with semaphore:
        print(f"proccess: {name}")
        download_batch(name)
        name_without_ext = (name.split('/')[-1]).split('.')[0]
        lastFilesCount = count_all_subfolders_os_walk(f'content/{name_without_ext}')
        for root, dirs, files in os.walk(f'content/{name_without_ext}'):
            print(f"Directory: {root}")
            max_threads = 5
            semaphore = threading.Semaphore(max_threads)
            threads = []
            for file in files:
                if "mp3" in file:
                    thread = threading.Thread(target=proccess_item, args=(name_without_ext, file, API_KEY, semaphore))
                    threads.append(thread)
                    thread.start()
                
            for thread in threads:
                thread.join()

        # rename_old_tar(name_without_ext)
        if count_all_subfolders_os_walk(f'content/{name_without_ext}') == lastFilesCount:
            print(f"proccess: {name} - no new files found, skipping")
            shutil.rmtree(f"./content/{name_without_ext}")
            return
        else:
            create_tar_gz(f"./content/{name_without_ext}.tar.gz", f"./content/{name_without_ext}")
            api.upload_file(
                path_or_fileobj=f"./content/{name_without_ext}.tar.gz",
                path_in_repo=f"{name_without_ext}.tar.gz",
                repo_id="farsi-asr/PerSets-tarjoman-chunked",
                repo_type="dataset",
            )
        
        shutil.rmtree(f"./content/{name_without_ext}")
        os.remove(f"./content/{name_without_ext}.tar.gz")


def proccess():
    max_threads = 2
    semaphore = threading.Semaphore(max_threads)
    threads = []
    fileList = fs.ls("datasets/farsi-asr/PerSets-tarjoman-chunked", detail=True)
    for file in fileList:
        if ".tar.gz" in file['name'] and file['last_commit'].date.replace(tzinfo=datetime.timezone.utc) < datetime.datetime(2025, 5, 24, 0,0,0, tzinfo=datetime.timezone.utc):
            thread = threading.Thread(target=proccess_batch, args=(file['name'].split('/')[-1], semaphore))
            threads.append(thread)
            thread.start()
    for thread in threads:
        thread.join()

proccess()