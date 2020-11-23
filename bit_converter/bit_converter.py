import os
import shutil
import numpy as np
import math
from multiprocessing import Pool
from joblib import delayed, Parallel
from PIL import Image, UnidentifiedImageError


def update_island_pixel(pixel, min_val, max_val, mean):
    return mean if pixel > max_val or pixel < min_val else pixel


def convert_image_simple(image):
    pixels = np.asarray(image)
    pixels = pixels.astype('float32')
    pixels = pixels * (255.0 / np.max(pixels))
    converted_img = Image.fromarray(np.uint8(pixels))
    return converted_img


def island_boundaries(image_arr, bin_min, bin_max):
    temp_arr = np.copy(image_arr)
    mean = (bin_max + bin_min) / 2
    temp_arr[temp_arr > bin_max] = mean
    temp_arr[temp_arr < bin_min] = mean
    return np.min(temp_arr), np.max(temp_arr)


def apply_window(pixels, real_min, real_max, dominant_mean):
    pixels = pixels.astype('float32')
    pixels[(pixels > real_max) | (pixels < real_min)] = dominant_mean
    pixels -= real_min
    pixels *= (255.0 / real_max)
    return Image.fromarray(np.uint8(pixels))


def convert_image_smart(image):
    image_arr = np.asarray(image)
    window_width = int((np.max(image_arr) - np.min(image_arr))/10)
    image_hist = np.histogram(image_arr, bins=window_width)
    islands = []  # find islands in picture's histogram
    is_island = False
    for index, pixel_count in enumerate(image_hist[0]):
        if pixel_count != 0 and not is_island:
            is_island = True
            islands.append({'begin': image_hist[1][index], 'end': image_hist[1][-1], 'area': pixel_count})
        elif pixel_count != 0 and is_island:
            islands[-1]['area'] += pixel_count
        elif pixel_count == 0 and is_island:
            is_island = False
            islands[-1]['end'] = image_hist[1][index]
        elif pixel_count == 0 and not is_island:
            continue
    if not islands:
        raise Exception("empty image")
    islands.sort(key=lambda isl: isl['area'], reverse=False)
    max_pix = islands[-1]['end']
    min_pix = islands[-1]['begin']
    real_min, real_max = island_boundaries(image_arr, min_pix, max_pix)
    dominant_mean = (max_pix + min_pix) / 2
    return apply_window(image_arr, real_min, real_max, dominant_mean)


def convert_all(images_folder, output_folder, image_extension, function):
    error_counter = 0
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    for image in os.listdir(images_folder):
        if image.endswith(image_extension):
            try:
                output_path = os.path.join(output_folder, image)
                if not os.path.exists(output_path):
                    with Image.open(os.path.join(images_folder, image)) as image:
                        converted_img = function(image)
                        converted_img.save(output_path)
            except UnidentifiedImageError:
                error_counter += 1
                print(f'[{error_counter}] Error converting an image: {image}')
                shutil.move(os.path.join('cr', image), os.path.join('errors', image))

convert_all('D:\covid-19\playground', 'D:\covid-19\playground\output', '.png', convert_image_smart)