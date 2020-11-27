import zipfile
import csv
import shutil
import os


def add_extension_if_lacking(filename, extension):
    return filename if filename.endswith(extension) else filename + extension


def normalize_folder_name(folder_name):
    banned = r' \/'
    name = folder_name.strip(banned).lower()
    for b in banned:
        name = name.replace(b, '-')
    return name


def group(args):
    error_counter = 0
    with open(args.meta, 'r') as metadata_file:
        metadata = csv.DictReader(metadata_file)
        metadata_included_files = []
        for row in metadata:
            try:
                image_name = add_extension_if_lacking(row[args.file_col], args.ext)
                metadata_included_files.append(image_name)
                image_path = os.path.join(args.path, image_name)
                if os.path.exists(image_path):
                    label = normalize_folder_name(row[args.label_col])
                    output_path = os.path.join(args.output, label)
                    os.makedirs(output_path, exist_ok=True)
                    shutil.copy(image_path, os.path.join(output_path, image_name))
                else:
                    error_counter += 1
                    print(f"[{error_counter}] Missing file", image_name)
            except Exception as ex:
                error_counter += 1
                print(f"[{error_counter}] Error processing image {image_name}:", ex)
        for file in os.listdir(args.path):
            file = add_extension_if_lacking(file, args.ext)
            if file not in metadata_included_files:
                error_counter += 1
                print(f"[{error_counter}] Missing metadata entry for file", file)
