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
from lensepy_app.widgets.objects import LabelWidget, SelectWidget


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy_app.modules.camera.basler.basler_controller import BaslerController

class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """

    mask_updated = pyqtSignal()
    mask_applied = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(None)
        # Attributes
        self.parent: BaslerController = parent  # BaslerController or any CameraController
        self.camera = self.parent.get_variables()['camera']
        # Graphical objects
        layout = QVBoxLayout()

        label = QLabel(translate('basler_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('basler_infos_name'), '')
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('basler_infos_serial'), '')
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('basler_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = LabelWidget(translate('basler_infos_color_mode'), '', '')
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())
        layout.addStretch()
        # Mask
        self.mask_button = QPushButton(translate('baslerlite_mask_button'))
        self.mask_button.setStyleSheet(unactived_button)
        self.mask_button.setFixedHeight(BUTTON_HEIGHT)
        self.mask_button.clicked.connect(self.handle_mask)
        layout.addWidget(self.mask_button)
        self.mask_apply_button = QCheckBox(translate('baslerlite_mask_apply'))
        self.mask_apply_button.setStyleSheet(styleCheckbox)
        self.mask_apply_button.stateChanged.connect(self.handle_apply_mask)
        layout.addWidget(self.mask_apply_button)
        # End
        self.activate_mask_check(False)
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
        self.camera: BaslerCamera = self.parent.get_variables()['camera']
        if self.parent.camera_connected:
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

    def handle_mask(self):
        self.mask_button.setStyleSheet(actived_button)
        self.mask_updated.emit()

    def activate_mask_button(self, value=False):
        if not value:
            self.mask_button.setStyleSheet(unactived_button)
        else:
            self.mask_button.setStyleSheet(actived_button)

    def handle_apply_mask(self):
        value = self.mask_apply_button.isChecked()
        self.mask_applied.emit(value)

    def activate_mask_check(self, value=True):
        self.mask_apply_button.setEnabled(value)
