import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, \
    QMessageBox, QGridLayout
from lensepy.css import *
from lensepy import translate
from lensepy.modules.camera.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline, process_hist_from_array, save_hist, save_slice
from lensepy.widgets import LabelWidget, SliderBloc, HistogramWidget, CameraParamsWidget, LineEditWidget
import numpy as np



class SliceMeasurementWidget(QWidget):
    """
    Widget to display information about slices.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Graphical objects
        label = QLabel(translate('slice_measurement_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout().addWidget(label)
        self.layout().addWidget(make_hline())
        # X0, Y0, X1, Y1, W, H - horizontal
        widget_hor_meas = QWidget()
        layout = QGridLayout()
        widget_hor_meas.setLayout(layout)
        label = QLabel(translate('hor_slice_measurement_title'))
        label.setStyleSheet(styleH3)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(label)
        self.layout().addWidget(make_hline())
        self.x0_h_label = LineEditWidget(translate('slice_x0'), value='')
        self.x0_h_label.setStyleSheet(styleH2)
        self.y0_h_label = LineEditWidget(translate('slice_y0'), value='')
        self.y0_h_label.setStyleSheet(styleH2)
        self.x1_h_label = LineEditWidget(translate('slice_x1'), value='')
        self.x1_h_label.setStyleSheet(styleH2)
        self.y1_h_label = LineEditWidget(translate('slice_y1'), value='')
        self.y1_h_label.setStyleSheet(styleH2)
        # Width and Height
        self.w_h_label = LineEditWidget(translate('slice_w'), value='')
        self.w_h_label.setStyleSheet(styleH2)
        self.h_h_label = LineEditWidget(translate('slice_h'), value='')
        self.h_h_label.setStyleSheet(styleH2)

        layout.addWidget(self.x0_h_label, 0, 0)
        layout.addWidget(self.y0_h_label, 0, 1)
        layout.addWidget(self.x1_h_label, 1, 0)
        layout.addWidget(self.y1_h_label, 1, 1)
        layout.addWidget(self.w_h_label, 2, 0)
        layout.addWidget(self.h_h_label, 2, 1)
        self.layout().addWidget(widget_hor_meas)

        # X0, Y0, X1, Y1, W, H - vertical
        widget_ver_meas = QWidget()
        layout = QGridLayout()
        widget_ver_meas.setLayout(layout)
        label = QLabel(translate('ver_slice_measurement_title'))
        label.setStyleSheet(styleH3)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(label)
        self.layout().addWidget(make_hline())
        self.x0_v_label = LineEditWidget(translate('slice_x0'), value='')
        self.x0_v_label.setStyleSheet(styleH2)
        self.y0_v_label = LineEditWidget(translate('slice_y0'), value='')
        self.y0_v_label.setStyleSheet(styleH2)
        self.x1_v_label = LineEditWidget(translate('slice_x1'), value='')
        self.x1_v_label.setStyleSheet(styleH2)
        self.y1_v_label = LineEditWidget(translate('slice_y1'), value='')
        self.y1_v_label.setStyleSheet(styleH2)
        # Width and Height
        self.w_v_label = LineEditWidget(translate('slice_w'), value='')
        self.w_v_label.setStyleSheet(styleH2)
        self.h_v_label = LineEditWidget(translate('slice_h'), value='')
        self.h_v_label.setStyleSheet(styleH2)

        layout.addWidget(self.x0_v_label, 0, 0)
        layout.addWidget(self.y0_v_label, 0, 1)
        layout.addWidget(self.x1_v_label, 1, 0)
        layout.addWidget(self.y1_v_label, 1, 1)
        layout.addWidget(self.w_v_label, 2, 0)
        layout.addWidget(self.h_v_label, 2, 1)
        self.layout().addWidget(widget_ver_meas)

        self.layout().addStretch()

    def set_horizontal_xy(self, x0, y0, x1, y1):
        self.x0_h_label.set_value(str(x0))
        self.y0_h_label.set_value(str(y0))
        self.x1_h_label.set_value(str(x1))
        self.y1_h_label.set_value(str(y1))

    def set_vertical_xy(self, x0, y0, x1, y1):
        self.x0_v_label.set_value(str(x0))
        self.y0_v_label.set_value(str(y0))
        self.x1_v_label.set_value(str(x1))
        self.y1_v_label.set_value(str(y1))