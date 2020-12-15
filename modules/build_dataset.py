import os
import shutil
import random
import csv


def build(args):
    """
    Splitting into train, test, valid wrapper.
    """
    build_dataset(args.path, args.output, int(args.train),
                  int(args.valid), int(args.test),
                  True if args.allow_imbalanced_remainings else False,
                  args.labels)


def curr_num_samples(images, label, num_samples, allow_imbalanced_remainings, remainings_cap):
    if num_samples > 0:
        return num_samples
    elif allow_imbalanced_remainings:  # num_samples < 0 => remainings
        return min(len(images[label]), remainings_cap)
    else:  # not allow imbalanced remainings
        # find lowest quantity set and take that much
        smallest_label = len(images[min(images, key=lambda x: len(images[x]))])
        return min(remainings_cap, smallest_label)


def create_set(datapool_path, dataset_path, subset_name, num_samples, labels,
               images, allow_imbalanced_remainings, remainings_cap):
    subset_path = os.path.join(dataset_path, subset_name)
    os.makedirs(subset_path)
    with open(os.path.join(subset_path, 'origins.csv'), 'x') as csv_file:
        keys = ['img_name', "in_dataset_path", 'in_datapool_path', 'in_datasource_path', 'origin_datasource', 'label']
        csv_writer = csv.DictWriter(csv_file, keys)
        csv_writer.writeheader()
        for label in labels:
            output_label_folder = os.path.join(subset_path, label)
            os.makedirs(output_label_folder)
            current_num = curr_num_samples(images, label, num_samples, allow_imbalanced_remainings, remainings_cap)
            samples = random.sample(images[label], current_num)
            for sample in samples:
                in_dataset_path = os.path.join(output_label_folder, sample['img_name'])
                shutil.copy(os.path.join(datapool_path, sample['in_datapool_path']),
                            in_dataset_path)
                images[label].remove(sample)
                sample['in_dataset_path'] = os.path.relpath(in_dataset_path,
                                                            subset_path)
                csv_writer.writerow(sample)


def build_dataset(datapool_path, output_path, train_size, valid_size,
                  test_size, allow_imbalanced_remainings, remainings_cap,
                  labels):
    os.makedirs(output_path, exist_ok=False)
    sizes = {'train': train_size, 'valid': valid_size, 'test': test_size}
    negative_sizes = {k: v for (k, v) in sizes.items() if v < 0}
    positive_sizes = {k: v for (k, v) in sizes.items() if v >= 0}
    if len(negative_sizes) > 1:
        raise Exception("cannot create more than 1 dataset with 'include all "
                        "remainings images' option")
    with open(os.path.join(datapool_path, 'origins.csv'), 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        images = [row for row in csv_reader]
    labelled_images = {}
    for label in labels:
        labelled_images[label] = [image for image in images
                                  if image['label'] == label]
        print(f'Found {len(labelled_images[label])} images of class: {label}')
    for (name, size) in positive_sizes.items():
        create_set(datapool_path, output_path, name, size, labels, labelled_images,
                   allow_imbalanced_remainings, remainings_cap)
    for (name, size) in negative_sizes.items():
        create_set(datapool_path, output_path, name, size, labels, labelled_images,
                   allow_imbalanced_remainings, remainings_cap)


if __name__ == '__main__':
    build_dataset('/home/peter/media/c/Desktop/datapool',
                  '/home/peter/covid/datasets/1k-1k-8k-reforged',
                  1000, 1000, -1,
                  allow_imbalanced_remainings=False,
                  remainings_cap=8000,
                  labels=['covid', 'other', 'healthy'])
