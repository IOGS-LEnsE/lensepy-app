from xmlrpc.client import boolean

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QLineEdit, QGridLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox)

from lensepy import translate
from lensepy.css import *
from lensepy.utils import *
from scipy.ndimage import value_indices

from lensepy_app import *
from lensepy_app.widgets import *
from lensepy_app.widgets.objects import make_hline, LabelWidget, SliderBloc
from lensepy.drivers.ids_camera.ids_camera import CameraIDS
from lensepy_app.widgets.objects import LabelWidget, SelectWidget


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy_app.modules.camera.idslite.idslite_controller import IDSController

MIN_EXPO_TIME = 0.1 # ms

class CameraParamsWidget(QWidget):
    """
    Widget to display image infos.
    """
    exposure_time_changed = pyqtSignal(float)
    black_level_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent     # IDSController or equivalent
        layout = QVBoxLayout()
        # Attributes
        self.camera = self.parent.get_variables()['camera']
        # Graphical objects
        layout.addWidget(make_hline())
        label = QLabel(translate('ids_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        print(f'Camera = {self.camera}')
        # Test if camera is connected to the computer
        if self.camera is not None:
            self.label_fps = LabelWidget(translate('ids_params_fps'), '')
            layout.addWidget(self.label_fps)
            self.slider_expo = SliderBloc(translate('ids_params_slider_expo'), unit='ms',
                                          min_value=MIN_EXPO_TIME, max_value=1000)
            #self.slider_expo.slider.setEnabled(False)
            layout.addWidget(self.slider_expo)
            layout.addWidget(make_hline())
            self.slider_black_level = SliderBloc(translate('ids_params_slider_black'), unit='ADU',
                                          min_value=0, max_value=255, integer=True)
            #self.slider_black_level.slider.setEnabled(False)
            layout.addWidget(self.slider_black_level)
            layout.addWidget(make_hline())

            self.slider_expo.slider_changed.connect(self.handle_exposure_time_changed)
            self.slider_black_level.slider_changed.connect(self.handle_black_level_changed)

        else:
            nocam = QLabel(translate('no_ids_camera'))
            nocam.setStyleSheet(styleH3)
            nocam.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(nocam)

        layout.addStretch()
        self.setLayout(layout)

    def set_max_exposure_time(self, value):
        self.slider_expo.set_min_max_slider_values(MIN_EXPO_TIME, int(value))

    def handle_exposure_time_changed(self, value):
        """
        Action performed when color mode is changed.
        """
        self.exposure_time_changed.emit(value)

    def handle_black_level_changed(self, value):
        """
        Action performed when color mode is changed.
        """
        self.black_level_changed.emit(int(value))

    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera = self.parent.get_variables()['camera']
        if self.camera is not None:
            self.camera.open()
            fps_value = self.camera.get_frame_rate()
            fps = np.round(fps_value, 2)
            self.label_fps.set_value(str(fps))

    def set_black_level(self, value: int):
        self.slider_black_level.set_value(value)

    def set_exposure_time(self, value):
        self.slider_expo.set_value(value)


class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """

    mask_updated = pyqtSignal()
    mask_applied = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(None)
        # Attributes
        self.parent: IDSController = parent  # IDSController or any CameraController
        self.camera = self.parent.get_variables()['camera']
        # Graphical objects
        layout = QVBoxLayout()

        label = QLabel(translate('ids_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('ids_infos_name'), '')
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('ids_infos_serial'), '')
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('ids_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = LabelWidget(translate('ids_infos_color_mode'), '', '')
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())
        layout.addStretch()
        # End
        layout.addStretch()
        self.setLayout(layout)
        self.update_infos()

    def handle_color_mode_changed(self, event):
        """
        Action performed when color mode is changed.
        """
        self.color_mode_changed.emit(event)

    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera: CameraIDS = self.parent.get_variables()['camera']
        if self.parent.camera_connected:
            self.camera.open()
            serial_no, camera_name = self.camera.get_cam_info()
            self.label_name.set_value(camera_name)
            self.label_serial.set_value(serial_no)
            width, height = self.camera.get_sensor_size()
            w = str(width)
            h = str(height)
            self.label_size.set_value(f'WxH = {w} x {h}')
        else:
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')
