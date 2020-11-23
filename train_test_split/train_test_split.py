# split into train, test, valid
import os
import shutil
import random


def create_set(dataset_path, set_name, num_samples, labels, images):
  for label in labels:
    folder_path = os.path.join(dataset_path, set_name, label)
    os.makedirs(folder_path)#, exist_ok=True)
    samples = random.sample(images[label], num_samples) if num_samples > 0 else list(images[label])
    for sample in samples:
      shutil.copy(os.path.join(dataset_path, label, sample), os.path.join(folder_path, sample))
      images[label].remove(sample)


def split_into_train_test_valid(dataset_path, test_size, valid_size, labels):
  images = {}
  for label in labels:
    label_path = os.path.join(dataset_path, label)
    images[label] = [img for img in os.listdir(label_path)]
    print(f'Found {len(images[label])} images of class: {label}')
  create_set(dataset_path, 'test', test_size, labels, images)
  create_set(dataset_path, 'valid', valid_size, labels, images)
  create_set(dataset_path, 'train', -1, labels, images) # -1 returns all image that are left
