
from enum import Flag, auto

import numpy as np

from lensepy_app.modules.optics.zygo.images.images_model import ImagesSet
from lensepy_app.modules.optics.zygo.masks.masks_model import MasksSet

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



class DataSet:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_sets = ImagesSet(set_size)
        self.masks_sets = MasksSet()
        '''
        self.acquisition_mode = AcquisitionModel(set_size)
        '''
        self.data_set_state = DataSetState()


    def add_set_images(self, images: list) -> bool:
        """
        Add a new set of images.
        :param images: List of images to add.
        :return: True if the set of images is added.
        """
        state = self.images_sets.add_set_images(images)
        if state:
            self.data_set_state.set_state(DataSetStateValue.IMAGES, True)
        return state

    def get_images_sets(self, index: int=1) -> list[np.ndarray]:
        """
        Return the list of images of a specific set of images.
        :param index: Index of the set to get images list.
        :return: List of images of a specific set of images.
        """
        return self.images_sets.get_images_set(index)

    def load_images_set_from_file(self, filename: str = '') -> bool:
        """
        Load sets of images from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        state = self.images_sets.load_images_set_from_file(filename)
        if state:
            self.data_set_state.set_state(DataSetStateValue.IMAGES, True)
        return state

    def get_masks_list(self) -> list[np.ndarray]:
        """
        Return the list of the masks.
        :return: List of 2D-array.
        """
        return self.masks_sets.get_mask_list()

    def add_mask(self, mask: np.ndarray, type_m: str = ''):
        """Add a new mask to the list.
        :param mask: Mask to add to the list.
        :param type_m: Type of mask (Circular, Rectangular, Polygon).
        """
        self.masks_sets.add_mask(mask, type_m)
        self.data_set_state.set_state(DataSetStateValue.MASKS)

    def load_mask_from_file(self, filename: str = '') -> bool:
        """
        Load a set of mask from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        state = self.masks_sets.load_mask_from_file(filename)
        if state:
            self.data_set_state.set_state(DataSetStateValue.MASKS, True)
        return state


    def get_global_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_mask()

    def get_global_cropped_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_cropped_mask()

    def is_data_ready(self):
        """
        Check if a set of images and almost one mask are processed.
        :return: True if almost a set of images and a mask are ready.
        """
        if self.images_sets.get_number_of_sets() >= 1 and self.masks_sets.get_masks_number() >= 1:
            return True
        else:
            return False

    def save_file(self, file_path: str):
        """
        Save data and masks to a .mat file.
        :param file_path: Path and name of the file to write.
        """
        new_data = np.concatenate([np.stack(sublist, axis=-1) for sublist in self.images_sets.images_list], axis=-1)
        new_data = new_data.astype(np.uint8)
        data = {
            'Images': new_data
        }
        if self.masks_sets.get_number() != 0:
            masks_list = self.masks_sets.get_mask_list()
            masks = [m[..., np.newaxis] for m in masks_list]
            new_mask = np.concatenate(masks, axis=-1)
            new_mask = new_mask.astype(bool)
            data['Masks'] = new_mask
        scipy.io.savemat(file_path, data)

    def reset_data(self, keep_mask: bool = False):
        """Reset all the data of the data set."""
        self.images_sets.reset_all_images()
        self.data_set_state.set_state(DataSetStateValue.IMAGES, False)
        self.data_set_state.set_state(DataSetStateValue.CROPPED, False)
        self.data_set_state.set_state(DataSetStateValue.ANALYZED, False)
        self.data_set_state.set_state(DataSetStateValue.WRAPPED, False)
        self.data_set_state.set_state(DataSetStateValue.UNWRAPPED, False)
        if keep_mask is False:
            self.masks_sets.reset_masks()
            self.data_set_state.set_state(DataSetStateValue.MASKS, False)
        else:
            self.data_set_state.set_state(DataSetStateValue.MASKS, True)

    def set_masks_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.MASKS, value)

    def set_images_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.IMAGES, value)

    def set_cropped_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.CROPPED, value)

    def set_wrapped_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.WRAPPED, value)

    def set_unwrapped_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.UNWRAPPED, value)

    def set_analyzed_state(self, value: bool = True):
        self.data_set_state.set_state(DataSetStateValue.ANALYZED, value)

    def is_analyzed(self):
        return self.data_set_state.check_state(DataSetStateValue.ANALYZED)

    def is_wrapped(self):
        return self.data_set_state.check_state(DataSetStateValue.WRAPPED)

    def is_unwrapped(self):
        return self.data_set_state.check_state(DataSetStateValue.UNWRAPPED)

    def has_mask(self):
        return self.data_set_state.check_state(DataSetStateValue.MASKS)


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    number_of_images = 5
    data_set = DataSetModel(number_of_images)

    images_set = ImagesModel(number_of_images)
    if images_set.load_images_set_from_file('../_data/test3.mat'):
        data_set.add_set_images(images_set.get_images_set(1))

    if data_set.images_sets.get_number_of_sets() >= 1:
        image_1_1 = data_set.get_images_sets(1)
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


