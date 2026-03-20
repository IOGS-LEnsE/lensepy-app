# -*- coding: utf-8 -*-
"""*masks.py* file.

./models/masks.py contains Masks_Model class to manage sets of masks to apply on images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
from typing import Tuple
from lensepy.images.conversion import find_mask_limits, crop_images
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lensepy_app.modules.optics.zygo.utils import read_mat_file, split_3d_array
import numpy as np

class MasksModel:
    """Class containing masks data and parameters.
    """
    def __init__(self):
        """Default constructor.
        """
        self.masks_list = []
        self.masks_number = 0
        self.mask_type = []
        self.mask_selected = []
        self.mask_inverted = []
        self.global_inverted = False

    def __str__(self):
        """Print function."""
        out_str = 'Masks List\n'
        for i in range(self.masks_number):
            out_str += f'\tMask {i+1} : {self.mask_type[i]}\n'
        return out_str

    def get_mask(self, index: int) -> np.ndarray:
        """Return the selected mask.
        :param index: Index of the mask to return.
        """
        if index <= self.masks_number:
            if self.mask_inverted[index-1] is True:
                mask = np.logical_not(self.masks_list[index-1])
            else:
                mask = self.masks_list[index-1]
            return mask, self.mask_type[index-1]
        return None

    def get_type(self, index: int) -> str:
        """Return the type of the selected mask.
        :param index: Index of the mask to get the type.
        :return: Type of the mask.
        """
        if index <= self.masks_number:
            return self.mask_type[index-1]
        return None

    def get_mask_list(self) -> list[np.ndarray]:
        """Return all the masks in a list."""
        return self.masks_list

    def get_number(self):
        """Return the number of masks."""
        return self.masks_number

    def add_mask(self, mask: np.ndarray, type_m: str = ''):
        """Add a new mask to the list.
        :param mask: Mask to add to the list.
        :param type_m: Type of mask (Circular, Rectangular, Polygon).
        """
        self.masks_list.append(mask)
        self.mask_type.append(type_m)
        self.mask_selected.append(True)
        self.mask_inverted.append(False)
        self.masks_number += 1

    def reset_masks(self):
        """Reset all the masks."""
        self.masks_list.clear()
        self.mask_type.clear()
        self.mask_selected.clear()
        self.mask_inverted.clear()
        self.masks_number = 0

    def del_mask(self, index: int):
        """Remove the specified mask.
        :param index: Index of the mask to remove.
        """
        self.masks_list.pop(index-1)
        self.mask_type.pop(index-1)
        self.mask_selected.pop(index-1)
        self.mask_inverted.pop(index-1)
        self.masks_number -= 1

    def select_mask(self, index: int, value: bool = True):
        """Select or unselect a mask.
        :param index: Index of the mask to select.
        :param value: False to unselect. Default True to select.
        """
        self.mask_selected[index-1] = value

    def invert_mask(self, index: int, value: bool = True):
        """Invert or not a mask.
        :param index: Index of the mask to invert.
        :param value: False to uninvert. Default True to invert.
        """
        self.mask_inverted[index-1] = value

    def invert_global_mask(self, value: bool = True):
        """Invert the global mask.
        :param value: False to uninvert. Default True to invert.
        """
        self.global_inverted = value

    def get_global_mask(self):
        """Return the resulting mask."""
        if self.masks_number > 0:
            global_mask = np.zeros_like(self.masks_list[0]).astype(bool)
            for i, simple_mask in enumerate(self.masks_list):
                if self.mask_selected[i]:
                    simple_mask = simple_mask > 0.5
                    if self.mask_inverted[i]:
                        simple_mask = np.logical_not(simple_mask)
                    global_mask = np.logical_or(global_mask, simple_mask)
            if self.global_inverted:
                return np.logical_not(global_mask)
            else:
                return global_mask
        else:
            return None

    def get_global_cropped_mask(self) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
        """
        Return the cropped mask around the limits.
        :return:
        """
        global_mask = self.get_global_mask()
        top_left, bottom_right = find_mask_limits(global_mask)
        height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
        pos_x, pos_y = top_left[1], top_left[0]
        global_crop = crop_images([global_mask], (height, width), (pos_x, pos_y))[0]
        return global_crop, (height, width), (pos_x, pos_y)

    def get_masks_number(self):
        """Return the number of stored masks."""
        return self.masks_number

    def is_mask_selected(self, index: int):
        """Return the status of the selection of a mask.
         :param index: Index of the mask.
         :return: True if the mask is selected.
         """
        return self.mask_selected[index-1]

    def is_mask_inverted(self, index: int):
        """Return the status of the inversion of a mask.
         :param index: Index of the mask.
         :return: True if the mask is inverted.
         """
        return self.mask_inverted[index-1]

    def load_mask_from_file(self, filename: str = '') -> bool:
        """
        Load a set of mask from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        if filename != '':
            data_from_mat = read_mat_file(filename)
            # Process masks from MAT file
            if 'Masks' in data_from_mat:
                mask_mat = data_from_mat['Masks']
                mask_d = split_3d_array(mask_mat, size=1)
                if 'Masks_type' in data_from_mat:
                    print(f'Masks Type = {data_from_mat["Masks_type"]}')
                if isinstance(mask_d, list):
                    self.reset_masks()
                    for i, maskk in enumerate(mask_d):
                        self.add_mask(maskk.squeeze())
                return True
            else:
                return False
        return False


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    masks_set = MasksModel()

    ## Open MAT file - including 'Images' and 'Masks'
    if masks_set.load_mask_from_file('../_data/test3.mat'):
        print('Masks OK')

    ## Test class
    print(f'Number of masks = {masks_set.get_masks_number()}')
    if masks_set.get_masks_number() >= 1:
        mask_1, _ = masks_set.get_mask(1)
        plt.figure()
        plt.imshow(mask_1, cmap='gray')
        plt.show()