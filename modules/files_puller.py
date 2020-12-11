import os
import shutil


def pull_files(args):
    pull_files_impl(args.path, args.output, args.ext)


def pull_files_impl(input_folder, output_folder, extension):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(extension):
                shutil.move(os.path.join(root, file), os.path.join(output_folder, file))

