import argparse
import os
import sys
from modules.convert import bitness, color_flip, extension
from modules.duplicates import compare_folders_impl, find_duplicates, restore_original_names
from modules.files_puller import pull_files
from modules.labels import group_labels
from modules.modalities import split_by_modality
from modules.unzipper import unzip_all, verify_sha1_impl


if __name__ == '__main__':
    parser_initial = argparse.ArgumentParser()
    parser_initial.set_defaults(func=lambda args: parser_initial.print_help())
    subparsers = parser_initial.add_subparsers()

    # CONVERT
    parser_bit_convert = subparsers.add_parser('convert', help="file conversions")
    bit_converter_subparsers = parser_bit_convert.add_subparsers()

    parser_bitness_convert = bit_converter_subparsers.add_parser('bitness', help='bitness conversions')
    parser_bitness_convert.add_argument('--input', required=True, help="path to the folder with input images")
    parser_bitness_convert.add_argument('--output', required=True, help="path to the output folder")
    parser_bitness_convert.add_argument('--ext', required=True, help="images extension")
    parser_bitness_convert.add_argument('--simple', help="force simple conversion without histogram evaluation", action="store_true")
    parser_bitness_convert.set_defaults(func=bitness)

    parser_color_flip = bit_converter_subparsers.add_parser('color-flip', help="inverse colors (or grayscale)")
    parser_color_flip.add_argument('--path', required=True, help='path to the image folder')
    parser_color_flip.add_argument('--output', required=True, help='path to the output folder')
    parser_color_flip.add_argument('--ext', required=True, help='images extension')
    parser_color_flip.set_defaults(func=color_flip)

    parser_extension = bit_converter_subparsers.add_parser('format', help="changes the format of all files within directory")
    parser_extension.add_argument('--path', required=True, help='path to the image folder')
    parser_extension.add_argument('--output', required=True, help='path to the output folder')
    parser_extension.add_argument('--ext-in', required=True, help='input extension')
    parser_extension.add_argument('--ext-out', required=True, help='output extension')
    parser_extension.set_defaults(func=extension)

    # DUPLICATES
    parser_duplicates = subparsers.add_parser('duplicates', help="find duplicates and similar images")
    duplicate_subparsers = parser_duplicates.add_subparsers()

    parser_duplicate_folders = duplicate_subparsers.add_parser('compare-folders', help="compare two folders for duplicates")
    parser_duplicate_folders.add_argument('--original', required=True, help='path to the original folder')
    parser_duplicate_folders.add_argument('--newcome', required=True, help='path to the folder you want to join')
    parser_duplicate_folders.add_argument('--sensitivity', required=False, help='0-low, 4-high')
    parser_duplicate_folders.set_defaults(func=compare_folders_impl)

    parser_duplicate_finder = duplicate_subparsers.add_parser('find', help="find suplicates within one folder")
    parser_duplicate_finder.add_argument('--path', required=True, help="path to the folder")
    parser_duplicate_finder.add_argument('--hash-size', required=True, help="size of an image hash")
    parser_duplicate_finder.add_argument('--hf-factor', required=True, help="highfreq factor")
    parser_duplicate_finder.add_argument('--skip-strict', help="skips calculating regular hashes", action="store_true")
    parser_duplicate_finder.set_defaults(func=find_duplicates)

    parser_restore_original_names = duplicate_subparsers.add_parser('restore_names', help="restore original names")
    parser_restore_original_names.add_argument('--path', required=True, help='path to the folder')
    parser_restore_original_names.set_defaults(func=restore_original_names)

    # FILES_PULLER
    parser_file_pulling = subparsers.add_parser('files-puller', help="pull files of the same extension from dirtree")
    parser_file_pulling.add_argument('--path', required=True, help="path to the root of the dirtree")
    parser_file_pulling.add_argument('--output', required=True, help="path to the output folder")
    parser_file_pulling.add_argument('--ext', required=True, help="images extension")
    parser_file_pulling.set_defaults(func=pull_files)

    # LABELS
    parser_labels = subparsers.add_parser('labels', help="split files to folders according to their labels")
    parser_labels.add_argument('--path', required=True, help='path to the images folder')
    parser_labels.add_argument('--meta', required=True, help='metadata file')
    parser_labels.add_argument('--output', required=True, help='output folder')
    parser_labels.add_argument('--label-col', required=True, help='column that holds labels')
    parser_labels.add_argument('--file-col', required=True, help='column that holds filenames')
    parser_labels.add_argument('--ext', required=True, help='images extension')
    # OPTIONAL: TODO DRY RUN
    parser_labels.set_defaults(func=group_labels)

    # MODALITIES
    parser_modality_splitter = subparsers.add_parser('modality-splitter', help='categorize images by modality')
    parser_modality_splitter.add_argument('--path', required=True, help="folderpath with images to split by modality")
    parser_modality_splitter.add_argument('--ext', required=True, help="images extension")
    parser_modality_splitter.set_defaults(func=split_by_modality)

    # TRAIN TEST VALID
    parser_train_test_split = subparsers.add_parser('train-test-valid', help="split images into train, test, valid sets")
    parser_train_test_split.add_argument('--path', required=True, help="dataset path")
    parser_train_test_split.add_argument('--output', required=True, help="output path")
    parser_train_test_split.add_argument('--train', required=True, help="number of images of test set (-1 = all remaining)")
    parser_train_test_split.add_argument('--test', required=True, help="number of images of test set (-1 = all remaining)")
    parser_train_test_split.add_argument('--valid', required=True, help="number of images of validation set (-1 = all remaining)")
    parser_train_test_split.add_argument('--allow-imbalanced-remainings', help="forces -1 mode to ignore class balancing and include all remaining images", action="store_true")
    parser_train_test_split.add_argument('--labels', nargs='*', required=True, help="labels")
    parser_train_test_split.set_defaults(func=split)

    # UNZIPPER
    parser_unzip_all = subparsers.add_parser('unzipper', help="unzipp all zipper files within directory")
    parser_unzip_all.add_argument('--path', required=True, help='path to the input folder')
    parser_unzip_all.set_defaults(func=unzip_all)

    # VERIFY SHA1
    parser_verify_sha1 = subparsers.add_parser('verify_sha1', help='verify hashes of files in directory')
    parser_verify_sha1.add_argument('--path', required=True, help="path to the input folder")
    parser_verify_sha1.add_argument('--shafile', required=True, help='path to the file containing sha1 hashes')
    parser_verify_sha1.set_defaults(func=verify_sha1_impl)

    os.chdir(sys.argv.pop())  # changes script location to the one from which wrapper was called

    arguments = parser_initial.parse_args()
    arguments.func(arguments)
