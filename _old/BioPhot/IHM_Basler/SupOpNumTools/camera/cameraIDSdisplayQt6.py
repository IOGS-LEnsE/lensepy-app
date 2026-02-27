# -*- coding: utf-8 -*-
"""IDS Camera Widget library.

/!\ Only for IDS USB 2.0 CMOS camera
Based on pyueye library

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/01/01


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python cameraIDSdisplay.py
"""
# Standard Libraries
import time

import numpy as np
import cv2

# Third pary imports
from PyQt6.QtWidgets import QWidget, QComboBox, QPushButton
from PyQt6.QtWidgets import QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6 import QtGui

# Local libraries
import SupOpNumTools as sont
import SupOpNumTools.camera.cameraIDS as camIDS
import SupOpNumTools.camera.cameraBasler as camBAS


class CameraIDSError(Exception):
    """
    
    """
    
    def __init__(self, error_mode="camDisp_ERROR"):
        self.error_mode = error_mode
        super().__init__(self.error_mode)


class CameraIDSDisplay(QWidget):
    """
    cameraIDSDisplay class to create a QWidget for camera display.
    Children of QWidget 
    ---
    
    Attributes
    ----------
    camera: camera
        Camera uses in the application - IDS CMOS Sensor only (for the moment).
    cb_list_cam: list
        List of all the IDS connected camera.
    camera_connected: bool
        Returns true if a camera is connected.
    user_color_mode: str
        "MONO8", "MONO10", "MONO12" or "RGB"
        converts by get_cam_color_mode from cameraIDS module
    min_width: int
        Minimum width of the widget.
    max_width: int
        Maximum width of the widget.
    exposure_time: float
        Exposure time of the camera.
    FPS: float
        Frame rate in frame per second.
    
    Methods
    -------
    connectCam():
        Initializes the USB connexion to the camera.
    closeEvent(event):
        Closes the application properly.
    """
    
    connected_signal = pyqtSignal(str)
    
    def __init__(self, cam = None):
        super().__init__() 
        
        # Camera
        self.camera = cam
        self.max_width = -1
        self.max_height = -1
        self.camera_connected = False
        # List of cameras
        self.nb_cam = 0
        self.camera_list = []
        self.selected_camera = 0
        # Camera Parameters
        self.user_color_mode = "MONO12"
        self.expo_min = 0
        self.expo_max = 0
        self.min_fps = 0
        self.max_fps = 0
        self.color_mode = ''
        self.exposure_time = 20.0
        self.FPS = 10
        self.n_bits_per_pixel = 0
        self.bytes_per_pixel = int(np.ceil(self.n_bits_per_pixel / 8))
        self.camera_raw_array = np.array([])

        self.main_layout = QVBoxLayout()
        
        # Elements for List of camera        
        self.label_no_cam = QLabel('NO CAMERA')
        self.cb_list_cam = QComboBox()
        self.bt_connect = QPushButton('Connect')
        self.bt_connect.clicked.connect(self.connect_cam)
        self.bt_refresh = QPushButton('Refresh')
        self.bt_refresh.clicked.connect(self.display_list)

        # Elements for displaying camera
        self.camera_display = QLabel()
        
        # Display list or camera
        self.display_list()
        
        # Graphical interface
        self.setLayout(self.main_layout)

    def clear_layout(self):
        count = self.main_layout.count()
        for i in reversed(range(count)):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def display_list(self):
        """
        Calls to display connection panel.

        Returns
        -------
        None.

        """
        if self.camera_connected:
            self.camera.stop_camera()     
            self.camera_connected = False
            
        self.main_layout.addWidget(self.label_no_cam)
        self.main_layout.addWidget(self.cb_list_cam)
        self.main_layout.addWidget(self.bt_connect)
        self.main_layout.addWidget(self.bt_refresh)
        
        self.setLayout(self.main_layout)
        self.nb_cam_IDS = camIDS.get_nb_of_cam()
        self.cb_list_cam.clear()
        if self.nb_cam_IDS > 0:
            self.camera_list_IDS = camIDS.get_cam_list() 
            for i in range(self.nb_cam_IDS):
                camera_t = self.camera_list_IDS[i]
                self.cb_list_cam.addItem(f'{camera_t[2]} (SN : {camera_t[1]})')
        self.nb_cam_BAS = camBAS.get_nb_of_cam()
        if self.nb_cam_BAS > 0:
            self.camera_list_BAS = camBAS.get_cam_list() 
            for i in range(self.nb_cam_BAS):
                camera_t = self.camera_list_BAS[i]
                self.cb_list_cam.addItem(f'{camera_t[2]} (SN : {camera_t[1]})')

    def connect_cam(self):
        """
        Event link to the connect button of the GUI.

        Returns
        -------
        None.

        """
        self.selected_camera = self.cb_list_cam.currentIndex()
        self.camera = camIDS.uEyeCamera(self.selected_camera)
        self.camera_connected = True
        
        self.max_width = self.camera.get_sensor_max_width()
        self.max_height = self.camera.get_sensor_max_height()
        
        self.camera.set_pixel_clock(50)
        
        self.min_fps, self.max_fps, step_fps = self.camera.get_frame_time_range()
        self.min_fps, self.max_fps, step_fps = self.camera.get_frame_rate_range()
        self.FPS = self.max_fps / 2       
        self.camera.set_frame_rate(self.FPS)
        self.expo_min, self.expo_max = self.camera.get_exposure_range()
        self.exposure_time = self.expo_max/2
        self.camera.set_exposure_time(self.exposure_time)
        print(self.color_mode_list())
        self.set_color_mode(self.user_color_mode)
        self.camera.set_aoi(0, 0, self.max_width, self.max_height)        
        self.n_bits_per_pixel = self.camera.nBitsPerPixel.value
        self.bytes_per_pixel = int(np.ceil(self.n_bits_per_pixel / 8))
        self.clear_layout()
        self.connected_signal.emit('C')
      
    def start_cam(self):
        if self.camera_connected:
            self.camera.alloc()
            self.camera.capture_video()
    
    def stop_cam(self):
        if self.camera_connected:
            self.camera.stop_video()
            self.camera.un_alloc()

    def color_mode_list(self):
        list = []
        if self.camera.is_colormode(camIDS.get_cam_color_mode('RGB')):
            list.append('RGB')
        if self.camera.is_colormode(camIDS.get_cam_color_mode('MONO12')):
            list.append('MONO12')
        if self.camera.is_colormode(camIDS.get_cam_color_mode('MONO10')):
            list.append('MONO10')
        if self.camera.is_colormode(camIDS.get_cam_color_mode('MONO8')):
            list.append('MONO8')
        return list

    def refresh(self):
        '''
        Refresh the displaying image from camera.

        Returns
        -------
        None.
        '''
        if self.camera_connected:
            self.main_layout.addWidget(self.camera_display)
            
            self.camera_raw_array = self.camera.get_image()

            AOIX, AOIY, AOIWidth, AOIHeight = self.camera.get_aoi()

            # Raw data and display frame depends on bytes number per pixel
            if self.bytes_per_pixel >= 2:
                # Raw data array for analysis
                self.camera_raw_frame = self.camera_raw_array.view(np.uint16)
                self.camera_frame = np.reshape(self.camera_raw_frame, 
                                               (AOIHeight, AOIWidth, -1))
                
                # 8bits array for frame displaying.
                camera_frame_8b = self.camera_frame / (2**(self.n_bits_per_pixel-8))
                self.camera_array = camera_frame_8b.astype(np.uint8)    
            else:
                self.camera_raw_frame = self.camera_raw_array.view(np.uint8)
                self.camera_array = self.camera_raw_frame
            
            
            self.frame_width = self.width()-30
            self.frame_height = self.height()-20
            # Reshape of the frame to adapt it to the widget
            self.camera_disp = np.reshape(self.camera_array, 
                                         (AOIHeight, AOIWidth, -1))
            self.camera_disp2 = cv2.resize(self.camera_disp,
                                         dsize=(self.frame_width, 
                                                self.frame_height), 
                                         interpolation=cv2.INTER_CUBIC)
            
            # Convert the frame into an image
            image = QImage(self.camera_disp2, self.camera_disp2.shape[1],
                           self.camera_disp2.shape[0], self.camera_disp2.shape[1],
                           QImage.Format.Format_Indexed8)
            pmap = QPixmap(image)

            # display it in the cameraDisplay
            self.camera_display.setPixmap(pmap)

    def get_camera_width(self):
        return int(self.camera.get_sensor_max_width())

    def get_camera_height(self):
        return int(self.camera.get_sensor_max_height())

    def disconnect(self):
        if self.camera_connected:
            self.camera.stop_camera()
            self.camera_connected = False

    def get_image_raw(self):
        """
        Return reshaped image from camera.

        Returns
        -------
        image : numpy array
            raw image in full size
        """
        return self.camera_disp
          
    def get_raw_data(self):
        return self.camera_raw_frame

    def get_camera(self):
        return self.camera
    
    def get_exposure_time(self):
        return self.exposure_time

    def set_exposure_time(self, time):
        if self.expo_max >= time >= self.expo_min:
            self.exposure_time = time
        else:
            raise CameraIDSError("exposure_time_Error - No change")
        self.camera.set_exposure_time(self.exposure_time)
    
    def get_exposure_range(self):
        return self.expo_min, self.expo_max
    
    def set_frame_rate(self, fps):
        """
        Update the frame rate with the FPS value.
        Also update new exposure time range.

        Parameters
        ----------
        fps : float
            Value of the Frame Rate.

        Returns
        -------
        None.
        """
        if self.max_fps >= fps >= self.min_fps:
            self.FPS = fps
        '''
        else:
            raise cameraIDS_ERROR("fps_Error - No change")
        '''
        self.camera.set_frame_rate(self.FPS)
        self.expo_min, self.expo_max = self.camera.get_exposure_range()
        self.exposure_time = self.expo_max / 2
        self.camera.set_exposure_time(self.exposure_time)
        
    def get_frame_rate_range(self):
        return self.min_fps, self.max_fps

    def get_frame_rate(self):
        """
        Returns the frame rate of the camera.

        Returns
        -------
        float
            Frame rate of the camera.

        """
        return self.FPS

    def is_camera_connected(self):
        return self.camera_connected

    def set_color_mode(self, color_user_mode):
        temp_mode = camIDS.get_cam_color_mode(color_user_mode)
        ret = self.camera.is_colormode(temp_mode)
        if ret:
            self.color_mode = temp_mode
            self.camera.set_colormode(self.color_mode)
            return True
        else:
            return False

    def get_color_mode(self):
        return self.color_mode

    def print_cam_info(self):
        if(self.camera_connected):
            print('\n\tCamera Info\n')
            print(f'\t\tFPS : {self.FPS} fps')
            print(f'\t\texpo Time : {self.exposure_time} ms')
            print(f'\t\tPixel Clock : {self.camera.get_pixel_clock()} MHz')
        else:
            print('No Camera Connected')

    def get_nb_bits_per_pixel(self):
        return self.n_bits_per_pixel

    def set_blacklevel(self, value):
        self.camera.set_black_level(int(value))

    def get_blacklevel(self):
        return self.camera.get_black_level()

    def get_pixel_clock(self):
        return self.camera.get_pixel_clock()

    def set_aoi(self, x, y, width, height):
        if self.is_aoi_in_range(x, y, width, height):
            print('OK2')
            self.camera.set_aoi(x, y, width, height)
        else:
            print('AOI Range Error')

    def is_aoi_in_range(self, x, y, x_size, y_size):
        error_nb = 0
        x_max = self.camera.get_sensor_max_width()
        y_max = self.camera.get_sensor_max_height()
        # Test if values are in the good range
        if error_nb == 0:
            x = int(x)
            y = int(y)
            x_size = int(x_size)
            y_size = int(y_size)
            if not (0 <= x < x_max) or not (0 <= y < y_max):
                error_nb += 1
                print('error RANGE X/Y')
            if not (0 < x + x_size <= x_max) or not (0 < y + y_size <= y_max):
                error_nb += 1
                print('error RANGE Size')
        if error_nb == 0:
            return True
        else:
            return False

