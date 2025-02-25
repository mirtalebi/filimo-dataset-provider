import shutil
import os

def archive_folder(folder_path, output_filename):
    archive_path = shutil.make_archive(output_filename, 'gztar', folder_path)
    print(f"Folder archived successfully: {archive_path}")
    return archive_path


def list_directories(path="."):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def move_directory(source, destination):
    new_path = shutil.move(source, destination)
    print(f"Directory moved to: {new_path}")
    return new_path

# Example usage
directories = list_directories("../../ganjoor")
for directoryPath in directories:
    archive_folder("../../ganjoor/" + directoryPath, "../../ganjoor/" + directoryPath)
    move_directory("../../ganjoor/" + directoryPath, "../../ganjoor-raw/")
