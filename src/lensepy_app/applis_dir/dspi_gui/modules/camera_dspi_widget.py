import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from lensepy import translate
from lensepy_app import *
from lensepy_app.appli import *

from typing import TYPE_CHECKING

from lensepy_app.widgets import SliderBloc

if TYPE_CHECKING:
    from DSPI.modules.basler_dspi import BaslerCamera


class CameraParamsWidget(ModuleWidget):
    """
    Widget to display image infos.
    """
    exposure_time_changed = pyqtSignal(int)
    black_level_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()

        self.camera = self.controller.get_variables()['camera']

        label = QLabel(translate("Paramètres d'acquisition"))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        # Exposure time setting
        self.slider_expo = SliderBloc(translate("Temps d'exposition - Exposure time"), unit='us',
                                      min_value=105, max_value=1000000, integer=True,
                                      parent=self.controller)
        self.slider_expo.slider.setEnabled(False)
        layout.addWidget(self.slider_expo)
        layout.addWidget(make_hline())
        # Black level setting
        self.slider_black_level = SliderBloc(translate("Black level"), unit='ADU',
                                      min_value=0, max_value=255, integer=True,
                                      parent=self.controller)
        self.slider_black_level.slider.setEnabled(False)
        layout.addWidget(self.slider_black_level)
        layout.addWidget(make_hline())

        self.slider_expo.slider_changed.connect(self.handle_exposure_time_changed)
        self.slider_black_level.slider_changed.connect(self.handle_black_level_changed)

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
        self.camera: BaslerCamera = self.parent.get_variables()['camera']
        if self.camera is not None:
            self.camera.open()
            fps_value = self.camera.get_parameter('AcquisitionFrameRate')
            fps = np.round(fps_value, 2)
            self.camera.close()

    def set_black_level(self, value: int):
        self.slider_black_level.set_value(value)

    def set_exposure_time(self, value):
        self.slider_expo.set_value(value)

