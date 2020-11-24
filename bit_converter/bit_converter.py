import os
import shutil
import numpy as np
from PIL import Image, UnidentifiedImageError


def get_island_boundaries(pixels, bin_min, bin_max):
    """
    Calculates real min- and max-pixel-values within one island that spans from bin_min to bin_max. Basing just on bins'
    applying window of just bin_max and bin_min may cause image flattening, because real max- and min-pixel-values
    are usually slightly different from highest bin's upper bound and lowest bin's lower bound (especially when low
    number of bins).
    :param pixels: input image as numpy array
    :param bin_min: lower bound of lowest bin
    :param bin_max: upper bound value of highest bin
    :return: tuple of lowest and highest pixel-values within the island
    """
    pixels_cpy = np.copy(pixels)
    mean = (bin_max + bin_min) / 2
    pixels_cpy[pixels_cpy > bin_max] = mean
    pixels_cpy[pixels_cpy < bin_min] = mean
    return np.min(pixels_cpy), np.max(pixels_cpy)


def apply_window(pixels, window_bot, window_top, mean):
    """
    Applies linear transformation to the image, forcing all pixels to spread across whole pixelspace (0-255 for 8-bit
    picture). Everything outside the window (i.e. outliers) is replaced with the mean; if window_bot == lowest pixel
    value and window_top == highest pixel value, then no replacements take place.
    :param pixels: input image as numpy array
    :param window_bot: lower bound of the window
    :param window_top: upper bound of the window
    :param mean: mean of the window
    :return: Image, in which pixels that fitted [window-bot, window-top] span across whole pixelspace (0-255 for 8-bits)
    """
    pixels = pixels.astype('float32')
    pixels[(pixels > window_top) | (pixels < window_bot)] = mean
    pixels -= window_bot
    pixels *= (255.0 / window_top)
    return Image.fromarray(np.uint8(pixels))


def convert_image_simple(image):
    """
    Applies window to the image, priorly calculating image min- and max-pixel-values. No replacements take place.
    :param image: input image as PIL.Image
    :return: PIL.Image with pixels spreading across whole pixelspace (0-255 for 8-bit pictures)
    """
    pixels = np.asarray(image)
    img_min, img_max = np.min(pixels), np.max(pixels)
    return apply_window(pixels, img_min, img_max, (img_max + img_min) / 2)


def convert_image_smart(image):
    """
    Check image's histogram in search of outlaying pixel-values, that almost certainly represent human-made marks,
    highlights, captions. These artificially introduced pixels can harm regular window applying, because they may
    significantly widen pixelspace, forcing the data itself to occupy only few percents of pixelspace.
    TODO: Introduce checking the islands by calculating their variances - low variance == bad.
    :param image: input PIL.Image
    :return: PIL.Image with man-made marks replaced with the mean of the rest of the picture, window applied
    """
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
    real_min, real_max = get_island_boundaries(image_arr, min_pix, max_pix)
    dominant_mean = (max_pix + min_pix) / 2
    return apply_window(image_arr, real_min, real_max, dominant_mean)


def convert_all(images_folder, output_folder, image_extension, function):
    """
    Applies function to all images with extension image_extension from images_folder and saves them in output_folder.
    Original pictures remain unchanged.
    :param images_folder: input folder
    :param output_folder: output folder
    :param image_extension: extension of the images to transform
    :param function: transformation function
    """
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

# convert_all('D:\covid-19\playground', 'D:\covid-19\playground\output', '.png', convert_image_smart)