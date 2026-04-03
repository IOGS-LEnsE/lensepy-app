from pyueye import ueye
import numpy as np


class CameraIDS2:

    def __init__(self):
        self.h_cam = None  # Handle de la caméra
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()
        self.width = 0
        self.height = 0
        self.color_mode = ueye.IS_CM_MONO8  # Monochrome
        self.exposure = ueye.double(100.0)  # microseconds

    def find_first_camera(self):
        if not CameraIDS.is_connected():
            return False

        self.h_cam = ueye.HIDS(0)
        if self.h_cam:
            # Camera initialization
            ueye.is_InitCamera(self.h_cam, None)

            ueye.is_SetBinning(self.h_cam, ueye.IS_BINNING_DISABLE)
            ueye.is_SetSubSampling(self.h_cam, ueye.IS_SUBSAMPLING_DISABLE)

            # AOI
            rect_aoi = ueye.IS_RECT()
            ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

            self.width = int(rect_aoi.s32Width)
            self.height = int(rect_aoi.s32Height)
            print(f'Camera Size = {self.width} / {self.height}')

            # Allocation of memory
            ueye.is_AllocImageMem(self.h_cam, self.width, self.height, 8, self.mem_ptr, self.mem_id)
            ueye.is_SetImageMem(self.h_cam, self.mem_ptr, self.mem_id)

            # Start acquisition
            try:
                ueye.is_CaptureVideo(self.h_cam, ueye.IS_DONT_WAIT)
                return True
            except ueye.UeyeError as e:
                print(f"Erreur uEye : {e}")
                return False
            except Exception as e:
                print(f"Erreur inattendue : {e}")
                return False

        print('No H_CAM')
        return False

    def set_exposure(self, exposure_us):
        """Définir le temps d'intégration (microsecondes)"""
        self.exposure = ueye.double(exposure_us)
        ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, self.exposure, ueye.sizeof(self.exposure))

    def set_color_mode(self, color=True):
        """Définir le type d'image : True pour couleur, False pour monochrome"""
        if color:
            self.color_mode = ueye.IS_CM_BGRA8_PACKED
        else:
            self.color_mode = ueye.IS_CM_MONO8
        ueye.is_SetColorMode(self.h_cam, self.color_mode)

    def get_image(self):
        """Get an image as a numpy array."""
        ueye.is_CaptureVideo(self.h_cam, ueye.IS_DONT_WAIT)
        pitch = ueye.int()
        ueye.is_GetImageMemPitch(self.h_cam, pitch)
        array = ueye.get_data(
            self.mem_ptr,
            self.width,
            self.height,
            8,  # bits per pixel (ex: 8 pour mono)
            pitch,
            True  # copy → IMPORTANT
        )
        image = np.reshape(array, (self.height, self.width))
        return image

    def is_connected(self):
        return self.h_cam is not None

    @staticmethod
    def is_connected():
        """Test if almost one camera is connected."""
        num_cams = ueye.INT()
        if ueye.is_GetNumberOfCameras(num_cams) == ueye.IS_SUCCESS:
            return num_cams.value > 0
        return False

    def close(self):
        """Free all ressources."""
        ueye.is_FreeImageMem(self.h_cam, self.mem_ptr, self.mem_id)
        ueye.is_ExitCamera(self.h_cam)

# FROM OLD VERSION
"""
.. warning::

    **IDS peak** (2.8 or higher) and **IDS Sofware Suite** (4.95 or higher) softwares
    are required on your computer.

    For old IDS camera, IDS peak must be installed in Custom mode with the Transport Layer option.

    **IDS peak IPL** (Image Processing Library) and **Numpy** are required.

.. note::

    To use old IDS generation of cameras (type UI), you need to install **IDS peak** in **custom** mode
    and add the **uEye Transport Layer** option.

.. note::

    **IDS peak IPL** can be found in the *IDS peak* Python API.

    Installation file is in the directory :file:`INSTALLED_PATH_OF_IDS_PEAK\generic_sdk\ipl\binding\python\wheel\x86_[32|64]`.

    Then run this command in a shell (depending on your python version and computer architecture):

    .. code-block:: bash

        pip install ids_peak_1.2.4.1-cp<version>-cp<version>m-[win32|win_amd64].whl

    Generally *INSTALLED_PATH_OF_IDS_PEAK* is :file:`C:\Program Files\IDS\ids_peak`

@ see : https://www.1stvision.com/cameras/IDS/IDS-manuals/en/index.html
@ See API DOC : C:\Program Files\IDS\ids_peak\generic_sdk\api\doc\html
"""

