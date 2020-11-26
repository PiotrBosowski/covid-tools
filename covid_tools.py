#!C:\ProgramData\Anaconda3\python.exe
import argparse
import os
import sys


def convert_bitness(args):
    from bit_converter.bit_converter import convert_all, convert_image_simple, convert_image_smart
    convert_all(args.input, args.output, args.ext, convert_image_simple if args.simple else convert_image_smart)


def flip_colors_wrapper(args):
    from bit_converter.bit_converter import convert_all, flip_colors
    convert_all(args.path, args.output, args.ext, flip_colors)


def compare_folders(args):
    from duplicate_finder.duplicate_finder import compare_folders
    compare_folders(args.original, args.newcome, args.sensitivity)


def find_duplicates(args):
    from duplicate_finder.duplicate_finder import delete_duplicates
    delete_duplicates(args.path, args.sensitivity)


def restore_original_names(args):
    from duplicate_finder.duplicate_finder import restore_original_names
    restore_original_names(args.path)


def pull_files(args):
    from files_puller.files_puller import pull_files
    pull_files(args.path, args.output, args.ext)


def train_test_split(args):
    from train_test_split.train_test_split import split_into_train_test_valid
    split_into_train_test_valid(args.path, args.test, args.valid, args.labels)


def unzip_all(args):
    from unzip_all.unzip_all import unzip_all
    unzip_all(args.path)


def verify_sha_1(args):
    from verify_sha1.verify_sha1 import verify_sha1
    verify_sha1(args.path, args.shafile)


def split_by_modality(args):
    from modality_splitter.modality_splitter import split_dataset_by_modality
    split_dataset_by_modality(args.path, args.ext)


if __name__ == '__main__':
    parser_initial = argparse.ArgumentParser()
    subparsers = parser_initial.add_subparsers()

    ### BIT CONVERSIONS
    parser_bit_convert = subparsers.add_parser('convert', help="bit_convert help")
    bit_converter_subparsers = parser_bit_convert.add_subparsers()

    parser_bitness_convert = bit_converter_subparsers.add_parser('bitness', help='convert bitness help')
    parser_bitness_convert.add_argument('--input', required=True, help="path to the folder with images to convert")
    parser_bitness_convert.add_argument('--output', required=True, help="path to the folder with converted images")
    parser_bitness_convert.add_argument('--ext', required=True, help="image_extension")
    group = parser_bitness_convert.add_mutually_exclusive_group()
    group.add_argument('--simple', help="force simple conversion without histogram evaluation", action="store_true")
    parser_bitness_convert.set_defaults(func=convert_bitness)

    parser_color_flip = bit_converter_subparsers.add_parser('color-flip', help="color-flip help")
    parser_color_flip.add_argument('--path', required=True, help='path to the image folder')
    parser_color_flip.add_argument('--output', required=False, help='path to the output')
    parser_color_flip.add_argument('--ext', required=True, help='images extension')
    parser_color_flip.set_defaults(func=flip_colors_wrapper)


    ### DUPLICATES
    parser_duplicates = subparsers.add_parser('duplicates', help="duplicate_finder help")
    duplicate_subparsers = parser_duplicates.add_subparsers()

    parser_duplicate_folders = duplicate_subparsers.add_parser('compare_folders', help="compare_folders help")
    parser_duplicate_folders.add_argument('--original', required=True, help='path to the original folder')
    parser_duplicate_folders.add_argument('--newcome', required=True, help='path to the folder you want to join')
    parser_duplicate_folders.add_argument('--sensitivity', required=False, help='sensitivity of detection')
    parser_duplicate_folders.set_defaults(func=compare_folders)

    parser_duplicate_finder = duplicate_subparsers.add_parser('find', help="find duplicates help")
    parser_duplicate_finder.add_argument('--path', required=True, help="path to the folder with images to analyse")
    parser_duplicate_finder.add_argument('--sensitivity', required=False, help='sensitivity of detection')
    parser_duplicate_finder.set_defaults(func=find_duplicates)

    parser_restore_original_names = duplicate_subparsers.add_parser('restore_names', help="restore original names help")
    parser_restore_original_names.add_argument('--path', required=True, help='path to the images folder')
    parser_restore_original_names.set_defaults(func=restore_original_names)

    ### PULL FILES
    parser_file_pulling = subparsers.add_parser('files_puller', help="files_puller help")
    parser_file_pulling.add_argument('--path', required=True, help="path to the folder containing images")
    parser_file_pulling.add_argument('--output', required=True, help="path to the folder with pulled images")
    parser_file_pulling.add_argument('--ext', required=True, help="image_extension")
    parser_file_pulling.set_defaults(func=pull_files)

    ### TRAIN TEST SPLIT
    parser_train_test_split = subparsers.add_parser('train_test_split', help="train_test_split help")
    parser_train_test_split.add_argument('--path', required=True, help="dataset path")
    parser_train_test_split.add_argument('--test', required=True, help="number of images of test set")
    parser_train_test_split.add_argument('--valid', required=True, help="number of images of validation set")
    parser_train_test_split.add_argument('--labels', nargs='*', required=True, help="set of classes you want to include")
    parser_train_test_split.set_defaults(func=train_test_split)

    ### UNZIP_ALL
    parser_unzip_all = subparsers.add_parser('unzip_all', help="unzip all help")
    parser_unzip_all.add_argument('--path', required=True, help='path to the folder containing archives')
    parser_unzip_all.set_defaults(func=unzip_all)

    ### VERIFY SHA1
    parser_verify_sha1 = subparsers.add_parser('verify_sha1', help='verify sha1 help')
    parser_verify_sha1.add_argument('--path', required=True, help="path to the folder containing files")
    parser_verify_sha1.add_argument('--shafile', required=True, help='path to the file containing sha1 hashes')
    parser_verify_sha1.set_defaults(func=verify_sha_1)

    ### MODALITY SPLITTER
    parser_modality_splitter = subparsers.add_parser('modality-splitter', help='modality-splitter help')
    parser_modality_splitter.add_argument('--path', required=True, help="folderpath with images to split by modality")
    parser_modality_splitter.add_argument('--ext', required=True, help="images extension")
    parser_modality_splitter.set_defaults(func=split_by_modality)

    os.chdir(sys.argv.pop())  # changes script location to the one from which wrapper was called

    arguments = parser_initial.parse_args()
    arguments.func(arguments)

