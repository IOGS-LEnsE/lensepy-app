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

import os

import time

from os.path import exists
from dataclasses import dataclass

from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak_icv.pipeline import DefaultPipeline
from ids_peak_common import PixelFormat

TARGET_PIXEL_FORMAT = PixelFormat.BGRA_8


@dataclass
class RecordingStatistics:
    frames_encoded: int
    frames_stream_dropped: int
    frames_video_dropped: int
    frames_lost_stream: int
    duration: int

    def fps(self):
        return self.frames_encoded / self.duration


class Camera:
    """
    This class showcases the usage of the ids_peak API in
    setting camera parameters, starting/stopping acquisition and
    how to record a video using the ids_peak_ipl API.
    """
    def __init__(self, device_manager, interface):
        self.device_manager = device_manager

        self._device = None
        self._datastream = None
        self._acquisition_running = False
        self._interface = interface
        self.target_fps = 20000
        self.max_fps = 0
        self.target_gain = 1
        self.max_gain = 1
        self._node_map = None

        self.killed = False

        self._interface.set_camera(self)

        self.start_recording = False

        self._get_device()
        if not self._device:
            print("Error: Device not found")
        self._setup_device_and_datastream()

        # Create an instance of the default pixel pipeline which defines a sequence of processing steps
        # that are applied to an acquired image. The image is then processed into an image of the specified
        # output pixel format.
        self._image_pipeline = DefaultPipeline()
        self._image_pipeline.output_pixel_format = TARGET_PIXEL_FORMAT

    def __del__(self):
        self.close()

    def _get_device(self):
        # Update the device manager.
        # When `Update` is called, it searches for all producer libraries
        # contained in the directories found in the official GenICam GenTL
        # environment variable GENICAM_GENTL{32/64}_PATH. It then opens all
        # found ProducerLibraries, their Systems, their Interfaces, and lists
        # all available DeviceDescriptors.
        self.device_manager.Update()
        if self.device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return
        selected_device = None

        # Initialize first device found if only one is available
        if len(self.device_manager.Devices()) == 1:
            selected_device = 0
        else:
            # List all available devices
            for i, device in enumerate(self.device_manager.Devices()):
                print(
                    f"{str(i)}:  {device.ModelName()} ("
                    f"{device.ParentInterface().DisplayName()} ; "
                    f"{device.ParentInterface().ParentSystem().DisplayName()} v." 
                    f"{device.ParentInterface().ParentSystem().Version()})")
            while True:
                try:
                    # Let the user decide which device to open
                    selected_device = int(input("Select device to open: "))
                    if selected_device < len(self.device_manager.Devices()):
                        break
                    else:
                        print("Invalid ID.")
                except ValueError:
                    print("Please enter a correct id.")
                    continue

        # Open the selected device with control access.
        # The access types correspond to the GenTL `DEVICE_ACCESS_FLAGS`.
        self._device = self.device_manager.Devices()[selected_device].OpenDevice(
            ids_peak.DeviceAccessType_Control)
        # Retrieve the remote device's primary node map, which in GenICam represents
        # a hierarchical set of device parameters (features) such as exposure, gain,
        # and firmware info. The remote nodemap provides access to controls implemented
        # on the device itself, primarily following the
        # GenICam Standard Feature Naming Convention (SFNC),
        # while also supporting custom nodes to accommodate device-specific features.
        self._node_map = self._device.RemoteDevice().NodeMaps()[0]

        # Load the default settings
        self._node_map.FindNode("UserSetSelector").SetCurrentEntry("Default")
        self._node_map.FindNode("UserSetLoad").Execute()
        self._node_map.FindNode("UserSetLoad").WaitUntilDone()

        self.max_gain = self._node_map.FindNode("Gain").Maximum()


    def _setup_device_and_datastream(self):
        self._datastream = self._device.DataStreams()[0].OpenDataStream()
        # Disable auto gain and auto exposure to facilitate setting a
        # custom gain from the UI.
        self._find_and_set_remote_device_enumeration("GainAuto", "Off")
        self._find_and_set_remote_device_enumeration("ExposureAuto", "Off")

        # Allocate image buffer for image acquisition
        payload_size = self._node_map.FindNode("PayloadSize").Value()
        # Use more buffers to avoid running out of buffers while recording
        # the video.
        max_buffer = self._datastream.NumBuffersAnnouncedMinRequired() * 5
        for idx in range(max_buffer):
            buffer = self._datastream.AllocAndAnnounceBuffer(payload_size)
            self._datastream.QueueBuffer(buffer)
        print("Allocated buffers, finished opening device")

    def close(self):
        self.stop_acquisition()

        # If the datastream has been opened, revoke and deallocate all buffers
        if self._datastream is not None:
            try:
                for buffer in self._datastream.AnnouncedBuffers():
                    self._datastream.RevokeBuffer(buffer)
            except Exception as e:
                print(f"Exception (close): {str(e)}")

    def _find_and_set_remote_device_enumeration(self, name: str, value: str):
        # In GenICam, enumeration nodes can contain multiple possible entries
        # (enum values), but not all entries are guaranteed to be available or
        # implemented on every device or in every state. According to the
        # standard, only entries with a valid access status (i.e., not
        # 'NotAvailable' or 'NotImplemented') can be selected.
        # This ensures that only legal, supported values are used
        # when configuring the device.
        all_entries = self._node_map.FindNode(name).Entries()
        available_entries = []
        for entry in all_entries:
            if (entry.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
                    and entry.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented):
                available_entries.append(entry.SymbolicValue())
        if value in available_entries:
            self._node_map.FindNode(name).SetCurrentEntry(value)

    def set_remote_device_float_value(self, name: str, value: float):
        try:
            self._node_map.FindNode(name).SetValue(value)
        except ids_peak.Exception:
            self._interface.warning(f"Could not set value for {name}!")

    def print(self):
        print(
            f"{self._device.ModelName()}: ("
            f"{self._device.ParentInterface().DisplayName()} ; "
            f"{self._device.ParentInterface().ParentSystem().DisplayName()} v."
            f"{self._device.ParentInterface().ParentSystem().Version()})")

    def get_data_stream_image(self):
        # Wait until the next buffer is received.
        buffer = self._datastream.WaitForFinishedBuffer(500)

        # Convert the acquired buffer to an image view.
        # The ImageView defines a standard way to access image properties and raw pixel data,
        # enabling interoperability with different image processing libraries or backends.
        # Note: This object does not own the image memory.
        image_view = buffer.ToImageView()

        # Pass the ImageView through the image pipeline which runs all processing steps
        # in sequence. The resulting image is guaranteed to be a copy.
        converted_image = self._image_pipeline.process(image_view)

        # Queue buffer so that it can be used again.
        self._datastream.QueueBuffer(buffer)

        return converted_image

    def start_acquisition(self):
        if self._device is None:
            return False
        if self._acquisition_running is True:
            return True

        self.target_fps = 0
        try:
            # Get cameras maximums possible FPS
            self.max_fps = self._node_map.FindNode("AcquisitionFrameRate").Maximum()
            # Set frames per second to given maximum
            self.target_fps = self.max_fps
            self.set_remote_device_float_value("AcquisitionFrameRate", self.target_fps)
        except ids_peak.Exception:
            self._interface.warning(
                "Warning Unable to limit fps, "
                "since node AcquisitionFrameRate is not supported."
                "Program will continue without set limit.")

        try:
            # Lock writable nodes, which could influence the payload size or
            # similar information during acquisition.
            self._node_map.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition both locally and on device.
            self._datastream.StartAcquisition()
            self._node_map.FindNode("AcquisitionStart").Execute()
            self._node_map.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception as e:
            print(f"Exception (start acquisition): {str(e)}")
            return False
        self._acquisition_running = True
        return True

    def stop_acquisition(self):
        if self._device is None or self._acquisition_running is False:
            return
        try:
            self._node_map.FindNode("AcquisitionStop").Execute()

            # Stop and flush the `DataStream`.
            # `KillWait` will cancel pending `WaitForFinishedBuffer` calls.
            # NOTE: One call to `KillWait` will cancel one pending `WaitForFinishedBuffer`.
            #       For more information, refer to the documentation of `KillWait`.
            self._datastream.KillWait()
            self._datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            # Discard all buffers from the acquisition engine.
            # They remain in the announced buffer pool.
            self._datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self._acquisition_running = False

            # Unlock parameters
            self._node_map.FindNode("TLParamsLocked").SetValue(0)

        except Exception as e:
            print(f"Exception (stop acquisition): {str(e)}")

    def _valid_name(self, path: str, ext: str):
        num = 0

        def build_string():
            return f"{path}_{num}{ext}"

        while exists(build_string()):
            num += 1
        return build_string()

    def record(self, timer: int):
        """
        Records image frames into an AVI-container and saves it to {CWD}/video.avi
        :param timer: video length in seconds
        """

        # Create video writing object
        video = ids_peak_ipl.VideoWriter()
        cwd = os.getcwd()

        dropped_before = 0
        lost_before = 0

        try:
            # Create a new file the video will be saved in.
            video.Open(self._valid_name(cwd + "/" + "video", ".avi"))

            # Set target frame rate and gain
            self.set_remote_device_float_value("AcquisitionFrameRate", self.target_fps)
            self.set_remote_device_float_value("Gain", self.target_gain)

            video.Container().SetFramerate(self.target_fps)

            print("Recording with: ")
            var_name = "AcquisitionFrameRate"
            print(f"  Framerate: {self._node_map.FindNode(var_name).Value():.2f}")
            var_name = "Gain"
            print(f"  Gain: {self._node_map.FindNode(var_name).Value():.2f}")
            data_stream_node_map = self._datastream.NodeMaps()[0]
            dropped_before = data_stream_node_map.FindNode("StreamDroppedFrameCount").Value()
            lost_before = data_stream_node_map.FindNode("StreamLostFrameCount").Value()

        except Exception as e:
            self._interface.warning(str(e))
            raise

        print("Recording...")
        # Set target time
        limit = timer + time.time()
        while (limit - time.time()) > 0 and not self.killed:
            try:
                # Receive image from datastream
                # Wait until the image is completed
                buffer = self._datastream.WaitForFinishedBuffer(500)

                # Convert the acquired buffer to an image view.
                # The ImageView defines a standard way to access image properties and raw pixel data,
                # enabling interoperability with different image processing libraries or backends.
                # Note: This object does not own the image memory.
                image_view = buffer.ToImageView()

                # Pass the ImageView through the image pipeline which runs all processing steps
                # in sequence. The resulting image is guaranteed to be a copy.
                converted_image = self._image_pipeline.process(image_view)

                # Passes the image to the user interface
                self._interface.on_image_received(converted_image)

                # Append image to video
                data = converted_image.to_numpy_array().flatten()
                video.Append(ids_peak_ipl.Image.CreateFromSizeAndPythonBuffer(converted_image.pixel_format.value,
                                                                                data,
                                                                                converted_image.width,
                                                                                converted_image.height))
                # Give buffer back into the queue so it can be used again
                self._datastream.QueueBuffer(buffer)

            except Exception as e:
                print(f"Warning: Exception caught: {str(e)}")

        if self.killed:
            return

        # See if the acquisition was lossless. Note that between the last
        # acquisition and the next acquisition some frames will be lost
        # (seen after the second recording).
        data_stream_node_map = self._datastream.NodeMaps()[0]
        dropped_stream_frames = data_stream_node_map.FindNode(
            "StreamDroppedFrameCount").Value() - dropped_before
        lost_stream_frames = data_stream_node_map.FindNode(
            "StreamLostFrameCount").Value() - lost_before

        stats = RecordingStatistics(
            frames_encoded=video.NumFramesEncoded(),
            frames_video_dropped=video.NumFramesDropped(),
            frames_stream_dropped=dropped_stream_frames,
            frames_lost_stream=lost_stream_frames,
            duration=timer)

        # AVI framerate sets the playback speed.
        # You can calculate that with the amount of frames captured in the
        # time duration the video was recorded
        video.Container().SetFramerate(stats.fps())
        # Wait until all frames are written to the file
        video.WaitUntilFrameDone(10000)
        video.Close()
        self._interface.done_recording(stats)

    def acquisition_thread(self):
        while not self.killed:
            try:
                if self.start_recording:
                    # Start recording a 10 seconds long video
                    self.record(10)
                    self.start_recording = False
                else:
                    # Forward image to interface
                    image = self.get_data_stream_image()
                    self._interface.on_image_received(image)
            except Exception as e:
                self._interface.warning(str(e))
                self.start_recording = False
                self._interface.done_recording(RecordingStatistics(0, 0, 0, 0, 0))
