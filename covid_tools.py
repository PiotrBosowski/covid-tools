import argparse
import os
import sys
from modules import convert, duplicates, files_puller, modalities, train_test_valid, unzipper


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
    group = parser_bitness_convert.add_mutually_exclusive_group()
    group.add_argument('--simple', help="force simple conversion without histogram evaluation", action="store_true")
    parser_bitness_convert.set_defaults(func=convert.bitness)

    parser_color_flip = bit_converter_subparsers.add_parser('color-flip', help="inverse colors (or grayscale)")
    parser_color_flip.add_argument('--path', required=True, help='path to the image folder')
    parser_color_flip.add_argument('--output', required=False, help='path to the output folder')
    parser_color_flip.add_argument('--ext', required=True, help='images extension')
    parser_color_flip.set_defaults(func=convert.color_flip)

    # DUPLICATES
    parser_duplicates = subparsers.add_parser('duplicates', help="find duplicates and similar images")
    duplicate_subparsers = parser_duplicates.add_subparsers()

    parser_duplicate_folders = duplicate_subparsers.add_parser('compare_folders', help="compare two folders for duplicates")
    parser_duplicate_folders.add_argument('--original', required=True, help='path to the original folder')
    parser_duplicate_folders.add_argument('--newcome', required=True, help='path to the folder you want to join')
    parser_duplicate_folders.add_argument('--sensitivity', required=False, help='0-low, 4-high')
    parser_duplicate_folders.set_defaults(func=duplicates.compare_folders)

    parser_duplicate_finder = duplicate_subparsers.add_parser('find', help="find suplicates within one folder")
    parser_duplicate_finder.add_argument('--path', required=True, help="path to the folder")
    parser_duplicate_finder.add_argument('--sensitivity', required=False, help='0-low, 4-high')
    parser_duplicate_finder.set_defaults(func=duplicates.find_duplicates)

    parser_restore_original_names = duplicate_subparsers.add_parser('restore_names', help="restore original names")
    parser_restore_original_names.add_argument('--path', required=True, help='path to the folder')
    parser_restore_original_names.set_defaults(func=duplicates.restore_original_names)

    # FILES_PULLER
    parser_file_pulling = subparsers.add_parser('files_puller', help="pull files of the same extension from dirtree")
    parser_file_pulling.add_argument('--path', required=True, help="path to the root of the dirtree")
    parser_file_pulling.add_argument('--output', required=True, help="path to the output folder")
    parser_file_pulling.add_argument('--ext', required=True, help="images extension")
    parser_file_pulling.set_defaults(func=files_puller.pull_files)

    # MODALITIES
    parser_modality_splitter = subparsers.add_parser('modality-splitter', help='categorize images by modality')
    parser_modality_splitter.add_argument('--path', required=True, help="folderpath with images to split by modality")
    parser_modality_splitter.add_argument('--ext', required=True, help="images extension")
    parser_modality_splitter.set_defaults(func=modalities.split_by_modality)

    # TRAIN TEST VALID
    parser_train_test_split = subparsers.add_parser('train_test_valid', help="split images into train, test, valid sets")
    parser_train_test_split.add_argument('--path', required=True, help="dataset path")
    parser_train_test_split.add_argument('--test', required=True, help="number of images of test set")
    parser_train_test_split.add_argument('--valid', required=True, help="number of images of validation set")
    parser_train_test_split.add_argument('--labels', nargs='*', required=True, help="labels")
    parser_train_test_split.set_defaults(func=train_test_valid.split)

    # UNZIPPER
    parser_unzip_all = subparsers.add_parser('unzipper', help="unzipp all zipper files within directory")
    parser_unzip_all.add_argument('--path', required=True, help='path to the input folder')
    parser_unzip_all.set_defaults(func=unzipper.unzip_all)

    # VERIFY SHA1
    parser_verify_sha1 = subparsers.add_parser('verify_sha1', help='verify hashes of files in directory')
    parser_verify_sha1.add_argument('--path', required=True, help="path to the input folder")
    parser_verify_sha1.add_argument('--shafile', required=True, help='path to the file containing sha1 hashes')
    parser_verify_sha1.set_defaults(func=unzipper.verify_sha1)

    os.chdir(sys.argv.pop())  # changes script location to the one from which wrapper was called

    arguments = parser_initial.parse_args()
    arguments.func(arguments)
