import os
import shutil
import random


def split(args):
    """
    Splitting into train, test, valid wrapper.
    """
    split_into_train_test_valid(args.path, args.output, int(args.train),
                                int(args.valid), int(args.test),
                                True if args.allow_imbalanced_remainings
                                else False,
                                args.labels)


def create_set(dataset_path, output_path, set_name, num_samples, labels,
               images, allow_imbalanced_remainings=False):
    if num_samples < 0 and not allow_imbalanced_remainings:
        # find lowest quantity set and take that much
        num_samples = len(images[min(images, key=lambda x: len(images[x]))])
    for label in labels:
        output_label_folder = os.path.join(output_path, set_name, label)
        os.makedirs(output_label_folder)
        samples = random.sample(images[label], num_samples)\
            if num_samples >= 0 else list(images[label])
        for sample in samples:
            shutil.copy(os.path.join(dataset_path, label, sample),
                        os.path.join(output_label_folder, sample))
            images[label].remove(sample)


def split_into_train_test_valid(dataset_path, output_path, train_size,
                                valid_size, test_size,
                                allow_imbalanced_remainings, labels):
    os.makedirs(output_path, exist_ok=False)
    sizes = {'train': train_size, 'valid': valid_size, 'test': test_size}
    negative_sizes = {k: v for (k, v) in sizes.items() if v < 0}
    positive_sizes = {k: v for (k, v) in sizes.items() if v >= 0}
    if len(negative_sizes) > 1:
        raise Exception("cannot create more than 1 dataset with 'include all "
                        "remainings images' option")
    images = {}
    for label in labels:
        label_path = os.path.join(dataset_path, label)
        images[label] = [img for img in os.listdir(label_path)]
        print(f'Found {len(images[label])} images of class: {label}')
    for (name, size) in positive_sizes.items():
        create_set(dataset_path, output_path, name, size, labels, images)
    for (name, size) in negative_sizes.items():
        create_set(dataset_path, output_path, name, size, labels, images,
                   allow_imbalanced_remainings)
