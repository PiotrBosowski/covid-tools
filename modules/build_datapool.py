import os
import csv
import shutil


def build_datapool(input_path, output_path):
    """
    Checks all directories in input_path directory in search of inner
    'data' directories - these are supposed to contain label-named
    directories. Script builds merged 'datapool' directory in the
    output_path location and creates a origin.csv file that allows
    backtracking the origin of particular picture and prevents naming
    collision.
    """
    datasets = [os.path.join(input_path, directory)
                for directory in os.listdir(input_path)]
    buildable_datasets = [dataset for dataset in datasets
                          if os.path.exists(os.path.join(dataset, 'data'))]
    os.makedirs(output_path, exist_ok=False)
    with open(os.path.join(output_path, 'origins.csv'), 'x') as csv_file:
        # origin_path and new_path are relative - they relate to the
        # root folder: accordingly input_path and output_path
        csv_writer = csv.DictWriter(csv_file, ['img_name',
                                               'in_datapool_path',
                                               'in_datasource_path',
                                               'origin_datasource',
                                               'label'])
        csv_writer.writeheader()
        for dataset in buildable_datasets:
            print(os.path.basename(dataset))
            for label in os.listdir(os.path.join(dataset, 'data')):
                print('\t', label, end=' ')
                items = 0
                input_label_path = os.path.join(dataset, 'data', label)
                output_label_path = os.path.join(output_path, label)
                os.makedirs(output_label_path, exist_ok=True)
                for file in os.listdir(input_label_path):
                    input_file_path = os.path.join(input_label_path, file)
                    if not os.path.isfile(input_file_path):
                        continue
                    output_file_path = os.path.join(output_label_path, file)
                    if not os.path.exists(output_file_path):
                        shutil.copy(input_file_path, output_file_path)
                    else:
                        counter = 1
                        while True:
                            new_name = os.path.join(output_file_path,
                                                    str(counter))
                            if not os.path.exists(new_name):
                                # original data stays untouched
                                shutil.copy(input_file_path, output_file_path)
                                break
                            counter += 1
                    csv_writer.writerow({'img_name': file,
                                         'in_datapool_path':
                                        os.path.relpath(output_file_path,
                                                        output_path),
                                         'in_datasource_path':
                                        os.path.relpath(input_file_path,
                                                        input_path),
                                         'origin_datasource':
                                        os.path.basename(dataset),
                                         'label': label})
                    items += 1
                print(items)


if __name__ == '__main__':
    build_datapool('/home/peter/media/data/covid-19/cr',
                   '/home/peter/media/c/Desktop/datapool')