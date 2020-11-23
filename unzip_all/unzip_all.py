import tarfile
import os


def unzip_all(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".tar.gz"):
            print(f"Unzipping file {file}...")
            tar = tarfile.open(file, "r:gz")
            tar.extractall()
            tar.close()
    print("Done.")
