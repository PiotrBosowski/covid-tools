import os
import shutil
import numpy as np
from PIL import Image, UnidentifiedImageError


def convert_images_np(image_path):
    img = Image.open(image_path)
    pixels = np.asarray(img)
    pixels = pixels.astype('float32')
    pixels = pixels * (255.0 / np.max(pixels))
    converted_img = Image.fromarray(np.uint8(pixels))
    return converted_img
   

def convert_all(images_folder, output_folder, image_extension):
    error_counter = 0
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    for image in os.listdir(images_folder):
        if image.endswith(image_extension):
            try:
                output_path = os.path.join(output_folder, image)
                if not os.path.exists(output_path):
                    converted_img = convert_images_np(os.path.join(images_folder, image))
                    converted_img.save(output_path)
            except UnidentifiedImageError:
                error_counter += 1
                print(f'[{error_counter}] Error converting an image: {image}')
                shutil.move(os.path.join('cr', image), os.path.join('errors', image))