from ids_peak import ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl

class CameraIDS:
    """Class to communicate with an IDS camera sensor.

    :param camera: Camera object that can be controlled.
    :type camera: ids_peak.Device

    TO COMPLETE

    .. note::

        In the context of this driver,
        the following color modes are available :

        * 'Mono8' : monochromatic mode in 8 bits raw data
        * 'Mono10' : monochromatic mode in 10 bits raw data
        * 'Mono12' : monochromatic mode in 12 bits raw data
        * 'RGB8' : RGB mode in 8 bits raw data

    """

    def __init__(self, camera_device: ids_peak.Device = None) -> None:
        """"""
        self.camera_device = camera_device
        if self.camera_device is None:
            self.camera_connected = False
        else:  # A camera device is connected
            self.camera_connected = True
        self.camera_acquiring = False  # The camera is acquiring
        self.__camera_acquiring = False  # The camera is acquiring old value
        self.camera_remote = None
        self.data_stream = None
        # Camera parameters
        self.color_mode = None
        self.nb_bits_per_pixels = 8

    def list_cameras(self):
        pass

    def find_first_camera(self) -> bool:
        """Create an instance with the first IDS available camera.

        :return: True if an IDS camera is connected.
        :rtype: bool
        """
        # Initialize library
        ids_peak.Library.Initialize()
        # Create a DeviceManager object
        device_manager = ids_peak.DeviceManager.Instance()
        try:
            # Update the DeviceManager
            device_manager.Update()
            # Exit program if no device was found
            if device_manager.Devices().empty():
                print("No device found. Exiting Program.")
                return False
            self.camera_device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)
            self.camera_connected = True
            return True
        except Exception as e:
            print(f'Exception - find_first_camera : {e}')

    def get_camera_device(self):
        """Get Camera device."""
        return self.camera_device

    def get_log_mode(self):
        # self.camera_remote.FindNode("LogMode").SetCurrentEntry('Off')
        log_mode = self.camera_remote.FindNode("LogMode").CurrentEntry().SymbolicValue()
        print(f'Log Mode = {log_mode}')

    def get_cam_info(self) -> tuple[str, str]:
        """Return the serial number and the name.

        :return: the serial number and the name of the camera
        :rtype: tuple[str, str]

        # >>> my_cam.get_cam_info
        ('40282239', 'a2A1920-160ucBAS')

        """
        serial_no, camera_name = None, None
        try:
            camera_name = self.camera_device.ModelName()
            serial_no = self.camera_device.SerialNumber()
            return serial_no, camera_name
        except Exception as e:
            print("Exception - get_cam_info: " + str(e) + "")

    def get_sensor_size(self) -> tuple[int, int]:
        """Return the width and the height of the sensor.

        :return: the width and the height of the sensor in pixels
        :rtype: tuple[int, int]

        .. warning::

            This function requires a camera remote given by the :code:`init_camera()` function.

        # >>> my_cam.get_sensor_size()
        (1936, 1216)

        """
        try:
            max_height = self.camera_remote.FindNode("HeightMax").Value()
            max_width = self.camera_remote.FindNode("WidthMax").Value()
            return max_width, max_height
        except Exception as e:
            print("Exception - get_sensor_size: " + str(e) + "")

    def init_camera(self, camera_device=None, mode_max: bool = False):
        """
        Initialize parameters of the camera.
        :param camera_device:
        :param mode_max:
        :return:
        """
        if camera_device is None:
            if self.camera_connected:
                self.camera_remote = self.camera_device.RemoteDevice().NodeMaps()[0]
                self.camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
                self.camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
                self.camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")

                if mode_max is True:
                    # List of modes
                    color_mode_list = self.list_color_modes()
                    # Change to maximum color mode
                    max_mode = color_mode_list[len(color_mode_list) - 1]
                    self.set_color_mode(max_mode)
                    self.nb_bits_per_pixels = get_bits_per_pixel(max_mode)

        else:
            self.camera_device = camera_device
            self.camera_remote = camera_device.RemoteDevice().NodeMaps()[0]
            self.camera_remote.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
            self.camera_remote.FindNode("TriggerSource").SetCurrentEntry("Software")
            self.camera_remote.FindNode("TriggerMode").SetCurrentEntry("On")
            self.camera_connected = True
        self.color_mode = self.get_color_mode()

    def alloc_memory(self) -> bool:
        """Alloc the memory to get an image from the camera."""
        if self.camera_connected:
            data_streams = self.camera_device.DataStreams()
            if data_streams.empty():
                return False
            self.data_stream = data_streams[0].OpenDataStream()
            # Flush queue and prepare all buffers for revoking
            self.data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
            # Clear all old buffers
            for buffer in self.data_stream.AnnouncedBuffers():
                self.data_stream.RevokeBuffer(buffer)
            payload_size = self.camera_remote.FindNode("PayloadSize").Value()
            # Get number of minimum required buffers
            num_buffers_min_required = self.data_stream.NumBuffersAnnouncedMinRequired()
            # Alloc buffers
            for count in range(num_buffers_min_required):
                buffer = self.data_stream.AllocAndAnnounceBuffer(payload_size)
                self.data_stream.QueueBuffer(buffer)
            return True
        else:
            return False

    def free_memory(self) -> None:
        """
        Free memory containing the data stream.
        """
        self.data_stream = None

    def start_acquisition(self) -> bool:
        """Start acquisition.
        :return: True if the acquisition is started.
        """
        time.sleep(0.02)
        if self.camera_acquiring is False:
            try:
                self.data_stream.StartAcquisition(ids_peak.AcquisitionStartMode_Default)
                self.camera_remote.FindNode("TLParamsLocked").SetValue(1)
                self.camera_remote.FindNode("AcquisitionStart").Execute()
                self.camera_remote.FindNode("AcquisitionStart").WaitUntilDone()
                self.camera_acquiring = True
                self.__camera_acquiring = True
                return True
            except Exception as e:
                print(f'Exception start_acquisition {e}')
        return False

    def stop_acquisition(self):
        """Stop acquisition"""
        time.sleep(0.02)
        if self.camera_acquiring is True:
            self.camera_remote.FindNode("AcquisitionStop").Execute()
            self.camera_remote.FindNode("AcquisitionStop").WaitUntilDone()
            self.camera_remote.FindNode("TLParamsLocked").SetValue(0)
            self.data_stream.StopAcquisition()
            self.camera_acquiring = False
            self.__camera_acquiring = False

    def disconnect(self) -> None:
        """Disconnect the camera.
        """
        self.stop_acquisition()
        self.free_memory()
        for buffer in self.data_stream.AnnouncedBuffers():
            self.data_stream.RevokeBuffer(buffer)

    def destroy_camera(self, index: int = 0) -> None:
        self.camera_device = None

    def set_mode(self):
        """Set the mode of acquisition : Continuous or SingleFrame"""
        pass

    def get_image(self, fast_mode: bool = True) -> np.ndarray:
        """Collect an image from the camera.
        :param fast_mode: If True, raw data without any transformation are returned.
            This mode is required for live display.
            To get the formatted data (8-10-12 bits), fast_mode must be set as False.
        """
        if self.camera_connected and self.camera_acquiring:
            time.sleep(0.001)
            # trigger image
            self.camera_remote.FindNode("TriggerSoftware").Execute()
            buffer = self.data_stream.WaitForFinishedBuffer(4000)
            # convert to RGB
            raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(),
                                                              buffer.Size(), buffer.Width(), buffer.Height())
            self.data_stream.QueueBuffer(buffer)

            if self.color_mode == 'Mono12g24IDS':  # NOT YET IMPLEMENTED FOR CONVERSION ! See __init__.py
                raw_convert = raw_image.ConvertTo(ids_ipl.PixelFormatName_Mono12g24IDS,
                                                  ids_ipl.ConversionMode_Fast)
                picture = raw_convert.get_numpy_3D().copy()
            elif 'Mono' in self.color_mode:
                picture = raw_image.get_numpy_3D().copy()
            else:
                raw_convert = raw_image.ConvertTo(ids_ipl.PixelFormatName_BGRa8, ids_ipl.ConversionMode_Fast)
                picture = raw_convert.get_numpy_3D().copy()
                if len(picture.shape) > 2:
                    picture = picture[:, :, :3]

            if fast_mode:
                return picture
            else:
                # Depending on the color mode - display only in 8 bits mono
                nb_bits = get_bits_per_pixel(self.color_mode)
                if nb_bits > 8:
                    picture = picture.view(np.uint16)
                    pow_2 = 16 - nb_bits
                    picture = picture * 2 ** pow_2
                else:
                    picture = picture.view(np.uint8)
                return picture.squeeze()
        else:
            return None

    def get_color_mode(self):
        """Get the color mode.

        :param colormode: Color mode to use for the device
        :type colormode: str, default 'Mono8'

        # >>> my_cam.get_color_mode()
        'Mono8'

        """
        try:
            print(f'Get Color Mode')
            # Test if the camera is opened
            if self.camera_connected:
                self.stop_acquisition()
            pixel_format = self.camera_remote.FindNode("PixelFormat").CurrentEntry().SymbolicValue()
            self.color_mode = pixel_format
            if self.__camera_acquiring:
                self.start_acquisition()
            return pixel_format
        except Exception as e:
            print("Exception - get_color_mode: " + str(e) + "")

    def set_color_mode(self, color_mode: str) -> None:
        """Change the color mode.

        :param color_mode: Color mode to use for the device
        :type color_mode: str, default 'Mono8'

        """
        try:
            if self.camera_connected:
                self.stop_acquisition()
            self.camera_remote.FindNode("PixelFormat").SetCurrentEntry(color_mode)
            self.color_mode = color_mode
            self.color_mode = self.get_color_mode()
            self.nb_bits_per_pixels = get_bits_per_pixel(color_mode)
            # self.set_display_mode(color_mode)
            if self.__camera_acquiring:
                self.start_acquisition()
        except Exception as e:
            print("Exception - set_color_mode: " + str(e) + "")

    def list_color_modes(self):
        """
        Return a list of the different available color modes.

        See : https://www.1stvision.com/cameras/IDS/IDS-manuals/en/pixel-format.html

        :return: List of the different available color modes (PixelFormat)
        :rtype: list
        """
        color_modes = self.camera_remote.FindNode("PixelFormat").Entries()
        color_modes_list = []
        for entry in color_modes:
            if (entry.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
                    and entry.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented):
                color_modes_list.append(entry.SymbolicValue())

        return color_modes_list

    def set_aoi(self, x0, y0, width, height) -> bool:
        """Set the area of interest (aoi).

        :param x0: coordinate on X-axis of the top-left corner of the aoi must be dividable without rest by Inc = 4.
        :type x0: int
        :param y0: coordinate on X-axis of the top-left corner of the aoi must be dividable without rest by Inc = 4.
        :type y0: int
        :param width: width of the aoi
        :type width: int
        :param height: height of the aoi
        :type height: int
        :return: True if the aoi is modified
        :rtype: bool

        """
        if self.__check_range(x0, y0) is False or self.__check_range(x0 + width, y0 + height) is False:
            return False

        # Get the minimum ROI and set it. After that there are no size restrictions anymore
        x_min = self.camera_remote.FindNode("OffsetX").Minimum()
        y_min = self.camera_remote.FindNode("OffsetY").Minimum()
        w_min = self.camera_remote.FindNode("Width").Minimum()
        h_min = self.camera_remote.FindNode("Height").Minimum()

        self.camera_remote.FindNode("OffsetX").SetValue(x_min)
        self.camera_remote.FindNode("OffsetY").SetValue(y_min)
        self.camera_remote.FindNode("Width").SetValue(w_min)
        self.camera_remote.FindNode("Height").SetValue(h_min)

        # Set the new values
        self.camera_remote.FindNode("OffsetX").SetValue(x0)
        self.camera_remote.FindNode("OffsetY").SetValue(y0)
        self.camera_remote.FindNode("Width").SetValue(width)
        self.camera_remote.FindNode("Height").SetValue(height)
        return True

    def get_aoi(self) -> tuple[int, int, int, int]:
        """Return the area of interest (aoi).

        :return: [x0, y0, width, height] x0 and y0 are the
            coordinates of the top-left corner and width
            and height are the size of the aoi.
        :rtype: tuple[int, int, int, int]

        # >>> my_cam.get_aoi()
        (0, 0, 1936, 1216)

        """
        self.aoi_x0 = self.camera_remote.FindNode("OffsetX").Value()
        self.aoi_y0 = self.camera_remote.FindNode("OffsetY").Value()
        self.aoi_width = self.camera_remote.FindNode("Width").Value()
        self.aoi_height = self.camera_remote.FindNode("Height").Value()
        return self.aoi_x0, self.aoi_y0, self.aoi_width, self.aoi_height

    def reset_aoi(self) -> bool:
        """Reset the area of interest (aoi).

        Reset to the limit of the camera.

        :return: True if the aoi is modified
        :rtype: bool

        # >>> my_cam.reset_aoi()
        True

        """
        width_max, height_max = self.get_sensor_size()
        return self.set_aoi(0, 0, width_max, height_max)

    def get_exposure(self) -> float:
        """Return the exposure time in microseconds.

        :return: the exposure time in microseconds.
        :rtype: float

        # >>> my_cam.get_exposure()
        5000.0

        """
        try:
            return self.camera_remote.FindNode("ExposureTime").Value()
        except Exception as e:
            print("Exception - get exposure time: " + str(e) + "")

    def get_exposure_range(self) -> tuple[float, float]:
        """Return the range of the exposure time in microseconds.

        :return: the minimum and the maximum value
            of the exposure time in microseconds.
        :rtype: tuple[float, float]

        """
        try:
            exposure_min = self.camera_remote.FindNode("ExposureTime").Minimum()
            exposure_max = self.camera_remote.FindNode("ExposureTime").Maximum()
            return exposure_min, exposure_max
        except Exception as e:
            print("Exception - get range exposure time: " + str(e) + "")

    def set_exposure(self, exposure: float) -> bool:
        """Set the exposure time in microseconds.

        :param exposure: exposure time in microseconds.
        :type exposure: int

        :return: Return true if the exposure time changed.
        :rtype: bool
        """
        try:
            expo_min, expo_max = self.get_exposure_range()
            if check_value_in(exposure, expo_max, expo_min):
                self.camera_remote.FindNode("ExposureTime").SetValue(exposure)
                return True
            return False
        except Exception as e:
            print("Exception - set exposure time: " + str(e) + "")

    def get_frame_rate(self) -> float:
        """Return the frame rate.

        :return: the frame rate.
        :rtype: float

        # >>> my_cam.get_frame_rate()
        100.0

        """
        try:
            return self.camera_remote.FindNode("AcquisitionFrameRate").Value()
        except Exception as e:
            print("Exception - get frame rate: " + str(e) + "")

    def get_frame_rate_range(self) -> tuple[float, float]:
        """Return the range of the frame rate in frames per second.

        :return: the minimum and the maximum value
            of the frame rate in frames per second.
        :rtype: tuple[float, float]

        """
        try:
            frame_rate_min = self.camera_remote.FindNode("AcquisitionFrameRate").Minimum()
            frame_rate_max = self.camera_remote.FindNode("AcquisitionFrameRate").Maximum()
            return frame_rate_min, frame_rate_max
        except Exception as e:
            print("Exception - get range frame rate: " + str(e) + "")

    def set_frame_rate(self, fps: float) -> bool:
        """Set the frame rate in frames per second.

        :param fps: frame rate in frames per second.
        :type fps: float

        :return: Return true if the frame rate changed.
        :rtype: bool
        """
        try:
            fps_min, fps_max = self.get_frame_rate_range()
            if check_value_in(fps, fps_max, fps_min):
                self.camera_remote.FindNode("AcquisitionFrameRate").SetValue(fps)
                return True
            return False
        except Exception as e:
            print("Exception - set frame rate: " + str(e) + "")

    def get_black_level(self) -> float:
        """Return the black level.

        :return: the black level in gray scale.
        :rtype: float

        # >>> my_cam.get_black_level()
        100.0

        """
        try:
            return self.camera_remote.FindNode("BlackLevel").Value()
        except Exception as e:
            print("Exception - get black level: " + str(e) + "")

    def get_black_level_range(self) -> tuple[float, float]:
        """Return the range of the black level in gray scale.

        :return: the minimum and the maximum value
            of the black level in gray scale.
        :rtype: tuple[float, float]

        """
        try:
            bl_min = self.camera_remote.FindNode("BlackLevel").Minimum()
            bl_max = self.camera_remote.FindNode("BlackLevel").Maximum()
            return bl_min, bl_max
        except Exception as e:
            print("Exception - get range black level: " + str(e) + "")

    def set_black_level(self, black_level: int) -> bool:
        """Set the black level of the camera.

        :param black_level: Black level in gray intensity.
        :type black_level: int

        :return: Return true if the black level changed.
        :rtype: bool
        """
        try:
            bl_min, bl_max = self.get_black_level_range()
            if check_value_in(black_level, bl_max, bl_min):
                self.camera_remote.FindNode("BlackLevel").SetValue(black_level)
                return True
            return False
        except Exception as e:
            print("Exception - set frame rate: " + str(e) + "")

    def get_clock_frequency(self) -> float:
        """Return the clock frequency of the device.

        :return: clock frequency of the device in Hz.
        :rtype: float

        """
        return self.camera_remote.FindNode("DeviceClockFrequency").Value()

    def get_clock_frequency_range(self) -> tuple[float, float]:
        """Return Return the range of the clock frequency of the device.

        :return: the minimum and the maximum value
            of the clock frequency of the device in Hz.
        :rtype: tuple[float, float]

        """
        try:
            clock_min = self.camera_remote.FindNode("DeviceClockFrequency").Minimum()
            clock_max = self.camera_remote.FindNode("DeviceClockFrequency").Maximum()
            return clock_min, clock_max
        except Exception as e:
            print("Exception - get range clock frequency: " + str(e) + "")

    def set_clock_frequency(self, clock_frequency: int) -> bool:
        """Set the clock frequency of the camera.

        :param clock_frequency: Clock Frequency in Hertz.
        :type clock_frequency: int

        :return: Return true if the Clock Frequency changed.
        :rtype: bool
        """
        try:
            clock_min, clock_max = self.get_clock_frequency_range()
            if check_value_in(clock_frequency, clock_max, clock_min):
                self.camera_remote.FindNode("DeviceClockFrequency").SetValue(clock_frequency)
                return True
            return False
        except Exception as e:
            print("Exception - set clock frequency: " + str(e) + "")

    def __check_range(self, x: int, y: int) -> bool:
        """Check if the coordinates are in the sensor area.

        :param x: Coordinate to evaluate on X-axis.
        :type x: int
        :param y: Coordinate to evaluate on Y-axis.
        :type y: int

        :return: true if the coordinates are in the sensor area
        :rtype: bool

        """
        if self.camera_connected:
            width_max, height_max = self.get_sensor_size()
            if 0 <= x <= width_max and 0 <= y <= height_max:
                return True
            else:
                return False
        return False

    def is_connected(self) -> bool:
        """Return True if a camera is connected."""
        return self.camera_connected

    def get_temperature(self):
        """Return the temperature of the camera. In Celsius.
        Not implemented in old devices.
        """
        return None
        # return self.camera_remote.FindNode("DeviceTemperature").Value()

# Exemple d'utilisation
if __name__ == "__main__":

    import ids_peak.ids_peak as ids_peak

    ids_peak.Library.Initialize()
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    device_descriptors = device_manager.Devices()

    print("Found Devices: " + str(len(device_descriptors)))
    for device_descriptor in device_descriptors:
        print(device_descriptor.DisplayName())


    '''
    cam = CameraIDS()
    cam.set_exposure(20000)  # 20 ms
    cam.set_color_mode(False)  # Monochrome
    img = cam.get_image()
    print("Image capturée de taille :", img.shape)
    cam.close()
    '''