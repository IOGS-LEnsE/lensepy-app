
import os
import numpy as np
from pypylon import pylon, genicam
import cv2

def init_first_camera(filename: str = ""):
    """

    :param filename:
    """
    camera = BaslerCamera()
    if not camera.find_first_camera():
        return None
    else:
        if os.path.isfile(filename):
            camera.init_camera_parameters(filename)
        return camera


class BaslerCamera:
    """
    Class to manage Basler camera.
    """

    def __init__(self):
        """
        Basler Camera constructor.
        """
        # Variables
        self.camera_device = None
        self.camera_nodemap = None
        self.opened = False
        self.camera_acquiring = False
        self.list_params = {}
        self.initial_params = {}
        # Converter
        self.converter = pylon.ImageFormatConverter()

    @property
    def is_open(self):
        return self.opened and self.camera_device is not None and self.camera_device.IsOpen()

    def find_first_camera(self) -> bool:
        """

        :return:
        """
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()

        # Check if almost one camera is available.
        if not devices:
            return False
        else:
            # Create an instance of a Basler Camera (using pypylon wrapper).
            self.camera_device = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))
            self.camera_nodemap = self.camera_device.GetNodeMap()
            self._list_parameters()
            # self.init_camera_parameters('./config/camera.ini')
            return True

    def get_image(self):
        """
        Get image from the camera.
        :return:    Array containing the image.
        """
        if self.camera_acquiring:
            # Test if the camera is opened
            if not self.is_open:
                self.open()
            # Test if the camera is grabbing images
            if not self.camera_device.IsGrabbing():
                self.camera_device.StopGrabbing()
            # Create a list of images
            self.camera_device.StartGrabbingMax(1)
            grab_result = self.camera_device.RetrieveResult(100000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                image = grab_result.Array
            else:
                image = None

            # Free memory
            grab_result.Release()
            if image is not None and image.size > 0:
                if 'PixelFormat' in self.initial_params:
                    pixel_format = self.initial_params['PixelFormat']
                    if "Bayer" in pixel_format:
                        image = cv2.cvtColor(image, cv2.COLOR_BayerBG2RGB)
            return image
        return None

    def disconnect(self):
        """
        Disconnect the camera.
        """
        self.camera_device = None

    def open(self):
        """
        Open camera.
        """
        if self.camera_device is not None:
            if not self.opened:
                self.camera_device.Open()
                self.opened = True

    def close(self):
        """
        Open camera.
        """
        if self.camera_device is not None:
            if self.opened:
                self.camera_device.Close()
                self.opened = False

    def init_camera_parameters(self, filepath: str):
        """
        Initialize camera accessible parameters of the camera from a file.
        The txt file should have the following format:
        # comment
        key_1;value1;type1
        key_2;value2;type2

        :param filepath:    Name of a txt file containing the parameters to setup.
        """
        self.open()
        self.initial_params = {}
        if os.path.exists(filepath):
            # Read the CSV file, ignoring lines starting with '//'
            data = np.genfromtxt(filepath, delimiter=';',
                                 dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the CSV file
            for key, value, typ in data:
                match typ:
                    case 'I':
                        self.initial_params[key.strip()] = int(value.strip())
                    case 'F':
                        self.initial_params[key.strip()] = float(value.strip())
                    case 'B':
                        self.initial_params[key.strip()] = value.strip() == "True"
                    case _:
                        self.initial_params[key.strip()] = value.strip()
                self.set_parameter(key, self.initial_params[key.strip()])
        else:
            print('File error')
        self.close()

    def _list_parameters(self):
        """
        Update the list of accessible parameters of the camera.
        """
        self.open()
        self.list_params = [x for x in dir(self.camera_device) if not x.startswith("__")]

        for attr in self.list_params:
            try:
                node = self.camera_nodemap.GetNode(attr)
                if hasattr(node, "GetValue"):
                    pass
                elif hasattr(node, "Execute"):
                    self.list_params.remove(attr)
                else:
                    self.list_params.remove(attr)
            except Exception as e:
                self.list_params.remove(attr)
        self.close()

    def get_list_parameters(self) -> list:
        """
        Get the list of the accessible parameters of the camera.
        :return:    List of the accessible parameters of the camera.
        """
        return self.list_params

    def get_parameter(self, param):
        """
        Get the value of a camera parameter.
        The accessibility of the parameter is verified beforehand.
        :param param:   Name of the parameter.
        :return:        Value of the parameter if exists, else None.
        """
        if param in self.list_params:
            self.open()
            node = self.camera_nodemap.GetNode(param)
            if hasattr(node, "GetValue"):
                node_value = node.GetValue()
                self.close()
                return node_value
            else:
                self.close()
                return None
        else:
            return None

    def set_parameter(self, param, value):
        """
        Set a camera parameter to a specific value.
        The accessibility of the parameter is verified beforehand.
        :param param:   Name of the parameter.
        :param value:   Value to give to the parameter.
        """
        if param in self.list_params:
            self.open()
            node = self.camera_nodemap.GetNode(param)
            try:
                if hasattr(node, "GetAccessMode") and node.GetAccessMode() == genicam.RW:
                    if hasattr(node, "SetValue"):
                        node.SetValue(value)
                        self.initial_params[param] = value
                        self.close()
                        return True
                    else:
                        print(f"Node {param} has no SetValue()")
                else:
                    print(f"Node {param} not writable or invalid access mode")
            except Exception as e:
                print(f"Error setting parameter {param}: {e}")
        else:
            print(f"Parameter {param} not found in list_params")
        self.close()
        return False


if __name__ == "__main__":
    import time

    camera = BaslerCamera()
    camera.find_first_camera()
    camera.set_parameter('ExposureTime', 10000)
    camera.set_parameter('PixelFormat', 'Mono12')


    print(camera.get_parameter('PixelFormat'))

    new_offset_x = 62
    new_offset_y = 102
    new_width = 500
    new_height = 200
    # Attention : la somme offset + taille <= Max
    if ((new_offset_x + new_width) <= camera.get_parameter('WidthMax')
            and (new_offset_y + new_height) <= camera.get_parameter('HeightMax')):
        # Applique le ROI
        camera.set_parameter('Width', new_width)
        camera.set_parameter('Height', new_height)
        camera.set_parameter('OffsetX', new_offset_x)
        camera.set_parameter('OffsetY', new_offset_y)
    else:
        print("Erreur : ROI en dehors des limites du capteur")


    camera.camera_acquiring = True
    image = camera.get_image()
    camera.camera_acquiring = False
    camera.disconnect()

    import matplotlib.pyplot as plt
    plt.figure()
    plt.imshow(image)


    hist, bins = np.histogram(image, bins=4096, range=(0, 4095))

    # Affichage
    plt.figure(figsize=(8,4))
    plt.bar(bins[:-1], hist, width=1, color='black')
    plt.title("Histogramme de l'image")
    plt.xlabel("Intensité des pixels")
    plt.ylabel("Nombre de pixels")
    plt.show()
