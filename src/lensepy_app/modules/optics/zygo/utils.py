import os

import numpy as np
import scipy
from enum import Flag, auto



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



class DataSetModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_sets = ImagesModel(set_size)
        self.masks_sets = MasksModel()
        self.acquisition_mode = AcquisitionModel(set_size)
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
