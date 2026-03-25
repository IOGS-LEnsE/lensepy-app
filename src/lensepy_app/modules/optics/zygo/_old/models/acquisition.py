# -*- coding: utf-8 -*-
"""*acquisition.py* file.

./models/acquisition.py contains AcquisitionModel class to manage the acquisition of a set of images.

Images are intensity measurements of interferences. All images have the same size.
A set of 5 images is necessary to be demodulated by the Hariharan phase
demodulation algorithm

Data are stored in MAT file, containing "Images" (set of 5 arrays in 2 dimensions)
and "Masks" objects (array(s) in 2 dimensions - same size as images).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
from enum import Enum
import numpy as np
from lensecam.ids.camera_ids import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from images import *
from masks import *
from drivers.nidaq_piezo import NIDaqPiezo
from utils.dataset_utils import generate_images_grid

number_of_images = 5

class HWState(Enum):
    STANDBY = 0
    CONNECTED = 2
    INITIALIZED = 3
    READY = 4

class AcquisitionModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """

    def __init__(self, set_size: int=5, acq_nb: int=1):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        # Hardware
        self.camera = CameraIds()
        self.camera_state = HWState.STANDBY
        self.piezo = NIDaqPiezo()
        self.piezo_state = HWState.STANDBY
        self.voltages_list = []             # Voltages for piezo movement
        # Data
        self.set_size = set_size            # Number of images of each set
        self.current_images_set = []
        self.images_sets = ImagesModel(set_size)
        self.acquisition_number = acq_nb    # Total number of acquisition to do
        self.acquisition_counter = 0        # To count number of images sets during thread
        self.images_counter = 0             # To count acquired images in a set during thread

        self.thread = None
        # Init hardware
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera_state = HWState.CONNECTED
            self.camera.init_camera() # Add test in lensecam -> True if init correctly
            self.camera_state = HWState.INITIALIZED
            if self.camera.alloc_memory():
                self.camera_state = HWState.READY

        if self.piezo.is_piezo_here() is True:
            self.piezo_state = HWState.CONNECTED

    def set_default_parameters(self, params: dict):
        """
        Set default parameters to piezo and camera.
        :param params: Dictionary of parameters.
        """
        self.camera_state = HWState.INITIALIZED
        if 'Frame Rate' in params:
            fps = float(params['Frame Rate'])
            self.camera.set_frame_rate(fps)
        if 'Exposure Time' in params:
            expo = float(params['Exposure Time'])
            self.camera.set_exposure(expo)
        self.camera.set_color_mode('Mono8')
        self.camera_state = HWState.READY

        # Default parameters to load
        self.piezo.set_channel(1)
        self.piezo_state = HWState.INITIALIZED

    def set_number_of_acq(self, value: int = 1):
        """
        Set the number of acquisition.
        :param value: Number of acquisition.
        """
        self.acquisition_number = value

    def is_possible(self):
        """
        Check if a camera (IDS) and a piezo controller (NIDaqMx) are connected.
        :return: True if acquisition is possible.
        """
        if self.piezo_state != HWState.READY:
            print('models/acquisition.py - Piezo not ready')
            return False
        if self.camera_state != HWState.READY:
            print('models/acquisition.py - Camera not ready')
            return False
        return True

    def is_camera(self) -> bool:
        """
        Check if a camera (IDS) is connected.
        :return: True if a camera is connected.
        """
        if self.camera_state == HWState.STANDBY:
            print('models/acquisition.py / is_camera - Camera not connected')
            return False
        return True

    def is_piezo(self) -> bool:
        """
        Check if a piezo controller (NIDaq) is connected.
        :return: True if a piezo controller is connected.
        """
        if self.piezo_state == HWState.STANDBY:
            print('models/acquisition.py - Piezo not connected')
            return False
        return True

    def start(self) -> bool:
        """
        Start the acquisition.
        :return: Return False if acquisition is not possible.
        """
        if self.is_possible() is False:
            return False
        self.acquisition_counter = 0
        self.current_images_set = []
        self.images_sets.reset_all_images()
        self.thread = threading.Thread(target=self.thread_acquisition)
        time.sleep(0.0001)
        self.thread.start()
        return True

    def get_image(self) -> np.ndarray:
        """
        Acquire a new image from the camera.
        :return: Captured image as an array in 2D.
        """
        return self._one_acquisition(piezo_on=False)

    def _one_acquisition(self, piezo_on: bool = True) -> np.ndarray:
        """
        Process one acquisition, depending on index of the sample and index of the set.
        :return: Captured image as an array in 2D.
        """
        if piezo_on:
            #print(f'ImCnt = {self.images_counter + 1} / {self.set_size} -- '
            #     f'SetCnt = {self.acquisition_counter + 1} / {self.acquisition_number}')
            # Move piezo
            self.piezo.write_dac(self.voltages_list[self.images_counter])
            # Wait end of movement
            time.sleep(0.3)
        # Acquire image
        image = self.camera.get_image() #fast_mode=True)
        time.sleep(0.1)
        return image

    def thread_acquisition(self):
        """
        Thread for acquisition of data.
        """
        self.camera.start_acquisition()
        if self.acquisition_counter < self.acquisition_number:
            if self.images_counter < self.set_size:
                new_image = self._one_acquisition()
                self.current_images_set.append(new_image)
                self.images_counter += 1
            else:
                self.images_sets.add_set_images(self.current_images_set)
                self.acquisition_counter += 1
                self.images_counter = 0
                self.current_images_set = []
            self.thread = threading.Thread(target=self.thread_acquisition)
            self.thread.start()
        else:
            self.camera.stop_acquisition()

    def set_exposure(self, exposure: int) -> bool:
        """
        Set the exposure time of the camera.
        :param exposure: Exposure time in microseconds.
        :return: True if the exposure time is modified.
        """
        self.camera_state = HWState.INITIALIZED
        self.camera.stop_acquisition()
        old_expo = self.camera.get_exposure()
        if self.camera.set_exposure(exposure):
            self.camera.start_acquisition()
            self.camera_state = HWState.READY
            return True
        else:
            self.camera.set_exposure(old_expo)
            self.camera.start_acquisition()
            self.camera_state = HWState.READY
            return False

    def set_voltages(self, voltage_list) -> bool:
        """
        Set the voltages list (for the piezo controller)
        :param voltage_list: List of float - in Volt.
        :return: True if voltages are set after initialization.
        """
        self.voltages_list = voltage_list
        if self.piezo_state == HWState.INITIALIZED:
            self.piezo_state = HWState.READY
            return True
        else:
            return False

    def reset_all_images(self):
        """Reset all images."""
        self.images_sets.reset_all_images()

    def get_number_of_acquisition(self) -> int:
        """Return the number of stored sets of images.
        :return: Number of stored sets of images.
        """
        return self.acquisition_counter

    def get_acquisition_index(self) -> int:
        """
        Return the index of the current sample index.
        :return: Index of the current sample index.
        """
        return self.images_counter

    def get_progress(self):
        """
        Return the progression of the current acquisition. In %.
        """
        maximum = self.acquisition_number * self.set_size
        current = (self.images_counter + 1) + (self.acquisition_counter * self.set_size)
        return int(round(current * 100 / maximum, 0))

    def get_images_set(self, index: int) -> list[np.ndarray]:
        """Return a set of N images.
        :param index: Index of the set to return.
        :return: List of images from the specified set.
        """
        if index <= self.acquisition_counter+1:
            return self.images_sets.get_images_set(index)
        return None

    def get_images_sets(self) -> ImagesModel:
        """
        Return all the sets of images.
        :return:
        """
        return self.images_sets


if __name__ == '__main__':
    from matplotlib import pyplot as plt

    nb_of_images_per_set = 5
    acquisition = AcquisitionModel(nb_of_images_per_set, acq_nb=1)
    acquisition.set_default_parameters({})
    volt_list = [0.80,1.62,2.43,3.24,4.05]
    acquisition.set_voltages(volt_list)
    if acquisition.is_camera():
        if acquisition.set_exposure(400):
            print('Expo Changed')
    if acquisition.is_possible():
        print('ACQ is possible')
        acquisition.start()

        while acquisition.get_progress() < 100:
            time.sleep(0.2)
        if acquisition.get_progress() == 100:
            acquisition.thread.join()
        time.sleep(0.2)

        new_images = acquisition.get_images_set(1)
        print(new_images[0].shape)

        image_set = ImagesModel(nb_of_images_per_set)
        image_set.add_set_images(new_images)

        ## Test class
        print(f'Number of sets = {image_set.get_number_of_sets()}')
        if image_set.get_number_of_sets() >= 1:
            image_1 = image_set.get_images_set(1)
            print(len(image_1))
            if isinstance(image_1, list):
                result = generate_images_grid(image_1)

                plt.figure()
                plt.imshow(result, cmap='gray')
                plt.show()
