import os
import shutil


def pull_files(args):
    from modules.files_puller import pull_files
    pull_files(args.path, args.output, args.ext)




def pull_files(input_folder, output_folder, extension):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(extension):
                shutil.move(os.path.join(root, file), os.path.join(output_folder, file))
