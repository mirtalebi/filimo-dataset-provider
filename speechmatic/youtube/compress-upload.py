import tarfile
import os
from huggingface_hub import HfApi

api = HfApi()
batch_name = ''
try:
  with open("batch_name.txt", "r") as file:
    batch_name = file.read().strip()

except FileNotFoundError:
  print("Error: batch_name.txt not found.")

def rename_old_tar():
    filename = batch_name + ".tar.gz"
    os.rename("./content/" + filename, "./content/" + filename + '.old')


def create_tar_gz(output_filename, source_dir):
    try:
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        print(f"Successfully created {output_filename}")
    except FileNotFoundError:
        print(f"Error: Directory '{source_dir}' not found.")
    except Exception as e:
        print(f"An error occured: {e}")



# Example usage:
folder_to_compress = f"./content/{batch_name}"  # Replace with the actual folder name
output_tar_gz = f"./content/{batch_name}.tar.gz"

rename_old_tar()
create_tar_gz(output_tar_gz, folder_to_compress)


api.upload_file(
    path_or_fileobj=output_tar_gz,
    path_in_repo=f"{batch_name}.tar.gz",
    repo_id="farsi-asr/farsi-youtube-asr-dataset",
    repo_type="dataset",
)