import imagehash
import os
import hashlib
import shutil
import re
from PIL import Image


def compare_folders(args):
    compare_folders_impl(args.original, args.newcome, args.sensitivity)


def find_duplicates(args):
    delete_duplicates(args.path, args.hash_size, args.hf_factor, args.skip_strict)


def restore_original_names(args):
    restore_original_names(args.path)


def calculate_strict_hash(file):
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    while True:
        data = file.read(BUF_SIZE)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()


def delete_strict_duplicates(image_dir):
    """
    Deletes files with identical hashes (leaving only one copy). It is
    safe to run multiple times (but can be quite time consuming).
    :param image_dir: path to the directory containing images
    """
    images = {}
    for image in os.listdir(image_dir):
        if os.path.isfile(os.path.join(image_dir, image)):
            with open(os.path.join(image_dir, image), 'rb') as f:
                images[image] = calculate_strict_hash(f)
    dupl_counter = 0
    flipped = {}
    for key, value in images.items():
        if value not in flipped:
            flipped[value] = key
        else:
            dupl_counter += 1
            os.remove(os.path.join(image_dir, key))
            print(f"[{dupl_counter}] Strictly duplicated images: {key}, "
                  f"{flipped[value]}. The latter has been removed.")
    print(f"Found {dupl_counter} strict duplicates.")


def restore_original_names(image_dir):
    """
    Restores original names, removing DUPLICATE_(...) from the beginning
    of affected files.
    :param image_dir: path to images folder
    """
    pattern = r'DUPLICATE_[\d]*_(ORIG|DUPL)_'
    counter = 0
    for image in os.listdir(image_dir):
        new_name = re.sub(pattern, '', image)
        if new_name != image:
            counter += 1
            shutil.move(os.path.join(image_dir, image),
                        os.path.join(image_dir, new_name))
            print(f"[{counter}] Renaming [{image}] back to [{new_name}]")

def delete_duplicates(image_dir, hash_size, highfreq_factor, skip_strict):
    """
    Detects duplicates and moves them to 'duplicates' folder. Originals
    are also copied to the folder for easier visual comparison. Uses
    pHash algorithm (info below).
    http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    :param image_dir:
    """
    if not skip_strict:
        delete_strict_duplicates(image_dir)
    counter = 0
    print(f"[hash_size={hash_size}]"
          f"[highfreq_factor={highfreq_factor}]")
    images = {}
    for ind, image in enumerate(sorted(os.listdir(image_dir))):
        print(ind)
        if os.path.isfile(os.path.join(image_dir, image)):
            images[image] = imagehash.phash(
                Image.open(os.path.join(image_dir, image)),
                hash_size=hash_size, highfreq_factor=highfreq_factor)
    flipped = {}
    duplicates_path = os.path.join(image_dir, 'duplicates')
    os.makedirs(duplicates_path, exist_ok=True)
    for key, value in images.items():
        if value not in flipped:
            flipped[value] = key
        else:
            counter += 1
            print(f"[hash_size={hash_size}][highfreq_factor="
                  f"{highfreq_factor}][no. {counter}] Similar images:"
                  f"   {flipped[value]}   {key}")
            shutil.copy(os.path.join(image_dir, flipped[value]),
                        os.path.join(
                            duplicates_path,
                            f'DUPLICATE_{counter}_ORIG_'
                            + flipped[value]))
            shutil.move(os.path.join(image_dir, key),
                        os.path.join(
                            duplicates_path,
                            f'DUPLICATE_{counter}_DUPL_' + key))


def compare_folders_impl(dir_a, dir_b, sensitivity):
    """
    Compares two folders looking for images in dir_b that already exists
    in dir_a. When such image is found, it is moved to the
    'dir_b/duplicates' folder along with a copy of the original picture
    from dir_a. Afterwards dir_b contains only new files and all
    duplicates can be reviewed conveniently in 'dir_b/duplicates'
    folder. It is recommended to clear both folders with
    'delete_duplicates' function prior to comparing the folders.
    :param source_dir: source_dir
    :param compared_dir: dir to be joined
    """
    counter = 0
    for hash_size in [16]:
        for highfreq_factor in [3]:
            print(f"[hash_size={hash_size}]"
                  f"[highfreq_factor={highfreq_factor}]")
            hashes_a = {imagehash.phash(Image.open(os.path.join(dir_a, image)),
                                        hash_size=hash_size,
                                        highfreq_factor=highfreq_factor):
                            image for image in sorted(os.listdir(dir_a))
                        if os.path.isfile(os.path.join(dir_a, image))}
            hashes_b = {imagehash.phash(Image.open(os.path.join(dir_b, image)),
                                        hash_size=hash_size,
                                        highfreq_factor=highfreq_factor):
                            image for image in sorted(os.listdir(dir_b))
                        if os.path.isfile(os.path.join(dir_b, image))}
            duplicates_path = os.path.join(dir_b, 'duplicates')
            os.makedirs(duplicates_path, exist_ok=True)
            for key, value in hashes_b.items():
                if key in hashes_a:
                    counter += 1
                    print(f"[hash_size={hash_size}][highfreq_factor="
                          f"{highfreq_factor}][no. {counter}] Similar images:"
                          f"   {hashes_a[key]}   {hashes_b[key]}")
                    shutil.copy(os.path.join(dir_a, hashes_a[key]),
                                os.path.join(duplicates_path,
                                             f'DUPLICATE_{counter}_ORIG_'
                                             + hashes_a[key]))
                    shutil.move(os.path.join(dir_b, hashes_b[key]),
                                os.path.join(duplicates_path,
                                             f'DUPLICATE_{counter}_DUPL_'
                                             + hashes_b[key]))

