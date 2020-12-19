import json
import os
import shutil
import random
import csv


def build(args):
    """
    Splitting into train, test, valid wrapper.
    """
    print(args)
    pass


def structurize_images(images, label_map):
    return {output_label:
            {source: [image for image in images
                      if image['origin_datasource'] == source
                      and image['label'] in input_labels]
             for source in {image['origin_datasource'] for image in images
                            if image['label'] in input_labels}}
            for output_label, input_labels in label_map.items()}


def evaluate_remainings(images, subset_sizes, remainings_balanced=True,
                        remainings_cap=20000):
    negative_sizes = [name for name, size in subset_sizes.items() if size < 0]
    positive_sizes = [size for size in subset_sizes.values() if size >= 0]
    if not negative_sizes:
        return subset_sizes
    if len(negative_sizes) > 1:
        raise Exception(
            "cannot create more than 1 dataset with 'include all "
            "remainings images' option")
    label_sizes = {label: sum([len(images) for source, images in sources.items()])
                   for (label, sources) in images.items()}
    label_remainings = {label: count - sum(positive_sizes)
                        for label, count in label_sizes.items()}
    if remainings_balanced:
        remainings = min(label_remainings.values())
        if remainings_cap:
            remainings = min(remainings_cap, remainings)
    else:  # remainings imbalanced
        remainings = {label: count
                      for label, count in label_remainings.items()}
        if remainings_cap:
            remainings = {label: min(count, remainings_cap)
                          for label, count in remainings.items()}
    # negative_sizes should be exactly of length 1
    subset_sizes[negative_sizes.pop()] = remainings
    return subset_sizes


def current_subset_sizes(subset_sizes, label):
    return {subset_name: size[label] if type(size) == dict else size
            for subset_name, size in subset_sizes.items()}


def calculate_sources_contribution(abundance, label, sources_img_count, label_subset_sizes):
    # sort ascending by number of images of this label in source
    sources_ascend = dict(sorted(sources_img_count.items(),
                                 key=lambda item: item[1]))
    for index, (src, imgs) in enumerate(sources_ascend.items()):
        # subsets_ratios holds ratios in which images of
        # current label will be split into subsets
        subsets_ratios = {label: size / sum(label_subset_sizes.values()) for
                          label, size in label_subset_sizes.items()}
        # calculate desired number of images of current source
        desired_num = round(sum(label_subset_sizes.values())
                            / (len(sources_ascend) - index))
        # consider posibility of current source being smaller than desired
        actual_num = min(desired_num, imgs)
        # split current number of images into subsets respecting subsets_ratios
        src_split = split_src(actual_num, subsets_ratios)
        # update abundance, saving results for all subsets (label, src fixed)
        for subset, size in src_split.items():
            abundance[subset][label][src] = size
            label_subset_sizes[subset] -= src_split[subset]


def structurize_abundance(subset_sizes, images):
    img_count = {label: {source: len(images[label][source]) for source in sources}
                 for label, sources in images.items()}
    abundance = {subset: {label: {source: 0 for source in sources}
                 for label, sources in images.items()}
                 for subset in subset_sizes}
    for label, sources in img_count.items():
        # evaluate subset sizes for this label
        label_subset_sizes = current_subset_sizes(subset_sizes, label)
        calculate_sources_contribution(abundance, label, sources, label_subset_sizes)
    return abundance


def split_src(imgs_per_src, subset_ratios):
    # transform to cumulative
    initial = 0
    for key in subset_ratios:
        subset_ratios[key] += initial
        initial = subset_ratios[key]
    src_split = {subset: round(imgs_per_src * ratio) for subset, ratio in
                 subset_ratios.items()}
    # transform back from cumulative
    initial = 0
    for key in src_split:
        src_split[key] -= initial
        initial += src_split[key]
    return src_split


def copy_namecheck(datapool_path, subset_path, label, sample):
    filename = sample['img_name']
    in_dataset_path = os.path.join(subset_path, label, filename)
    while os.path.exists(in_dataset_path):
        name, ext = os.path.splitext(sample['img_name'])
        filename = name + '_1' + ext
        in_dataset_path = os.path.join(subset_path, label, filename)
    sample['merging_name'] = filename
    sample['in_dataset_path'] = os.path.relpath(in_dataset_path, subset_path)
    shutil.copy(os.path.join(datapool_path, sample['in_datapool_path']),
                in_dataset_path)
    sample['premerging_label'] = sample['label']
    sample['label'] = label


def populate_sets(datapool_path, output_path, images_struct, abundance_struct):
    for subset, labels in abundance_struct.items():
        # subset_label_counter = {subset: {label: round(sum(sources.values()))
        #                                  for label, sources in labels.items()}
        #                         for subset, labels in abundance_struct.items()}
        subset_path = os.path.join(output_path, subset)
        os.makedirs(subset_path, exist_ok=True)
        with open(os.path.join(subset_path, 'origins.csv'), 'x') as csv_file:
            keys = ['img_name', 'merging_name', "in_dataset_path",
                    'in_datapool_path', 'in_datasource_path',
                    'origin_datasource', 'premerging_label', 'label']
            csv_writer = csv.DictWriter(csv_file, keys)
            csv_writer.writeheader()
            for label, sources in labels.items():
                for source, num_imgs in sources.items():
                    os.makedirs(os.path.join(subset_path, label), exist_ok=True)
                    samples = random.sample(images_struct[label][source], num_imgs)
                    for sample in samples:
                        copy_namecheck(datapool_path, subset_path, label, sample)
                        csv_writer.writerow(sample)
                        images_struct[label][source].remove(sample)


def build_dataset(datapool_path, dataset_path, subset_sizes,
                  remainings_balanced, remainings_cap,
                  label_map):
    """
    :param subset_sizes:
    :param datapool_path:
    :param dataset_path:
    :param remainings_balanced:
    :param remainings_cap:
    :param label_map: maps input labels to output labels, enabling
    combining few labels into one in resulting dataset
    :return:
    """
    os.makedirs(dataset_path, exist_ok=False)
    # todo: no csv mode
    with open(os.path.join(datapool_path, 'origins.csv'), 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        images = [row for row in csv_reader]
    images_struct = structurize_images(images, label_map)
    subset_sizes = evaluate_remainings(images_struct, subset_sizes,
                                       remainings_balanced, remainings_cap)
    # for (name, size) in positive_sizes.items():
    abundance_struct = structurize_abundance(subset_sizes, images_struct)
    populate_sets(datapool_path, dataset_path, images_struct, abundance_struct)
    with open(os.path.join(dataset_path, 'dataset_struct.txt'), 'x') as file:
        json.dump(abundance_struct, file, indent=4)


if __name__ == '__main__':
    build_dataset('/home/peter/media/data/covid-19/datapool',
                  '/home/peter/covid/datasets/balanced-binary-1.2k-1.2k-11.2k',
                  subset_sizes={
                      'train': 1200,
                      'valid': 1200,
                      'test': -1
                  },
                  remainings_balanced=True,
                  remainings_cap=11264,
                  label_map={'covid': ['covid'],
                             'non_covid': ['healthy', 'other',
                                           'other-or-healthy']},
                  )
    # source_balanced=True)
    # todo: add balancing combined labels
    # todo: add generate_remainings_separately so the test and split are balanced