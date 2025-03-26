import tarfile
import os
from huggingface_hub import HfApi

api = HfApi()
batch_number = input("Enter batch number: ")


def rename_old_tar(batchnumber, filename = "batch_"):
    filename = filename + batchnumber + ".tar.gz"
    os.rename("./content/" + filename, "./content/" + filename + '.old')
   

def rename_old_tar(batchnumber, filename = "batch_"):
    filename = filename + batchnumber + ".tar.gz"
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
folder_to_compress = "./content/filimo"  # Replace with the actual folder name
output_tar_gz = f"./content/batch_{batch_number}.tar.gz"

rename_old_tar(batch_number)
create_tar_gz(output_tar_gz, folder_to_compress)


api.upload_file(
    path_or_fileobj=output_tar_gz,
    path_in_repo=f"batch_{batch_number}.tar.gz",
    repo_id="mirtalebi/filimo-speechmatic",
    repo_type="dataset",
)