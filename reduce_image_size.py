import os
import shutil
import concurrent.futures
from PIL import Image


def reduce_image_size(file_path, max_size):
    """
    Reduce the size of an image file while preserving its aspect ratio.
    The file format is changed to JPEG if it is currently in PNG format.

    Args:
        file_path (str): The path to the image file to be reduced.
        max_size (int): The maximum size in bytes that the image should be reduced to.

    Returns:
        None
    """
    with Image.open(file_path) as img:
        if img.format == 'PNG':
            new_file_path = os.path.splitext(file_path)[0] + '.jpg'
            img = img.convert('RGB')
        else:
            new_file_path = file_path

        original_size = os.path.getsize(new_file_path)
        quality = 80

        while original_size > max_size and quality > 0:
            quality -= 5
            img.save(new_file_path, optimize=True, quality=quality)
            original_size = os.path.getsize(new_file_path)

    if os.path.getsize(new_file_path) > max_size:
        os.remove(new_file_path)
    else:
        os.remove(file_path)
        os.rename(new_file_path, file_path)


def process_images(root_folder, excluded_folders=[], max_size=2000000):
    """
    Traverse all subfolders of a given folder and apply reduce_image_size() function to all images found.
    Creates a .processed file in each processed folder to mark it as processed.
    Stores the list of processed folders in a separate file to avoid processing the same folder twice.

    Args:
        root_folder (str): The root folder to start traversing from.
        excluded_folders (list): A list of folder names to exclude from processing.
        max_size (int): The maximum size in bytes that an image should be reduced to.

    Returns:
        None
    """
    processed_file = os.path.join(root_folder, ".processed_folders.txt")
    if os.path.isfile(processed_file):
        with open(processed_file, "r") as f:
            processed_folders = f.read().splitlines()
    else:
        processed_folders = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for foldername, subfolders, filenames in os.walk(root_folder):
            if any(foldername.endswith(folder) for folder in excluded_folders):
                subfolders[:] = []
                continue

            if foldername not in processed_folders:
                futures = []
                for filename in filenames:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(foldername, filename)
                        if os.path.getsize(file_path) > max_size:
                            futures.append(executor.submit(reduce_image_size, file_path, max_size))

                for future in concurrent.futures.as_completed(futures):
                    future.result()

                with open(processed_file, "a") as f:
                    f.write(foldername + "\n")


if __name__ == '__main__':
    process_images('path/to/root/folder', excluded_folders=['excluded_folder_1', 'excluded_folder_2'], max_size=2000000)
