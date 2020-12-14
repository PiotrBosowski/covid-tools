import os
import shutil


def pull_files(args):
    """
    File pulling wrapper. See pull_files_impl.
    """
    pull_files_impl(args.path, args.output, args.ext)


def pull_files_impl(input_folder, output_folder, extension):
    """
    Pull files of certain extension from a dirtree that starts in a
    input_folder and saves them to output_folder. Warning: shutil.move
    is used instead of shutil.copy.
    :param input_folder: start of the dirtree
    :param output_folder: output path
    :param extension: extension of files to be pulled
    """
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(extension):
                shutil.move(os.path.join(root, file),
                            os.path.join(output_folder, file))

