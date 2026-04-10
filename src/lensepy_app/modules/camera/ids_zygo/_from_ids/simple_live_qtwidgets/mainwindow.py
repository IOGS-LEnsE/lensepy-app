# \version 1.5
#
# Copyright (C) 2021 - 2026, IDS Imaging Development Systems GmbH.
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

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QMainWindow, QMessageBox, QWidget
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt, Timer
from ids_peak_icv.pipeline import DefaultPipeline

from ids_peak import ids_peak
from ids_peak_common import PixelFormat

from display import Display

VERSION = "1.4.0"
FPS_LIMIT = 30
TARGET_PIXEL_FORMAT = PixelFormat.BGRA_8


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.widget = QWidget(self)
        self.__layout = QVBoxLayout()
        self.widget.setLayout(self.__layout)
        self.setCentralWidget(self.widget)

        self.__device = None
        self.__nodemap_remote_device = None
        self.__datastream = None

        self.__display = None
        self.__acquisition_timer = QTimer()
        self.__frame_counter = 0
        self.__error_counter = 0
        self.__acquisition_running = False

        self.__label_infos = None
        self.__label_version = None
        self.__label_aboutqt = None

        # The library must be initialized before use.
        # Each `Initialize` call must be matched with a corresponding call
        # to `Close`.
        ids_peak.Library.Initialize()

        # Create an instance of the default pixel pipeline which defines a sequence of processing steps
        # that are applied to an acquired image. The image is then processed into an image of the specified
        # output pixel format.
        self._image_pipeline = DefaultPipeline()
        self._image_pipeline.output_pixel_format = TARGET_PIXEL_FORMAT

        if self.__open_device():
            try:
                # Create a display for the camera image
                self.__display = Display()
                self.__layout.addWidget(self.__display)
                if not self.__start_acquisition():
                    QMessageBox.critical(self, "Error", "Unable to start acquisition!", QMessageBox.StandardButton.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Exception", str(e), QMessageBox.StandardButton.Ok)

        else:
            self.__destroy_all()
            sys.exit(0)

        self.__create_statusbar()

        self.setMinimumSize(700, 500)
        
    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        # Stop acquisition
        self.__stop_acquisition()

        # Close device and peak library
        self.__close_device()
        # Each `Initialize` call must be matched with a corresponding call
        # to `Close`.
        ids_peak.Library.Close()

    def __open_device(self):
        try:
            # Get the instance of the device manager singleton.
            device_manager = ids_peak.DeviceManager.Instance()

            # Update the device manager.
            # When `Update` is called, it searches for all producer libraries
            # contained in the directories found in the official GenICam GenTL
            # environment variable GENICAM_GENTL{32/64}_PATH. It then opens all
            # found ProducerLibraries, their Systems, their Interfaces, and lists
            # all available DeviceDescriptors.
            device_manager.Update()

            # Return if no device was found.
            if device_manager.Devices().empty():
                QMessageBox.critical(self, "Error", "No device found!", QMessageBox.StandardButton.Ok)
                return False

            # Open the first openable device in the managers device list.
            for device in device_manager.Devices():
                if device.IsOpenable():
                    self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
                    break

            # Return if no device could be opened.
            if self.__device is None:
                QMessageBox.critical(self, "Error", "Device could not be opened!", QMessageBox.StandardButton.Ok)
                return False

            # Open standard data stream
            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.StandardButton.Ok)
                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()

            # Retrieve the remote device's primary node map, which in GenICam represents
            # a hierarchical set of device parameters (features) such as exposure, gain,
            # and firmware info. The remote nodemap provides access to controls implemented
            # on the device itself, primarily following the GenICam Standard Feature Naming Convention (SFNC),
            # while also supporting custom nodes to accommodate device-specific features.
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            # To prepare for untriggered continuous image acquisition, load the default user set if available and
            # wait until execution is finished
            try:
                self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
                self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
                self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            except ids_peak.Exception:
                # Userset is not available
                pass

            # Get the payload size for correct buffer allocation
            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()

            # Get minimum number of buffers that must be announced
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            # Allocate and announce image buffers and queue them
            for i in range(buffer_count_max):
                # Let the TL allocate the buffers.
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                # Put the buffer in the pool.
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception as e:
            QMessageBox.critical(self, "Exception", str(e), QMessageBox.StandardButton.Ok)

        return False

    def __close_device(self):
        """
        Stop acquisition if still running and close datastream and nodemap of the device
        """
        # Stop Acquisition in case it is still running
        self.__stop_acquisition()

        # If a datastream has been opened, try to revoke its image buffers
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception as e:
                QMessageBox.information(self, "Exception", str(e), QMessageBox.StandardButton.Ok)

    def __start_acquisition(self):
        """
        Start Acquisition on camera and start the acquisition timer to receive and display images

        :return: True/False if acquisition start was successful
        """
        # Check that a device is opened and that the acquisition is NOT running. If not, return.
        if self.__device is None:
            return False
        if self.__acquisition_running:
            return True

        # Get the maximum frame rate possible, limit it to the configured
        # FPS_LIMIT. If the limit can't be reached, set
        # acquisition interval to the maximum possible frame rate.
        target_fps = 30
        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            # `AcquisitionFrameRate` is not available. Unable to limit fps.
            # Print warning and continue.
            QMessageBox.warning(self, "Warning",
                                "Unable to limit fps, since the AcquisitionFrameRate Node is"
                                " not supported by the connected camera. Program will continue without limit.")
            return False

        # Setup acquisition timer according to the configured target frame rate.
        self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        self.__acquisition_timer.setSingleShot(False)
        self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            # Lock writable nodes, which could influence the payload size or
            # similar information during acquisition.
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition both locally and on device.
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception as e:
            print("Exception: " + str(e))
            return False

        # Start the acquisition timer, which will call our `on_acquisition_timer`
        # at a rate corresponding to the target frame rate.
        self.__acquisition_timer.start()
        self.__acquisition_running = True

        return True

    def __stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        :return:
        """
        # Check that a device is opened and that the acquisition is running. If not, return.
        if self.__device is None or self.__acquisition_running is False:
            return

        # Otherwise try to stop acquisition
        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush the `DataStream`.
            # `KillWait` will cancel pending `WaitForFinishedBuffer` calls.
            # NOTE: One call to `KillWait` will cancel one pending `WaitForFinishedBuffer`.
            #       For more information, refer to the documentation of `KillWait`.
            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            # Discard all buffers from the acquisition engine.
            # They remain in the announced buffer pool.
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self.__acquisition_running = False

            # Unlock parameters after acquisition stop
            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    QMessageBox.information(self, "Exception", str(e), QMessageBox.StandardButton.Ok)

        except Exception as e:
            QMessageBox.information(self, "Exception", str(e), QMessageBox.StandardButton.Ok)

    def __create_statusbar(self):
        status_bar = QWidget(self.centralWidget())
        status_bar_layout = QHBoxLayout()
        status_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.__label_infos = QLabel(status_bar)
        self.__label_infos.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_bar_layout.addWidget(self.__label_infos)
        status_bar_layout.addStretch()

        self.__label_version = QLabel(status_bar)
        self.__label_version.setText("simple_live_qtwidgets v" + VERSION)
        self.__label_version.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_bar_layout.addWidget(self.__label_version)

        self.__label_aboutqt = QLabel(status_bar)
        self.__label_aboutqt.setObjectName("aboutQt")
        self.__label_aboutqt.setText("<a href='#aboutQt'>About Qt</a>")
        self.__label_aboutqt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__label_aboutqt.linkActivated.connect(self.on_aboutqt_link_activated)
        status_bar_layout.addWidget(self.__label_aboutqt)
        status_bar.setLayout(status_bar_layout)

        self.__layout.addWidget(status_bar)

    def update_counters(self):
        """
        This function gets called when the frame and error counters have changed
        :return:
        """
        self.__label_infos.setText("Acquired: " + str(self.__frame_counter) + ", Errors: " + str(self.__error_counter))

    def on_acquisition_timer(self):
        """
        This function gets called on every timeout of the acquisition timer
        """
        try:
            # Get buffer from device's datastream
            buffer = self.__datastream.WaitForFinishedBuffer(5000)

            # Convert the acquired buffer to an image view.
            # The ImageView defines a standard way to access image properties and raw pixel data,
            # enabling interoperability with different image processing libraries or backends.
            # Note: This object does not own the image memory.
            image_view = buffer.ToImageView()

            # Pass the ImageView through the image pipeline which runs all processing steps
            # in sequence. The resulting image is guaranteed to be a copy.
            converted_image = self._image_pipeline.process(image_view)

            # Queue buffer so that it can be used again.
            self.__datastream.QueueBuffer(buffer)

            # Get raw image data from converted image and construct a QImage from it.
            data = converted_image.to_numpy_array()
            image = QImage(data, converted_image.width, converted_image.height, QImage.Format.Format_RGB32)

            # Make an explicit copy of the QImage to ensure the underlying
            # image data is owned by Qt.
            # Without this, the QImage may reference memory managed by the
            # image library, which could be released or overwritten later.
            image_cpy = image.copy()

            # Emit signal that the image is ready to be displayed
            self.__display.on_image_received(image_cpy)
            self.__display.update()

            # Increase frame counter
            self.__frame_counter += 1
        except ids_peak.Exception as e:
            self.__error_counter += 1
            print("Exception: " + str(e))

        # Update counters
        self.update_counters()

    @Slot(str)
    def on_aboutqt_link_activated(self, link):
        if link == "#aboutQt":
            QMessageBox.aboutQt(self, "About Qt")
