import tarfile
from huggingface_hub import hf_hub_download

def download_batch(batchnumber, filename = "batch_"):
  filename = filename + batchnumber + ".tar.gz"
  hf_hub_download(repo_id="farsi-asr/filimo-chunked-asr-dataset", filename=filename, repo_type="dataset", local_dir="content")
  tar = tarfile.open("content/" + filename)
  tar.extractall(path="content/")
  tar.close()
  print("batch " + batchnumber + " downloaded")

download_batch(input("Enter batch number: "))