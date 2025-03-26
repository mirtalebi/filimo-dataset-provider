import tarfile
from huggingface_hub import hf_hub_download

def download_batch(batch_name):
  filename = batch_name + ".tar.gz"
  hf_hub_download(repo_id="farsi-asr/filimo-chunked-asr-dataset", filename=filename, repo_type="dataset", local_dir="content")
  tar = tarfile.open("content/" + filename)
  tar.extractall(path="content/")
  tar.close()
  print("batch " + batch_name + " downloaded")



try:
  with open("batch_name.txt", "r") as file:
    batch_name = file.read().strip()
    download_batch(batch_name)

except FileNotFoundError:
  print("Error: batch_name.txt not found.")
  


