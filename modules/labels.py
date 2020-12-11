import csv
import shutil
import os


def add_extension_if_lacking(filename, extension):
    """
    Adds extension to the filename if it doesn't already end with it.
    """
    return filename if filename.endswith(extension) else filename + extension


def normalize_folder_name(folder_name):
    """
    Normalizes folder name, removing banned characters and sriping it.
    :param folder_name: name to be normalized
    :return: normalized name
    """
    banned = r' \/'
    name = folder_name.strip(banned).lower()
    for b in banned:
        name = name.replace(b, '-')
    return name


def group_labels(args):
    """
    Group labels wrapper. See group_labels_impl().
    """
    group_labels_impl(args.meta, args.path, args.output, args.file_col,
                      args.label_col, args.ext)


def group_labels_impl(meta, path, output, file_col, label_col, ext):
    """
    Groups data by its label, according to a csv metadata file.
    :param meta: path to the csv metadata file
    :param path: path to the data folder
    :param output: output path
    :param file_col: name of the csv column that contains file names
    :param label_col: name of the csv column that contains label names
    :param ext: extension of the data
    """
    error_counter = 0
    with open(meta, 'r') as metadata_file:
        metadata = csv.DictReader(metadata_file)
        metadata_included_files = []
        for row in metadata:
            try:
                image_name = add_extension_if_lacking(row[file_col], ext)
                metadata_included_files.append(image_name)
                image_path = os.path.join(path, image_name)
                if os.path.isfile(image_path):
                    label = normalize_folder_name(row[label_col])
                    output_path = os.path.join(output, label)
                    os.makedirs(output_path, exist_ok=True)
                    shutil.copy(image_path,
                                os.path.join(output_path, image_name))
                else:
                    error_counter += 1
                    print(f"[{error_counter}] Missing file", image_name)
            except Exception as ex:
                error_counter += 1
                print(f"[{error_counter}] Error processing image "
                      f"{image_name}:", ex)
        for file in os.listdir(path):
            file = add_extension_if_lacking(file, ext)
            if file not in metadata_included_files:
                error_counter += 1
                print(f"[{error_counter}] Missing metadata entry for file",
                      file)
