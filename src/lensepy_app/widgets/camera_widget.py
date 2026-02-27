import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from lensepy import translate
from lensepy.css import *
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget, SliderBloc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.basler import BaslerCamera


class CameraParamsWidget(QWidget):
    """
    Widget to display image infos.
    """
    exposure_time_changed = pyqtSignal(int)
    black_level_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent     # BaslerController or equivalent
        layout = QVBoxLayout()
        # Attributes
        self.camera = self.parent.get_variables()['camera']
        # Graphical objects
        layout.addWidget(make_hline())
        label = QLabel(translate('basler_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        # Test if camera is connected to the computer
        if self.camera is not None:

            self.label_fps = LabelWidget(translate('basler_params_fps'), '')
            layout.addWidget(self.label_fps)
            self.slider_expo = SliderBloc(translate('basler_params_slider_expo'), unit='us',
                                          min_value=20, max_value=1000000, integer=True)
            self.slider_expo.slider.setEnabled(False)
            layout.addWidget(self.slider_expo)
            layout.addWidget(make_hline())
            self.slider_black_level = SliderBloc(translate('basler_params_slider_black'), unit='ADU',
                                          min_value=0, max_value=255, integer=True)
            self.slider_black_level.slider.setEnabled(False)
            layout.addWidget(self.slider_black_level)
            layout.addWidget(make_hline())

            self.slider_expo.slider_changed.connect(self.handle_exposure_time_changed)
            self.slider_black_level.slider_changed.connect(self.handle_black_level_changed)

        else:
            nocam = QLabel(translate('no_basler_camera'))
            nocam.setStyleSheet(styleH3)
            nocam.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(nocam)

        layout.addStretch()
        self.setLayout(layout)

    def set_max_exposure_time(self, value):
        self.slider_expo.set_min_max_slider_values(20, int(value))

    def handle_exposure_time_changed(self, value):
        """
        Action performed when color mode is changed.
        """
        self.exposure_time_changed.emit(int(value))

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
            fps_value = self.camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_value, 2)
            self.label_fps.set_value(str(fps))
            self.camera.close()

    def set_black_level(self, value: int):
        self.slider_black_level.set_value(value)

    def set_exposure_time(self, value):
        self.slider_expo.set_value(value)

