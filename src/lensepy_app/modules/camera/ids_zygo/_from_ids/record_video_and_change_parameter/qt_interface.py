# \brief   This sample showcases the usage of the ids_peak API
#          in setting camera parameters, starting/stopping the image acquisition
#          and how to record a video using the ids_peak_ipl API.
#
# \version 1.1
#
# Copyright (C) 2024 - 2026, IDS Imaging Development Systems GmbH.
#
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
#
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
#
# General permission to copy or modify is hereby granted.
import sys
import time

from typing import Optional

from camera import Camera, RecordingStatistics
from display import Display

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, Slot

import ids_peak_icv


class Interface(QtWidgets.QMainWindow):
    """
    Interface provides a graphical user interface (GUI) for
    interacting with the camera system.
    While it does not directly call the ids_peak or ids_peak_ipl APIs,
    it serves as part of the sample code infrastructure and demonstrates
    how a user-facing tool might be built around the API.

    Most of the actual API interactions can be found in camera.py, which
    contains the core usage examples of the API.
    """

    messagebox_signal = QtCore.Signal((str, str))
    start_button_signal = QtCore.Signal()

    def __init__(self, cam_module: Optional[Camera] = None):
        """
        :param cam_module: Camera object to access parameters
        """
        qt_instance = QtWidgets.QApplication(sys.argv)
        super().__init__()

        self._camera = cam_module

        self._timer = None
        self.widget = QtWidgets.QWidget(self)
        self._layout = QtWidgets.QVBoxLayout()
        self.widget.setLayout(self._layout)
        self.setCentralWidget(self.widget)
        self.display = None
        self._qt_instance = qt_instance
        self._qt_instance.aboutToQuit.connect(self._close)
        self.acquisition_thread = None

        self._button_start = None
        self._button_exit = None

        self.messagebox_signal[str, str].connect(self.message)
        self.start_button_signal.connect(self.reenable_button)

        self._frame_count = 0
        self._fps_label = None
        self._error_cont = 0
        self._gain_label = None

        self._label_infos = None
        self._label_version = None
        self._label_aboutqt = None

        self._fps_slider = None
        self._gain_slider = None

        self.recording_time = 10
        self.setMinimumSize(700, 650)

    # Common interface start

    def set_camera(self, cam_module):
        self._camera = cam_module

    def start_window(self):
        self.display = Display()
        self._layout.addWidget(self.display)
        self._create_button_bar()
        self._create_statusbar()

    def start_interface(self):
        self._fps_slider.setMaximum(int(self._camera.max_fps * 100))
        self._fps_slider.setValue(int(self._camera.max_fps * 100))
        self._gain_slider.setMaximum(int(self._camera.max_gain * 100))
        self._spinbox_fps.setMaximum(self._camera.max_fps)
        self._spinbox_fps.setValue(self._camera.max_fps)
        self._spinbox_gain.setMaximum(self._camera.max_gain)
        self._spinbox_gain.setMinimum(1.0)

        QtCore.QCoreApplication.setApplicationName("record video and change parameters")
        self.show()
        self._qt_instance.exec()

    def information(self, message: str):
        self.messagebox_signal.emit("Information", message)

    def warning(self, message: str):
        self.messagebox_signal.emit("Warning", message)

    def on_image_received(self, image: ids_peak_icv.Image):
        """
        Processes the received image for the video stream.

        :param image: takes an image for the video preview seen onscreen
        """
        image_numpy = image.to_numpy_array(copy=True).flatten()
        qt_image = QtGui.QImage(image_numpy,
                                image.width, image.height,
                                QtGui.QImage.Format.Format_RGB32)
        self.display.on_image_received(qt_image)
        self.display.update()
        if not self._button_start.isEnabled():
            now = time.time() - self._timer
            self._button_start.setText(str(now)[:3])
        else:
            self._button_start.setText("Start recording")

    def done_recording(self, stats: RecordingStatistics):
        if stats.frames_encoded != 0:
            self.messagebox_signal.emit(
                "Information",
                "Recording Done:\n"
                f"  Total Frames recorded: {stats.frames_encoded}\n"
                f"  Frames dropped by video recorder: {stats.frames_video_dropped}\n"
                f"  Frames dropped by image stream: {stats.frames_stream_dropped}\n"
                f"  Frames lost by image stream: {stats.frames_lost_stream}\n"
                f"  Frame rate: {stats.fps()}")
        self.start_button_signal.emit()

    # Common interface end

    @Slot(int)
    def _update_fps(self, val):
        self._spinbox_fps.setValue(val / 100)
        self._camera.target_fps = val / 100
        self._camera.set_remote_device_float_value("AcquisitionFrameRate", val / 100)

    @Slot(int)
    def _update_gain(self, val):
        self._spinbox_gain.setValue(val / 100)
        self._camera.target_gain = val / 100
        self._camera.set_remote_device_float_value("Gain", val / 100)

    def _create_button_bar(self):
        button_bar = QtWidgets.QWidget(self.centralWidget())
        button_bar_layout = QtWidgets.QGridLayout()

        self._button_start = QtWidgets.QPushButton("Start recording")
        self._button_start.clicked.connect(self.start)

        fps_widget = QtWidgets.QWidget(self.centralWidget())
        gain_widget = QtWidgets.QWidget(self.centralWidget())

        self._fps_label = QtWidgets.QLabel(fps_widget)
        self._fps_label.setText("<b>FPS: </b>")
        self._fps_label.setMaximumWidth(30)

        self._gain_label = QtWidgets.QLabel(gain_widget)
        self._gain_label.setMaximumWidth(30)
        self._gain_label.setText("<b>Gain: </b>")

        self._fps_slider = QtWidgets.QSlider()
        self._fps_slider.setMaximum(int(self._camera.max_fps * 100))
        self._fps_slider.setMinimum(100)
        self._fps_slider.setSingleStep(1)
        self._fps_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self._fps_slider.valueChanged.connect(self._update_fps)

        self._gain_slider = QtWidgets.QSlider()
        self._gain_slider.setMaximum(1000)
        self._gain_slider.setMinimum(100)
        self._gain_slider.setSingleStep(1)
        self._gain_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self._gain_slider.valueChanged.connect(self._update_gain)

        self._spinbox_fps = QtWidgets.QDoubleSpinBox()
        self._spinbox_gain = QtWidgets.QDoubleSpinBox()

        button_bar_layout.addWidget(self._button_start, 0, 0, 2, 4)
        button_bar_layout.addWidget(self._fps_label, 4, 0)
        button_bar_layout.addWidget(self._fps_slider, 4, 2, 1, 2)
        button_bar_layout.addWidget(self._spinbox_fps, 4, 1, 1, 1)
        button_bar_layout.addWidget(self._gain_label, 6, 0)
        button_bar_layout.addWidget(self._gain_slider, 6, 2, 1, 2)
        button_bar_layout.addWidget(self._spinbox_gain, 6, 1, 1, 1)

        button_bar.setLayout(button_bar_layout)
        self._layout.addWidget(button_bar)

        self._spinbox_fps.valueChanged.connect(self.change_slider_fps)
        self._spinbox_gain.valueChanged.connect(self.change_slider_gain)

    @Slot(float)
    def change_slider_fps(self, val):
        self._fps_slider.setValue(int(val * 100))

    def change_slider_gain(self, val):
        self._gain_slider.setValue(int(val * 100))

    def _close(self):
        self._camera.killed = True
        self.acquisition_thread.join()

    def _create_statusbar(self):
        status_bar = QtWidgets.QWidget(self.centralWidget())
        status_bar_layout = QtWidgets.QHBoxLayout()
        status_bar_layout.setContentsMargins(0, 0, 0, 0)
        status_bar_layout.addStretch()

        self._label_version = QtWidgets.QLabel(status_bar)
        self._label_version.setText("Version:")
        self._label_version.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_bar_layout.addWidget(self._label_version)

        self._label_aboutqt = QtWidgets.QLabel(status_bar)
        self._label_aboutqt.setObjectName("aboutQt")
        self._label_aboutqt.setText("<a href='#aboutQt'>About Qt</a>")
        self._label_aboutqt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._label_aboutqt.linkActivated.connect(self.on_aboutqt_link_activated)
        status_bar_layout.addWidget(self._label_aboutqt)
        status_bar.setLayout(status_bar_layout)

        self._layout.addWidget(status_bar)

    def start(self):
        self._timer = time.time()
        fps_input = float(self._fps_slider.value())
        fps_input = fps_input / 100
        gain_input = float(self._gain_slider.value())
        gain_input = gain_input / 100
        self._camera.target_fps = fps_input
        self._camera.target_gain = gain_input
        self._camera.start_recording = True
        self._button_start.setEnabled(False)

    @Slot(str)
    def on_aboutqt_link_activated(self, link: str):
        if link == "#aboutQt":
            QtWidgets.QMessageBox.aboutQt(self, "About Qt")

    @Slot()
    def reenable_button(self):
        self._button_start.setEnabled(True)

    @Slot(str, str)
    def message(self, type_: str, message: str):
        if type_ == "Warning":
            QtWidgets.QMessageBox.warning(self, "Warning", message, QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            QtWidgets.QMessageBox.information(self, "Information", message, QtWidgets.QMessageBox.StandardButton.Ok)
