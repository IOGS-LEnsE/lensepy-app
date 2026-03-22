# -*- coding: utf-8 -*-
"""*dataset_utils.py* file.

./utils/dataset_utils.py contains tools for images processing.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
from enum import Flag, auto
import numpy as np
import scipy
import cv2

from lensepy.images.conversion import resize_image_ratio


class DataSetStateValue(Flag):
    # Flag - Analys. / Unw. / Wrap. / Crop. / Masks / Images / On
    ON = auto()
    IMAGES = auto()
    MASKS = auto()
    CROPPED = auto()
    WRAPPED = auto()
    UNWRAPPED = auto()
    ANALYZED = auto()


class DataSetState:
    def __init__(self):
        self.state = DataSetStateValue.ON

    def reset(self):
        self.state = DataSetStateValue.ON

    def check_state(self, value: DataSetStateValue):
        return bool(self.state & value)

    def toggle_state(self, value: DataSetStateValue):
        if self.state & value:
            self.state = self.state & ~value
        else:
            self.state = self.state | value

    def set_state(self, value: DataSetStateValue, state: bool = True):
        actual_state = self.check_state(value)
        if actual_state != state:
            if state:
                self.state = self.state | value
            else:
                self.state = self.state & ~value


def generate_images_grid(images: list[np.ndarray]):
    """Generate a grid with 5 images.
    The 6th image is the mean of the 4 first images.
    :param images: List of 5 images.
    """
    img_height, img_width, *channels = images[0].shape
    if channels:
        for k in range(len(images)):
            if channels[0] != 1:
                images[k] = cv2.cvtColor(images[k], cv2.COLOR_RGB2GRAY)
            else:
                images[k] = images[k].squeeze()

    separator_size = 5
    # Global size
    total_height = 2 * img_height + separator_size  # 2 rows of images
    total_width = 3 * img_width + 2 * separator_size  # 3 columns of images
    # Empty image
    result = np.ones((total_height, total_width), dtype=np.uint8) * 255
    # Add each images
    result[0:img_height, 0:img_width] = images[0]
    result[0:img_height, img_width + separator_size:2 * img_width + separator_size] = images[1]
    result[0:img_height, 2 * img_width + 2 * separator_size:] = images[2]
    result[img_height + separator_size:, 0:img_width] = images[3]
    result[img_height + separator_size:, img_width + separator_size:2 * img_width + separator_size] = images[4]
    sum_image = (images[0] + images[1] + images[2] + images[3])/4
    sum_image = sum_image.astype(np.uint8)
    result[img_height + separator_size:, 2 * img_width + 2 * separator_size:] = sum_image
    result_s = resize_image_ratio(result, img_height, img_width)
    return result_s

def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    if os.path.exists(file_path):
        data = scipy.io.loadmat(file_path)
        return data
    else:
        print('read_mat_file / No File')


def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None, masks_type: list = []):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    :param masks_type: Type of the masks to save. Default [].
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    if len(masks_type) != 0:
        data['Masks_Type'] = masks_type
    scipy.io.savemat(file_path, data)


def split_3d_array(array_3d, size: int = 5):
    # Ensure the array has the expected shape
    if array_3d.shape[2]%size != 0:
        raise ValueError(f"The loaded array does not have the expected third dimension size of {size}.")
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(array_3d.shape[2])]
    return arrays

def load_default_parameters(file_path: str) -> dict:
    """
    Load parameter from a CSV file.

    :return: Dict containing 'key_1': 'language_word_1'.

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '#', which will be ignored.

    The file should have the following format:
        # comment
        # comment
        key_1 ; language_word_1
        key_2 ; language_word_2
    """
    dictionary_loaded = {}
    if os.path.exists(file_path):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt(file_path, delimiter=';',
                             dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for key, value in data:
            dictionary_loaded[key.strip()] = value.strip()
        return dictionary_loaded
    else:
        print('File error')
        return {}