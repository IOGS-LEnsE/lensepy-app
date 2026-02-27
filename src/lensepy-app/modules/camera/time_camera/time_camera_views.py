import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, \
    QMessageBox, QGridLayout
from lensepy.css import *
from lensepy import translate
from lensepy.modules.camera.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget, SliderBloc, HistogramSimpleWidget
import numpy as np


class TimeOptionsWidget(QWidget):
    """
    Widget to control camera parameters and save histogram and slices.
    """

    acquisition_started = pyqtSignal(int)
    save_data = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Attributes
        self.image_dir = None
        # Layout
        self.layout = QVBoxLayout()
        # Graphical objects
        self.camera_params = CameraParamsDisplayWidget()
        self.layout.addWidget(self.camera_params)
        # Acquisition
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        label = QLabel(translate('time_acquisition_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        self.layout.addWidget(make_hline())
        self.nb_of_points = SliderBloc(translate('nb_of_points_edit'), '',
                                       10, 2000, integer=True)
        self.nb_of_points.set_value(50)
        layout.addWidget(self.nb_of_points)
        self.start_time_acq_button = QPushButton(translate('start_time_not_button'))
        self.start_time_acq_button.setStyleSheet(disabled_button)
        self.start_time_acq_button.setEnabled(False)
        self.start_time_acq_button.setFixedHeight(BUTTON_HEIGHT)
        self.start_time_acq_button.clicked.connect(self.handle_start_acquisition)
        layout.addWidget(self.start_time_acq_button)
        self.layout.addWidget(widget)

        # Save data
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        self.save_histo_button = QPushButton(translate('save_time_histo_button'))
        self.save_histo_button.setStyleSheet(disabled_button)
        self.save_histo_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.handle_save_histogram)
        self.save_histo_button.setEnabled(False)
        layout.addWidget(self.save_histo_button)
        self.save_time_chart_button = QPushButton(translate('save_time_chart_button'))
        self.save_time_chart_button.setStyleSheet(disabled_button)
        self.save_time_chart_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_time_chart_button.clicked.connect(self.handle_save_time_chart)
        self.save_time_chart_button.setEnabled(False)
        layout.addWidget(self.save_time_chart_button)
        self.reset_data_button = QPushButton(translate('reset_data_button'))
        self.reset_data_button.setStyleSheet(disabled_button)
        self.reset_data_button.setFixedHeight(BUTTON_HEIGHT)
        self.reset_data_button.clicked.connect(self.reinit_acquisition)
        self.reset_data_button.setEnabled(False)
        layout.addWidget(self.reset_data_button)
        self.layout.addWidget(widget)
        # Data display
        self.point1_stats = QLabel('')
        self.point2_stats = QLabel('')
        self.point3_stats = QLabel('')
        self.point4_stats = QLabel('')
        self.layout.addWidget(self.point1_stats)
        self.layout.addWidget(self.point2_stats)
        self.layout.addWidget(self.point3_stats)
        self.layout.addWidget(self.point4_stats)
        self.setLayout(self.layout)

    def set_stats(self, m1, s1, m2, s2, m3, s3, m4, s4):
        """Set statistics for time data."""
        point1 = f'Point1 / Mean = {m1:.2f} - StdDev = {s1:.2f}'
        self.point1_stats.setText(point1)
        self.point1_stats.setStyleSheet(styleH3)
        point2 = f'Point2 / Mean = {m2:.2f} - StdDev = {s2:.2f}'
        self.point2_stats.setText(point2)
        self.point2_stats.setStyleSheet(styleH3)
        point3 = f'Point3 / Mean = {m3:.2f} - StdDev = {s3:.2f}'
        self.point3_stats.setText(point3)
        self.point3_stats.setStyleSheet(styleH3)
        point4 = f'Point4 / Mean = {m4:.2f} - StdDev = {s4:.2f}'
        self.point4_stats.setText(point4)
        self.point4_stats.setStyleSheet(styleH3)

    def set_start_enabled(self):
        """Set enable start button."""
        self.start_time_acq_button.setText(translate('start_time_acq_button'))
        self.start_time_acq_button.setStyleSheet(unactived_button)
        self.start_time_acq_button.setEnabled(True)

    def handle_start_acquisition(self):
        """Action performed when acquisition is started."""
        self.start_time_acq_button.setStyleSheet(actived_button)
        nb_of_points = int(self.nb_of_points.get_value())
        self.start_time_acq_button.setText(translate('acquiring... / Stop'))
        self.acquisition_started.emit(nb_of_points)
        self.save_histo_button.setStyleSheet(disabled_button)
        self.save_histo_button.setEnabled(False)
        self.save_time_chart_button.setStyleSheet(disabled_button)
        self.save_time_chart_button.setEnabled(False)
        self.reset_data_button.setStyleSheet(disabled_button)
        self.reset_data_button.setEnabled(False)

    def stop_acquisition(self):
        """Action performed when acquisition is stopped or ended."""
        self.start_time_acq_button.setStyleSheet(disabled_button)
        self.start_time_acq_button.setText(translate('Acquisition Stopped'))
        self.start_time_acq_button.setEnabled(False)
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_button.setEnabled(True)
        self.save_time_chart_button.setStyleSheet(unactived_button)
        self.save_time_chart_button.setEnabled(True)
        self.reset_data_button.setStyleSheet(unactived_button)
        self.reset_data_button.setEnabled(True)

    def handle_save_time_chart(self, event):
        self.save_time_chart_button.setStyleSheet(actived_button)
        self.save_data.emit('time')

    def handle_save_histogram(self, event):
        self.save_histo_button.setStyleSheet(actived_button)
        self.save_data.emit('histo')

    def reinit_acquisition(self):
        """Action performed when reset data is clicked."""
        self.start_time_acq_button.setText(translate('start_time_acq_button'))
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_time_chart_button.setStyleSheet(unactived_button)
        self.start_time_acq_button.setStyleSheet(unactived_button)
        self.start_time_acq_button.setEnabled(True)

    def set_exposure_time(self, exposure):
        """
        Set the exposure time in microseconds.
        :param exposure: exposure time in microseconds.
        """
        self.camera_params.exposure_time.set_value(f'{exposure}')

    def set_black_level(self, black_level):
        """
        Set the black level.
        :param black_level: black level.
        """
        self.camera_params.black_level.set_value(f'{black_level}')

    def set_frame_rate(self, frame_rate):
        """
        Set the frame rate.
        :param frame_rate: frame rate.
        """
        self.camera_params.frame_rate.set_value(f'{frame_rate}')


class CameraParamsDisplayWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        label = QLabel(translate('camera_display_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        self.layout.addWidget(make_hline())
        # Graphical objects
        self.exposure_time = LabelWidget(translate('exposure_time'), '0', units='us')
        self.black_level = LabelWidget(translate('black_level'), '0', units='ADU')
        self.frame_rate = LabelWidget(translate('frame_rate'), '0', units='Hz')
        self.layout.addWidget(self.exposure_time)
        self.layout.addWidget(self.black_level)
        self.layout.addWidget(self.frame_rate)
        self.layout.addWidget(make_hline())
        self.setLayout(self.layout)


class MultiHistoWidget(QWidget):
    """Display 4 histograms."""
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.histo1 = HistogramSimpleWidget(title="Point 1")
        self.histo2 = HistogramSimpleWidget(title="Point 2")
        self.histo3 = HistogramSimpleWidget(title="Point 3")
        self.histo4 = HistogramSimpleWidget(title="Point 4")

        self.layout.addWidget(self.histo1, 0, 0)
        self.layout.addWidget(self.histo2, 0, 1)
        self.layout.addWidget(self.histo3, 1, 0)
        self.layout.addWidget(self.histo4, 1, 1)

    def set_data(self, histo1, histo2, histo3, histo4, bits_depth=12):
        """Set data and process bins for histogram."""
        self.histo1.set_data(histo1, bits_depth)
        self.histo2.set_data(histo2, bits_depth)
        self.histo3.set_data(histo3, bits_depth)
        self.histo4.set_data(histo4, bits_depth)

    def set_background(self, color):
        """Set background color."""
        self.histo1.set_background(color)
        self.histo2.set_background(color)
        self.histo3.set_background(color)
        self.histo4.set_background(color)

