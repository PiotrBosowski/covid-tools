import os
import numpy as np
from PIL import Image


def bitness(args):
    convert_all(args.input, args.output, args.ext,
                convert_image_simple if args.simple else convert_image_smart)


def color_flip(args):
    convert_all(args.path, args.output, args.ext, flip_colors)


def extension(args):
    extension_impl(args.path, args.output, args.ext_in, args.ext_out)


def extension_impl(input_dir, output_dir, extension_in, extension_out):
    if 'dcm' in extension_in and 'png' in extension_out:
        images = [os.path.join(input_dir, image) for image in
                  os.listdir(input_dir) if image.endswith(extension_in)
                  and os.path.isfile(os.path.join(input_dir, image))]
        if images:
            print(
                f'med2image -i {images[-1]} -d {output_dir} '
                f'--outputFileType {extension_out}')
            os.system(
                f'med2image -i {images[-1]} -d {output_dir} '
                f'--outputFileType {extension_out}')
        else:
            print("no images to convert")


def get_island_boundaries(pixels, bin_min, bin_max):
    """
    Calculates real min- and max-pixel-values within one island that
    spans from bin_min to bin_max. Basing just on bins' applying window
    of just bin_max and bin_min may cause image flattening, because real
    max- and min-pixel-values are usually slightly different from
    highest bin's upper bound and lowest bin's lower bound (especially
    with low number of bins).
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
    Applies linear transformation to the image, forcing all pixels to
    spread across whole pixelspace (0-255 for 8-bit picture). Everything
    outside the window (i.e. outliers) is replaced with the mean;
    if window_bot == lowest pixel value and window_top == highest pixel
    value, then no replacements take place.
    :param pixels: input image as numpy array
    :param window_bot: lower bound of the window
    :param window_top: upper bound of the window
    :param mean: mean of the window
    :return: Image, in which pixels that fitted [window-bot, window-top]
    span across whole pixelspace (0-255 for 8-bits)
    """
    pixels = pixels.astype(np.float64)
    # clipping the image would be OK as well
    pixels[(pixels > window_top) | (pixels < window_bot)] = mean
    pixels -= window_bot
    window_top -= window_bot
    # DANGER: performing this step makes image human-readable, but it
    # also introduces some irregularities in the image histogram (trying
    # to extend (0, n) range to cover whole (0, 255) will result in
    # histogram-holes if n < 255).
    # TODO: think about giving up on it -> float processing framework
    try:
        # casting to regular float to prevent numpy from performing this
        # division and let python handle zero-division error
        pixels *= (255.0 / float(window_top))
    except ZeroDivisionError:
        pixels = np.zeros_like(pixels)
    return np.around(pixels)


def flip_colors(image):
    """
    Inverts image colors.
    :param image: PIL image to be converted
    :return: numpy array
    """
    image_arr = np.asarray(image)
    img_min, img_max = np.min(image_arr), np.max(image_arr)
    output_arr = apply_window(image_arr, img_min, img_max,
                              (float(img_max) + float(img_min)) / 2)
    img_max = np.max(output_arr)
    output_arr *= -1
    output_arr += img_max
    return output_arr


def convert_image_simple(image):
    """
    Applies window to the image, priorly calculating image min- and
    max-pixel-values. It's sometimes called 'clipping' the image.
    :param image: input image as PIL.Image
    :return: PIL.Image with pixels spreading across whole pixelspace
    (0-255 for 8-bit pictures)
    """
    pixels = np.asarray(image)
    img_min, img_max = np.min(pixels), np.max(pixels)
    return apply_window(pixels, img_min, img_max, (img_max + img_min) / 2)


