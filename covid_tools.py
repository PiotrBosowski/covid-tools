#!python
import argparse


def convert_bitness(args):
    from bit_converter import bit_converter
    bit_converter.convert_all(args.input,
                              args.output,
                              args.ext,
                              bit_converter.convert_image_smart if args.smart else bit_converter.convert_image_simple)


def compare_folders(args):
    from duplicate_finder import duplicate_finder
    duplicate_finder.compare_folders(args.original, args.newcome, args.sensitivity)


def find_duplicates(args):
    from duplicate_finder import duplicate_finder
    duplicate_finder.delete_duplicates(args.path, args.sensitivity)


def pull_files(args):
    from files_puller import files_puller
    files_puller.pull_files(args.path, args.output, args.ext)


def train_test_split(args):
    from train_test_split.train_test_split import split_into_train_test_valid
    split_into_train_test_valid(args.path, args.test, args.valid, args.labels)


def unzip_all(args):
    from unzip_all import unzip_all
    unzip_all.unzip_all(args.path)


def verify_sha_1(args):
    from verify_sha1 import verify_sha1
    verify_sha1.verify_sha1(args.path, args.shafile)


if __name__ == '__main__':

    parser_initial = argparse.ArgumentParser()
    subparsers = parser_initial.add_subparsers()

    ### BIT CONVERSIONS
    parser_bit_convert = subparsers.add_parser('bit_convert', help="bit_convert help")
    parser_bit_convert.add_argument('--input', required=True, help="path to the folder with images to convert")
    parser_bit_convert.add_argument('--output', required=True, help="path to the folder with converted images")
    parser_bit_convert.add_argument('--ext', required=True, help="image_extension")
    group = parser_bit_convert.add_mutually_exclusive_group()
    group.add_argument('--simple', help="simple and goes brrr", action="store_true")
    group.add_argument('--smart', help="smart but goes slooow", action="store_true")
    parser_bit_convert.set_defaults(func=convert_bitness)

    ### DUPLICATES
    parser_duplicates = subparsers.add_parser('duplicates', help="duplicate_finder help")
    duplicate_subparsers = parser_duplicates.add_subparsers()

    parser_duplicate_folders = duplicate_subparsers.add_parser('compare_folders', help="compare_folders help")
    parser_duplicate_folders.add_argument('--original', required=True, help='path to the original folder')
    parser_duplicate_folders.add_argument('--newcome', required=True, help='path to the folder you want to join')
    parser_duplicate_folders.add_argument('--sensitivity', required=True, help='sensitivity of detection')
    parser_duplicate_folders.set_defaults(func=compare_folders)

    parser_duplicate_finder = duplicate_subparsers.add_parser('find', help="find duplicates help")
    parser_duplicate_finder.add_argument('--path', required=True, help="path to the folder with images to analyse")
    parser_duplicate_finder.add_argument('--sensitivity', required=True, help='sensitivity of detection')
    parser_duplicate_finder.set_defaults(func=find_duplicates)

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

    arguments = parser_initial.parse_args()
    # arguments.func(arguments)