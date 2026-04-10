# \brief   This sample shows how to start and stop acquisition as well as
#          how to capture images using a software trigger
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

import ids_peak_icv
from ids_peak_common import PixelFormat, Channel

from camera import Camera
from display import Display
from ids_peak import ids_peak

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, Slot


class Interface(QtWidgets.QMainWindow):
    """
    Interface provides a graphical user interface (GUI) for
    interacting with the camera system.
    While it does not directly call the ids_peak API,
    it serves as part of the sample code infrastructure and demonstrates
    how a user-facing tool might be built around the API.

    Most of the actual API interactions can be found in camera.py, which
    contains the core usage examples of the API.
    """

    messagebox_signal = QtCore.Signal((str, str))
    start_button_signal = QtCore.Signal()

    def __init__(self, cam_module: Camera | None = None):
        """
        :param cam_module: Camera object to access parameters
        """
        qt_instance = QtWidgets.QApplication(sys.argv)
        super().__init__()

        self.__camera = cam_module

        self.widget = QtWidgets.QWidget(self)
        self.__layout = QtWidgets.QVBoxLayout()
        self.widget.setLayout(self.__layout)
        self.setCentralWidget(self.widget)
        self.display = Display()
        self.__qt_instance = qt_instance
        self.__qt_instance.aboutToQuit.connect(self._close)

        self._button_software_trigger = None
        self._button_start_acquisition = None
        self._button_stop_acquisition = None
        self._checkbox_save = None
        self._button_exit = None
        self._dropdown_pixel_format = None

        self.messagebox_signal[str, str].connect(self.message)

        self._label_infos = None
        self._label_version = None
        self._label_aboutqt = None

        self.acquisition_thread = None

        self.setMinimumSize(700, 500)

    def is_gui(self):
        return True

    def set_camera(self, cam_module):
        self.__camera = cam_module

    def _create_button_bar(self):
        self._checkbox_save = QtWidgets.QCheckBox("save image to computer")
        self._checkbox_save.setChecked(False)

        self._dropdown_pixel_format = QtWidgets.QComboBox()
        formats = self.__camera.node_map.FindNode("PixelFormat").Entries()
        for idx in formats:
            if (idx.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
                    and idx.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented
                    and not PixelFormat(idx.NumericValue()).has_channel(Channel.RED)):
                self._dropdown_pixel_format.addItem(idx.SymbolicValue())
        self._dropdown_pixel_format.currentIndexChanged.connect(
            self.change_pixel_format)

        self._button_software_trigger = QtWidgets.QPushButton(
            "Software Trigger")
        self._button_software_trigger.clicked.connect(self._trigger_sw_trigger)

        self._button_start_acquisition = QtWidgets.QPushButton(
            "Start Acquisition")
        self._button_start_acquisition.clicked.connect(self._start_acquisition)
        self._button_stop_acquisition = QtWidgets.QPushButton(
            "Stop Acquisition")
        self._button_stop_acquisition.clicked.connect(self._stop_acquisition)
        self._button_stop_acquisition.setEnabled(False)
        self._button_software_trigger.setEnabled(False)

        button_bar = QtWidgets.QWidget(self.centralWidget())
        button_bar_layout = QtWidgets.QGridLayout()
        button_bar_layout.addWidget(self._button_start_acquisition, 0, 0, 1, 2)
        button_bar_layout.addWidget(self._button_stop_acquisition, 0, 2, 1, 2)
        button_bar_layout.addWidget(self._button_software_trigger, 1, 0, 1, 2)
        button_bar_layout.addWidget(self._dropdown_pixel_format, 1, 2, 1, 1)
        button_bar_layout.addWidget(self._checkbox_save, 1, 3, 1, 1)

        button_bar.setLayout(button_bar_layout)
        self.__layout.addWidget(button_bar)

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
        self._label_aboutqt.linkActivated.connect(
            self.on_aboutqt_link_activated)
        status_bar_layout.addWidget(self._label_aboutqt)
        status_bar.setLayout(status_bar_layout)

        self.__layout.addWidget(status_bar)

    def _close(self):
        self.__camera.killed = True
        self.acquisition_thread.join()

    def start_window(self):
        self.__layout.addWidget(self.display)
        self._create_button_bar()
        self._create_statusbar()

    def start_interface(self):
        QtCore.QCoreApplication.setApplicationName(
            "start and stop acquisition")
        self.show()
        self.__qt_instance.exec()

    def _trigger_sw_trigger(self):
        self.__camera.make_image = True
        if self._checkbox_save.isChecked():
            self.__camera.keep_image = True
        else:
            self.__camera.keep_image = False

    def _start_acquisition(self):
        self.__camera.start_acquisition()
        self._button_start_acquisition.setEnabled(False)
        self._dropdown_pixel_format.setEnabled(False)
        self._button_software_trigger.setEnabled(True)
        self._button_stop_acquisition.setEnabled(True)

    def _stop_acquisition(self):
        self.__camera.stop_acquisition()
        self._button_start_acquisition.setEnabled(True)
        self._dropdown_pixel_format.setEnabled(True)
        self._button_software_trigger.setEnabled(False)
        self._button_stop_acquisition.setEnabled(False)

    def change_pixel_format(self):
        pixel_format = self._dropdown_pixel_format.currentText()
        self.__camera.change_pixel_format(pixel_format)

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

    def warning(self, message: str):
        self.messagebox_signal.emit("Warning", message)

    def information(self, message: str):
        self.messagebox_signal.emit("Information", message)

    @Slot(str)
    def on_aboutqt_link_activated(self, link: str):
        if link == "#aboutQt":
            QtWidgets.QMessageBox.aboutQt(self, "About Qt")

    @Slot(str, str)
    def message(self, typ: str, message: str):
        if typ == "Warning":
            QtWidgets.QMessageBox.warning(
                self, "Warning", message, QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            QtWidgets.QMessageBox.information(
                self, "Information", message, QtWidgets.QMessageBox.StandardButton.Ok)
