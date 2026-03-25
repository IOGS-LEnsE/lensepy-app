# -*- coding: utf-8 -*-
"""*phase.py* file.

./models/phase.py contains PhaseModel class to manage the phase from Zygo application.

Phase is demodulated by the Hariharan phase demodulation algorithm from a set of 5 images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import cv2
import numpy as np
from lensepy.images.conversion import crop_images, find_mask_limits
from models.hariharan_algorithm import *
from models.images import ImagesModel
from models.masks import MasksModel
from models.zernike_coefficients import Zernike
from utils.dataset_utils import DataSetState
from skimage.restoration import unwrap_phase
from scipy.ndimage import gaussian_filter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.dataset import DataSetModel

def process_statistics_surface(surface):
    # Process (Peak-to-Valley) and RMS
    PV = np.round(np.nanmax(surface) - np.nanmin(surface), 2)
    RMS = np.round(np.nanstd(surface), 2)
    return PV, RMS

class PhaseModel:
    """Class containing phase data and parameters.
    """
    def __init__(self, data_set: "DataSetModel"):
        """

        """
        self.data_set: "DataSetModel" = data_set
        set_size = self.data_set.images_sets.set_size
        self.cropped_images_sets = ImagesModel(set_size)
        self.cropped_masks_sets = MasksModel()
        self.cropped_data_ready = False
        self.wrapped_phase = None
        self.unwrapped_phase = None
        self.wedge_factor = 1.0
        # Zernike coefficients
        self.zernike_coeffs = Zernike(self)

    def prepare_data(self):
        """
        Crop the images.
        :return:
        """
        self.cropped_masks_sets.reset_masks()
        mask = self.data_set.get_global_mask()
        top_left, bottom_right = find_mask_limits(mask)
        height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
        pos_x, pos_y = top_left[1], top_left[0]
        mask_cropped = crop_images([mask], (height, width), (pos_x, pos_y))[0]
        self.cropped_masks_sets.add_mask(mask_cropped)

        # Process all the sets of images
        self.cropped_images_sets.reset_all_images()
        for k in range(self.data_set.images_sets.get_number_of_sets()):
            images = self.data_set.get_images_sets(k)
            # Process all images in the set
            images_c = crop_images(images, (height, width), (pos_x, pos_y))
            images_f = images_c # list(map(lambda x: gaussian_filter(x, 10), images_c))
            for im_k, image_f in enumerate(images_f):
                image_f = image_f.astype(np.float32)
                image_f[~mask_cropped] = np.nan
                images_f[im_k] = np.ma.masked_where(np.logical_not(mask_cropped), image_f)
            self.cropped_images_sets.add_set_images(images_f)
        self.cropped_data_ready = True
        self.data_set.set_cropped_state(True)

    def process_wrapped_phase(self, set_number: int=1):
        """
        Process Hariharan demodulation altorithm on data (set of 5 images).
        :param set_number: Number of the set to process.
        :return: True if Hariharan algorithm is processed.
        """
        if self.data_set.is_data_ready() and self.cropped_data_ready:
            self.cropped_phase = []
            mask,_ = self.cropped_masks_sets.get_mask(1)
            images_list = self.cropped_images_sets.get_images_set(set_number)
            self.wrapped_phase = hariharan_algorithm(images_list, mask)
            self.wrapped_phase = np.ma.masked_where(np.logical_not(mask), self.wrapped_phase)
            self.data_set.set_wrapped_state(True)
            return True
        else:
            self.wrapped_phase = None
            return False

    def get_wrapped_phase(self) -> np.ndarray:
        """
        Return the wrapped phase if calculated
        :return: Wrapped phase as an array in 2D.
        """
        return self.wrapped_phase

    def process_unwrapped_phase(self):
        """
        Process unwrapping algorithm from Skimage-restauration.
        :return: True if Hariharan algorithm is processed. None if not processed.
        """
        if self.wrapped_phase is not None:
            mask, _ = self.cropped_masks_sets.get_mask(1)
            self.unwrapped_phase = unwrap_phase(self.wrapped_phase) / (2 * np.pi)
            self.unwrapped_phase[~mask] = np.nan
            self.unwrapped_phase = np.ma.masked_where(np.logical_not(mask), self.unwrapped_phase)
            self.data_set.set_unwrapped_state()
            return True
        else:
            self.unwrapped_phase = None
            return False

    def get_unwrapped_phase(self) -> np.ndarray:
        """
        Return the unwrapped phase if calculated
        :return: Unwrapped phase as an array in 2D. None if not processed.
        """
        if self.unwrapped_phase is not None:
            return -self.unwrapped_phase * self.wedge_factor
        else:
            return None

    def is_analysis_ready(self):
        """
        Check if wrapped and unwrapped phase are processed from images.
        :return: True if wrapped and unwrapped phase are processed.
        """
        if self.wrapped_phase is None or self.unwrapped_phase is None:
            return False
        else:
            return True

    def reset_phase(self):
        """Reset all the data of the phase object (wrapped and unwrapped)."""
        self.wrapped_phase = None
        self.unwrapped_phase = None
        self.zernike_coeffs.reset_coeffs()
        self.data_set.set_cropped_state()

    def set_wedge_factor(self, value: float):
        """
        Set the wedge factor, for displaying.
        :param value: Wedge factor value.
        """
        self.wedge_factor = value

    def get_wedge_factor(self) -> float:
        """
        Get the wedge factor.
        """
        return self.wedge_factor


if __name__ == '__main__':
    import sys, os
    from matplotlib import pyplot as plt
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models.dataset import DataSetModel

    nb_of_images_per_set = 5
    file_path = '../_data/test3.mat'
    data_set = DataSetModel()
    data_set.load_images_set_from_file(file_path)
    data_set.load_mask_from_file(file_path)

    phase_test = PhaseModel(data_set)

    ## Test class
    phase_test.prepare_data()
    print(f'Number of sets = {phase_test.cropped_images_sets.get_number_of_sets()}')

    if phase_test.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = phase_test.get_wrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(wrapped.T, cmap='gray')

    if phase_test.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = phase_test.get_unwrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(unwrapped, cmap='gray')

    plt.show()

    print(f'PV / RMS - Unwrapped = {process_statistics_surface(unwrapped)}')

