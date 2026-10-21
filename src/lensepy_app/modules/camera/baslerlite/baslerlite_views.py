from xmlrpc.client import boolean

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QLineEdit, QGridLayout, QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox)

from lensepy import translate
from lensepy_app import *
from lensepy_app.appli import *
from lensepy.utils import *
from scipy.ndimage import value_indices

from lensepy_app import *
from lensepy_app.widgets import *
from lensepy_app.widgets.objects import LabelWidget, SelectWidget


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy_app.modules.camera.basler.basler_controller import BaslerController

class CameraInfosWidget(ModuleWidget):
    """
    Widget to display image infos.
    """

    mask_updated = pyqtSignal()
    mask_applied = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Attributes
        self.camera = self.controller.get_variables('camera')
        # Graphical objects
        layout = QVBoxLayout()

        label = QLabel(translate('basler_infos_title'))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('basler_infos_name'), '')
        self.label_name.setStyleSheet(STYLE_H3[self.global_theme][self.global_mode])
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('basler_infos_serial'), '')
        self.label_serial.setStyleSheet(STYLE_H3[self.global_theme][self.global_mode])
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('basler_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.label_size.setStyleSheet(STYLE_H3[self.global_theme][self.global_mode])
        self.color_choice = self.controller.colormode
        self.label_color_mode = LabelWidget(translate('basler_infos_color_mode'), '', '')
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
        self.camera: BaslerCamera = self.controller.get_variables('camera')
        if self.controller.camera_connected:
            self.camera.open()
            self.label_name.set_value(self.camera.get_parameter('DeviceModelName'))
            self.label_serial.set_value(self.camera.get_parameter('DeviceSerialNumber'))
            w = str(self.camera.get_parameter('SensorWidth'))
            h = str(self.camera.get_parameter('SensorHeight'))
            self.label_size.set_value(f'WxH = {w} x {h}')
            self.camera.close()
        else:
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')