def find_islands(image_arr, max_gap_percent):
    """
    Finds histogram islands, which in many applications are a sign of
    an image being corrupted with some human-made marks, signs, etc.
    Sorts the islands according to their size, hoping for that the
    biggest island will be the actual content (which most usually is
    the case). Ideas: Introduce checking the islands by calculating
    their variances - low variance == bad.
    :param image_arr: image to be processed
    :param max_gap_percent: maximum distance between islands expressed
    in % of image span (span = max - min pixel values).
    :return: list of image's islands; original image stays unmodified
    """
    window_width = int((np.max(image_arr) - np.min(image_arr)))
    # max acceptable distance between two islands
    max_gap = int(window_width * max_gap_percent)
    if window_width == 0:
        # if image is flat, return island with dummy area
        return [{'begin': np.min(image_arr),
                 'end': np.min(image_arr), 'area': 100}]
    image_hist = np.histogram(image_arr, bins=window_width)
    islands = []  # find islands in picture's histogram
    gap_counter = 0
    last_pixel = -1
    is_island = False
    for index, pixel_count in enumerate(image_hist[0]):
        if pixel_count != 0 and not is_island:
            is_island = True
            islands.append(
                {'begin': image_hist[1][index], 'end': image_hist[1][-1],
                 'area': pixel_count})
        elif pixel_count != 0 and is_island:
            gap_counter = 0
            islands[-1]['area'] += pixel_count
        elif pixel_count == 0 and is_island:
            if gap_counter == 0:
                # if just got out of island, remember the position
                last_pixel = index - 1
            gap_counter += 1
            if gap_counter > max_gap:
                gap_counter = 0
                is_island = False
                islands[-1]['end'] = image_hist[1][last_pixel]
        elif pixel_count == 0 and not is_island:
            continue
    if not islands:
        raise Exception("empty image")
    islands.sort(key=lambda isl: isl['area'], reverse=False)
    return islands


def convert_image_smart(image, max_gap_percent=0.05, max_iterations=3):
    """
    Checks image histogram in search of outlaying pixel-values, that
    almost certainly represent human-made marks,vhighlights, captions.
    These artificially introduced pixels can harm regular window
    applying, because they may significantly widen color deptch, forcing
    the data itself to occupy only few percents of all pixelspace.
    Ideas: Instead of replacing pixels with mean value, replace them
    with uniformly distributed noise to prevent spikes in histogram.
    :param image: input PIL.Image
    :param max_gap_percent: maximum distance between histogram islands
    expressed in % of the pixelspace (color depth)
    :param max_iterations: maximum number of repeats of the algorithm
    the need of repeating comes from the fact, that a gap can be smaller
    than max_gap_percent when the image is badly spanned and will be
    detected only after initial window-applying
    :return: numpy array with man-made marks replaced with the mean of
    the rest of the picture and applied window
    """
    image_arr = np.asarray(image)
    eps = 0.0001
    for index in range(max_iterations):
        islands = find_islands(image_arr, max_gap_percent)
        max_pix = islands[-1]['end']
        min_pix = islands[-1]['begin']
        real_min, real_max = get_island_boundaries(image_arr, min_pix, max_pix)
        if (abs(real_min - np.min(image_arr)) < eps)\
                and (abs(real_max - np.max(image_arr)) < eps):
            dominant_mean = (float(real_min) + float(real_max)) / 2
            image_arr = apply_window(image_arr, real_min, real_max,
                                     dominant_mean)
        else:
            break
    return image_arr


def convert_all(images_folder, output_folder, image_extension, function,
                verbose=False):
    """
    Applies function to all images with extension image_extension from
    images_folder and saves them in output_folder. Original pictures
    remain unchanged.
    :param images_folder: input folder
    :param output_folder: output folder
    :param image_extension: extension of the images to transform
    :param function: transformation function
    :param verbose: should elaborates be displayed
    """
    output_ext = '.png'
    error_counter = 0
    os.makedirs(output_folder, exist_ok=True)
    images = [img for img in os.listdir(images_folder)
              if os.path.isfile(os.path.join(images_folder, img))
              and image_extension == 'all' or img.endswith(image_extension)]
    for image_name in images:
        try:
            input_path = os.path.join(images_folder, image_name)
            image_name, _ = os.path.splitext(image_name)
            output_path = os.path.join(output_folder, image_name + output_ext)
            if verbose:
                print(f'Converting {input_path} -> {output_path}')
            if not os.path.exists(
                    output_path) or input_path == output_path:
                # .convert('RGB') drops unused alpha (opacity) channel
                with Image.open(input_path).convert('RGB') as image:
                    converted_img = function(image)
                    converted_img = Image.fromarray(np.uint8(converted_img))
                    converted_img.save(output_path)
        except Exception as ex:
            error_counter += 1
            print(f'[{error_counter}] Error converting an image: {image_name}',
                  ex)


if __name__ == "__main__":
    convert_all('/home/peter/covid/playground/plgnd',
                '/home/peter/covid/playground/plgnd2', ".png",
                convert_image_smart, verbose=True)
