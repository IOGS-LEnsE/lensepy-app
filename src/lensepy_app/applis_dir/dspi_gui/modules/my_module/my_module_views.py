import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow
)
from lensepy import translate
from lensepy_app import *
from lensepy_app.appli import *
from lensepy_app.widgets import ImageDisplayWidget

from modules.basler_dspi import BaslerDSPIController, BaslerDSPICamera
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .my_module_controller import MyModuleController

class MyModuleTopRightWidget(ModuleWidget):
    """
    Widget to select the processing mode to activate
    """
    diff_image = pyqtSignal()
    phase_shift = pyqtSignal()

    #ajout Philippe
    phase_shift_amplitude = pyqtSignal()

    stop_processing = pyqtSignal()
    enregistrer_image = pyqtSignal()
    diff_image_vibr = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Graphical objects
        layout = QVBoxLayout()
        label = QLabel('Top Right')
        layout.addWidget(label)

        self.open_button = QPushButton(translate("Enregistrer"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_enregistrer_image)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Image Difference"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_diff_image)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Image Difference Vibration"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_diff_image_vibr)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Phase Shift phase"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_phase_shift)
        layout.addWidget(self.open_button)

        """ajout philippe"""
        self.open_button = QPushButton(translate("Phase Shift amplitude"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_phase_shift_amplitude)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Stop Processing"))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_stop)
        layout.addWidget(self.open_button)

        self.setLayout(layout)

    def handle_stop(self):
        "Stop treatment"
        self.stop_processing.emit()

    def handle_diff_image(self):
        "Start Image Difference treatment"
        self.diff_image.emit()

    def handle_diff_image_vibr(self):
        "Start Image Difference treatment"
        self.diff_image_vibr.emit()

    def handle_phase_shift(self):
        "Start Image Difference treatment"
        self.phase_shift.emit()

    #ajout Philippe
    def handle_phase_shift_amplitude(self):
        "Start Image Difference treatment"
        self.phase_shift_amplitude.emit()

    def handle_enregistrer_image(self):
        "Start Image Difference treatment"
        self.enregistrer_image.emit()


class CameraWindow(QMainWindow):
    """
    Window to display the Live image grabbed by the camera
    """
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MyModuleController = parent
        # Main widget to display image
        self.camera_widget = ImageDisplayWidget()
        self.setCentralWidget(self.camera_widget)
        # Bit depth
        bits_depth = 8 # = int(self.parent.get_variables('bits_depth'))
        self.camera_widget.set_bits_depth(bits_depth)
        #Initial Image
        self.initial_image = self.parent.get_variables('image')
        if self.initial_image is not None:
            self.camera_widget.set_image_from_array(self.initial_image)