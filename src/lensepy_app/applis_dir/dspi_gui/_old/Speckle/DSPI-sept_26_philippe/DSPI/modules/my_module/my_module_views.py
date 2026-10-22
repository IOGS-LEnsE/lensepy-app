import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, \
    QMessageBox, QGridLayout, QMainWindow
from lensepy.css import *
from lensepy import translate
from DSPI.modules.basler_dspi import BaslerDSPIController, BaslerDSPICamera
from lensepy.utils import make_hline, process_hist_from_array, save_hist, save_slice
from lensepy.widgets import LabelWidget, SliderBloc, HistogramWidget, LineEditWidget, ImageDisplayWidget, RectangleDisplayWidget
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .my_module_controller import MyModuleController

class MyModuleTopRightWidget(QWidget):
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
        super().__init__(parent)

        # Graphical objects
        layout = QVBoxLayout()
        label = QLabel('Top Right')
        layout.addWidget(label)

        self.open_button = QPushButton(translate("Enregistrer"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_enregistrer_image)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Image Difference"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_diff_image)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Image Difference Vibration"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_diff_image_vibr)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Phase Shift phase"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_phase_shift)
        layout.addWidget(self.open_button)

        """ajout philippe"""
        self.open_button = QPushButton(translate("Phase Shift amplitude"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_phase_shift_amplitude)
        layout.addWidget(self.open_button)

        self.open_button = QPushButton(translate("Stop Processing"))
        self.open_button.setStyleSheet(unactived_button)
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
        #Bit depth
        bits_depth = int(self.parent.parent.variables.get('bits_depth', 8))
        self.camera_widget.set_bits_depth(bits_depth)
        #Initial Image
        self.initial_image = self.parent.parent.variables.get('image')
        if self.initial_image is not None:
            self.camera_widget.set_image_from_array(self.initial_image)