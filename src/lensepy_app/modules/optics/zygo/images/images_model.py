# -*- coding: utf-8 -*-
"""
Images are intensity measurements of interferences. All images have the same size.
A set of 5 images is necessary to be demodulated by the Hariharan phase
demodulation algorithm

Data are stored in MAT file, containing "Images" (set of 5 arrays in 2 dimensions),
"Masks" objects (array(s) in 2 dimensions - same size as images) and
"Masks_Type" list.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
import scipy

from lensepy_app.modules.optics.zygo.utils import read_mat_file, split_3d_array

class ImagesSet:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.filepath = None
        self.images_list = []
        self.images_sets_number = 0

    def add_set_images(self, images: list) -> bool:
        """Add a new set of images.
        :param images: list of 5 arrays
        :return: True if the set of images has the good size.
        """
        if isinstance(images, list):
            if len(images) == self.set_size:
                self.images_list.append(images)
                self.images_sets_number += 1
                return True
        return False

    def reset_all_images(self):
        """Reset all images."""
        self.images_list.clear()
        self.images_sets_number = 0

    def get_number_of_sets(self) -> int:
        """Return the number of stored sets of images.
        :return: Number of stored sets of images.
        """
        return self.images_sets_number

    def get_images_set(self, index: int) -> list[np.ndarray]:
        """Return a set of N images.
        :param index: Index of the set to return.
        :return: List of images from the specified set.
        """
        if index <= self.images_sets_number+1:
            return self.images_list[index-1]
        return None

    def get_image_from_set(self, index: int, set_index: int = 1):
        """Return an image from its index in a specific set.
        :param index: Index of the image to return.
        :param set_index: Index of the set of the image. Default 1.
        """
        return self.images_list[set_index-1][index-1]

    def get_images_as_list(self):
        """Return all the stored images in a single list."""
        list = []
        for i in range(self.images_sets_number):
            set = self.get_images_set(i+1)
            list += set
        return list

    def load_images_set_from_file(self, filename: str = '') -> bool:
        """
        Load sets of images from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        if filename != '':
            data_from_mat = read_mat_file(filename)
            if data_from_mat is not None:
                self.filepath = filename
                # Process images from MAT file
                images_mat = data_from_mat['Images']
                images_d = split_3d_array(images_mat)

                if isinstance(images_d, list):
                    if len(images_d) % self.set_size == 0 and len(images_d) > 1:
                        self.reset_all_images()
                        for i in range(int(len(images_d) / 5)):
                            self.add_set_images(images_d[i:i + 5])
                        return True
        return False

    def save_images_set_to_file(self, filename: str = '') -> bool:
        """
        Save sets of images to a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is saved.
        """
        new_data = np.concatenate([np.stack(sublist, axis=-1) for sublist in self.images_list], axis=-1)
        new_data = new_data.astype(np.uint8)
        data = {
            'Images': new_data
        }
        scipy.io.savemat(filename, data)


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    nb_of_images_per_set = 5
    image_set = ImagesModel(nb_of_images_per_set)

    ## Open MAT file - including 'Images' and 'Masks'
    if image_set.load_images_set_from_file('../_data/test3.mat'):
        image_set.save_images_set_to_file('../_data/test_new.mat')

    ## Test class
    print(f'Number of sets = {image_set.get_number_of_sets()}')
    if image_set.get_number_of_sets() >= 1:
        image_1_1 = image_set.get_images_set(1)
        print(type(image_1_1))
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


    ## Test Save and reload file MAT
    image_set_reload = ImagesModel(nb_of_images_per_set)
    if image_set_reload.load_images_set_from_file('../_data/test_new.mat'):
        print('Images OK')
        image_2_1 = image_set_reload.get_images_set(1)
        print(type(image_2_1))


