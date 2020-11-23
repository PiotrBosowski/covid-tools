import imagehash
import os
import hashlib
import shutil
from PIL import Image


def delete_strict_duplicates(image_dir):
    """
    Deletes files with identical hashes (leaving only one copy). It is safe to run multiple times.
    :param image_dir: path to the directory containing images
    """
    BUF_SIZE = 65536
    images = {}
    for image in os.listdir(image_dir):
        if os.path.isfile(os.path.join(image_dir, image)):
            with open(os.path.join(image_dir, image), 'rb') as f:
                md5 = hashlib.md5()
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    md5.update(data)
                images[image] = md5.hexdigest()
    duplicated_counter = 0
    flipped = {}
    for key, value in images.items():
        if value not in flipped:
            flipped[value] = key
        else:
            duplicated_counter += 1
            os.remove(os.path.join(image_dir, key))
            print(f"[{duplicated_counter}] Strictly duplicated images: {key}, {flipped[value]}. The latter has been removed.")
    print(f"Found {duplicated_counter} strict duplicates.")


def delete_duplicates(image_dir, sensitivity):
    """
    Detects duplicates and moves them to 'duplicates' folder. Originals are also copied to the folder for easier visual
    comparison. Uses pHash algorithm (info below).
    http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    :param image_dir:
    """
    delete_strict_duplicates(image_dir)
    counter = 0
    for hash_size in [12, 6]:
        for highfreq_factor in [3, 2]:
            print(f"[hash_size={hash_size}][highfreq_factor={highfreq_factor}]")
            images = {}
            for image in sorted(os.listdir(image_dir)):
                if os.path.isfile(os.path.join(image_dir, image)):
                    images[image] = imagehash.phash(Image.open(os.path.join(image_dir, image)), hash_size=hash_size, highfreq_factor=highfreq_factor)
            flipped = {}
            duplicates_path = os.path.join(image_dir, 'duplicates')
            os.makedirs(duplicates_path, exist_ok=True)
            for key, value in images.items():
                if value not in flipped:
                    flipped[value] = key
                else:
                    counter += 1
                    print(f"[hash_size={hash_size}][highfreq_factor={highfreq_factor}][no. {counter}] Similar images:   {flipped[value]}   {key}")
                    shutil.copy(os.path.join(image_dir, flipped[value]),
                                os.path.join(duplicates_path, f'DUPLICATE_{counter}_ORIG_' + flipped[value]))
                    shutil.move(os.path.join(image_dir, key),
                                os.path.join(duplicates_path, f'DUPLICATE_{counter}_DUPL_' + key))


def compare_folders(dir_a, dir_b, sensitivity):
    """
    Compares two folders looking for images in dir_b that already exists in dir_a. When such image is found, it is moved
    to the 'dir_b/duplicates' folder along with a copy of the original picture from dir_a. Afterwards dir_b contains
    only new files and all duplicates can be reviewed conveniently in 'dir_b/duplicates' folder. It is recommended to
    clear both folders with 'delete_duplicates' function prior to comparing the folders.
    :param source_dir:
    :param compared_dir:
    """
    counter = 0
    for hash_size in [12, 6]:
        for highfreq_factor in [3, 2]:
            print(f"[hash_size={hash_size}][highfreq_factor={highfreq_factor}]")
            hashes_a = {}
            hashes_b = {}
            for image in sorted(os.listdir(dir_a)):
                if os.path.isfile(os.path.join(dir_a, image)):
                    hash = imagehash.phash(Image.open(os.path.join(dir_a, image)), hash_size=hash_size,
                                                    highfreq_factor=highfreq_factor)
                    hashes_a[hash] = image
            for image in sorted(os.listdir(dir_b)):
                if os.path.isfile(os.path.join(dir_b, image)):
                    hash = imagehash.phash(Image.open(os.path.join(dir_b, image)), hash_size=hash_size,
                                                    highfreq_factor=highfreq_factor)
                    hashes_b[hash] = image

            duplicates_path = os.path.join(dir_b, 'duplicates')
            os.makedirs(duplicates_path, exist_ok=True)
            for key, value in hashes_b.items():
                if key in hashes_a:
                    counter += 1
                    print(f"[hash_size={hash_size}][highfreq_factor={highfreq_factor}][no. {counter}] Similar images:   {hashes_a[key]}   {hashes_b[key]}")
                    shutil.copy(os.path.join(dir_a, hashes_a[key]),
                                os.path.join(duplicates_path, f'DUPLICATE_{counter}_ORIG_' + hashes_a[key]))
                    shutil.move(os.path.join(dir_b, hashes_b[key]),
                                os.path.join(duplicates_path, f'DUPLICATE_{counter}_DUPL_' + hashes_b[key]))

actual_folder = r'data\converted'
delete_duplicates(actual_folder)
#compare_folders(r'c:\users\piotr\desktop\covid-combined-database\data\cr\ap-pa\covid', actual_folder)
