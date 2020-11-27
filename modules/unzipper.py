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



def unzip_all(args):
    from modules.unzipper import unzip_all
    unzip_all(args.path)





def verify_sha_1(args):
    from modules.verify_sha1 import verify_sha1
    verify_sha1(args.path, args.shafile)





import os
import hashlib


original_hashes = {}

def verify_sha1(folder_path, sha_file):
    with open(sha_file) as file:
        for line in file:
            split_line = line.split()
            original_hashes[split_line[1]] = split_line[0]

    for file in os.listdir(folder_path):
        current_hash = hashlib.sha1()
        try:
            file_hash = original_hashes[file]
            with open(file, 'rb') as source:
                block = source.read(2 ** 16)
                while len(block) != 0:
                    current_hash.update(block)
                    block = source.read(2 ** 16)
            if file_hash == current_hash.hexdigest():
                print(f"Match for file {file}")
            else:
                print(f"HASH MISMATCH! Hash {current_hash} doesn't match with original ({file_hash}). Please re-download {file}")
        except KeyError as ex:
            print(f"Missing original hash for file {file}, skipping")