'''
CameraIDSmainParams class
Update main parameters of an IDS Camera (exposure time, AOI...)
'''
class cameraIDSmainParams(QWidget):
    
    expo_signal = pyqtSignal(str)
    fps_signal = pyqtSignal(str)
    blacklevel_signal = pyqtSignal(str)

    
    def __init__(self):
        super().__init__() 
        
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.name_label = QLabel('Camera Parameters')
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.name_label, 0, 0)

        # Elements of the widget
        self.fps_bl = sont.SliderBlock()
        self.fps_bl.set_units('fps')
        self.fps_bl.set_name('FramePerSec')
        self.fps_bl.slider_changed_signal.connect(self.send_signal_fps)
        self.main_layout.addWidget(self.fps_bl, 1, 0)
        
        self.exposure_time_bl = sont.SliderBlock()
        self.exposure_time_bl.set_units('ms')
        self.exposure_time_bl.set_name('Exposure Time')
        self.exposure_time_bl.slider_changed_signal.connect(self.send_signal_expo)
        self.main_layout.addWidget(self.exposure_time_bl, 2, 0)

        self.blacklevel_bl = sont.SliderBlock()
        self.blacklevel_bl.set_units('__')
        self.blacklevel_bl.set_name('Black Level')
        self.blacklevel_bl.slider_changed_signal.connect(self.send_signal_blacklevel)
        self.blacklevel_bl.set_min_max_slider(0, 256)
        self.blacklevel_bl.set_ratio(1)
        self.main_layout.addWidget(self.blacklevel_bl, 3, 0)

        self.pixel_clock_label = QLabel('')
        self.pixel_clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.pixel_clock_label, 4, 0)


    def update(self):
        print('update Params IDS')
        
    def set_exposure_time_range(self, expo_min, expo_max):
        self.exposure_time_bl.set_min_max_slider(expo_min, expo_max)
        
    def get_exposure_time(self):
        return self.exposure_time_bl.get_real_value()
    
    def set_exposure_time(self, value):
        return self.exposure_time_bl.set_value(value)
    
    def set_FPS_range(self, fps_min, fps_max):
        self.fps_bl.set_min_max_slider(fps_min, fps_max)
        
    def get_FPS(self):
        return self.fps_bl.get_real_value()
    
    def set_FPS(self, value):
        return self.fps_bl.set_value(value)

    def send_signal_expo(self, event):
        self.expo_signal.emit('expo')

    def send_signal_fps(self, event):
        self.fps_signal.emit('fps')

    def send_signal_blacklevel(self, event):
        self.blacklevel_signal.emit('blacklevel')

    def get_blacklevel(self):
        return self.blacklevel_bl.get_real_value()

    def set_blacklevel(self, value):
        self.blacklevel_bl.set_value(value)

    def set_pixel_clock(self, value):
        self.pixel_clock_label.setText(f'Pixel Clock = {value} MHz')
