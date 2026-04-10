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
import os
from os.path import exists

from ids_peak_common import PixelFormat
from ids_peak_icv.pipeline import DefaultPipeline
from ids_peak import ids_peak


TARGET_PIXEL_FORMAT = PixelFormat.BGRA_8


class Camera:

    def __init__(self, device_manager, interface):
        if interface is None:
            raise ValueError("Interface is None")

        self.ipl_image = None
        self.device_manager = device_manager

        self._device = None
        self._datastream = None
        self.acquisition_running = False
        self.node_map = None
        self._interface = interface
        self.make_image = False
        self.keep_image = True
        self._buffer_list = []

        self.killed = False

        self._get_device()
        self._interface.set_camera(self)

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
            sys.exit(1)
        selected_device = None

        # Initialize first device found if only one is available
        if len(self.device_manager.Devices()) == 1:
            selected_device = 0
        else:
            # List all available devices
            for i, device in enumerate(self.device_manager.Devices()):
                # Display device information
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
        self.node_map = self._device.RemoteDevice().NodeMaps()[0]

        # Load the default settings
        self.node_map.FindNode("UserSetSelector").SetCurrentEntry("Default")
        self.node_map.FindNode("UserSetLoad").Execute()
        self.node_map.FindNode("UserSetLoad").WaitUntilDone()

        print("Finished opening device!")

    def _init_data_stream(self):
        # Open device's datastream
        self._datastream = self._device.DataStreams()[0].OpenDataStream()
        # Allocate image buffer for image acquisition
        self.revoke_and_allocate_buffer()

    def init_software_trigger(self):
        # In GenICam, enumeration nodes can contain multiple possible entries
        # (enum values), but not all entries are guaranteed to be available or
        # implemented on every device or in every state. According to the
        # standard, only entries with a valid access status (i.e., not
        # 'NotAvailable' or 'NotImplemented') can be selected.
        # This ensures that only legal, supported values are used
        # when configuring the device.
        allEntries = self.node_map.FindNode("TriggerSelector").Entries()
        availableEntries = []
        for entry in allEntries:
            if (entry.AccessStatus() != ids_peak.NodeAccessStatus_NotAvailable
                    and entry.AccessStatus() != ids_peak.NodeAccessStatus_NotImplemented):
                availableEntries.append(entry.SymbolicValue())

        if len(availableEntries) == 0:
            raise Exception("Software Trigger not supported")
        elif "ExposureStart" not in availableEntries:
            self.node_map.FindNode("TriggerSelector").SetCurrentEntry(
                availableEntries[0])
        else:
            self.node_map.FindNode(
                "TriggerSelector").SetCurrentEntry("ExposureStart")
        self.node_map.FindNode("TriggerMode").SetCurrentEntry("On")
        self.node_map.FindNode("TriggerSource").SetCurrentEntry("Software")

    def close(self):
        self.stop_acquisition()

        # If datastream has been opened, revoke and deallocate all buffers
        if self._datastream is not None:
            try:
                for buffer in self._datastream.AnnouncedBuffers():
                    self._datastream.RevokeBuffer(buffer)
            except Exception as e:
                print(f"Exception (close): {str(e)}")

    def start_acquisition(self):
        if self._device is None:
            return False
        if self.acquisition_running is True:
            return True

        if self._datastream is None:
            self._init_data_stream()

        for buffer in self._buffer_list:
            self._datastream.QueueBuffer(buffer)
        try:
            # Lock writable nodes, which could influence the payload size or
            # similar information during acquisition.
            self.node_map.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition both locally and on device.
            self._datastream.StartAcquisition()
            self.node_map.FindNode("AcquisitionStart").Execute()
            self.node_map.FindNode("AcquisitionStart").WaitUntilDone()
            self.acquisition_running = True

            print("Acquisition started!")
        except Exception as e:
            print(f"Exception (start acquisition): {str(e)}")
            return False
        return True

    def stop_acquisition(self):
        if self._device is None:
            return
        if self.acquisition_running is False:
            return
        try:
            self.node_map.FindNode("AcquisitionStop").Execute()

            # Stop and flush the `DataStream`.
            # `KillWait` will cancel pending `WaitForFinishedBuffer` calls.
            # NOTE: One call to `KillWait` will cancel one pending `WaitForFinishedBuffer`.
            #       For more information, refer to the documentation of `KillWait`.
            self._datastream.StopAcquisition(
                ids_peak.AcquisitionStopMode_Default)
            # Discard all buffers from the acquisition engine.
            # They remain in the announced buffer pool.
            self._datastream.Flush(
                ids_peak.DataStreamFlushMode_DiscardAll)

            self.acquisition_running = False

            # Unlock parameters
            self.node_map.FindNode("TLParamsLocked").SetValue(0)
        except Exception as e:
            self._interface.warning(f"Cannot stop acquisition: {str(e)}")

    def software_trigger(self):
        print("Executing software trigger...")
        self.node_map.FindNode("TriggerSoftware").Execute()
        self.node_map.FindNode("TriggerSoftware").WaitUntilDone()
        print("Finished.")

    def _valid_name(self, path: str, ext: str):
        num = 0

        def build_string():
            return f"{path}_{num}{ext}"

        while exists(build_string()):
            num += 1
        return build_string()

    def revoke_and_allocate_buffer(self):
        if self._datastream is None:
            return

        try:
            # Check if buffers are already allocated
            if self._datastream is not None:
                # Remove buffers from the announced pool
                for buffer in self._datastream.AnnouncedBuffers():
                    self._datastream.RevokeBuffer(buffer)
                self._buffer_list = []

            payload_size = self.node_map.FindNode("PayloadSize").Value()
            buffer_amount = self._datastream.NumBuffersAnnouncedMinRequired()

            for _ in range(buffer_amount):
                buffer = self._datastream.AllocAndAnnounceBuffer(payload_size)
                self._buffer_list.append(buffer)

            print("Allocated buffers!")
        except Exception as e:
            self._interface.warning(f"Cannot allocate buffer: {str(e)}")

    def change_pixel_format(self, pixel_format: str):
        try:
            self.node_map.FindNode("PixelFormat").SetCurrentEntry(pixel_format)
            # The `PayloadSize` might have changed, so reallocate the buffers.
            self.revoke_and_allocate_buffer()
        except Exception as e:
            self._interface.warning(f"Cannot change pixelformat: {str(e)}")

    def save_image(self):
        cwd = os.getcwd()

        # Wait until the next buffer is received.
        buffer = self._datastream.WaitForFinishedBuffer(1000)
        print("Buffered image!")

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

        self._interface.on_image_received(converted_image)

        if self.keep_image:
            print("Saving image...")
            image_path = self._valid_name(cwd + "/image", ".png")
            converted_image.save(image_path)
            print(f"Saved to {image_path}")

    def wait_for_signal(self):
        while not self.killed:
            try:
                if self.make_image:
                    # Call software trigger to load image
                    self.software_trigger()
                    # Get image and save it as file, if that option is enabled
                    self.save_image()
                    self.make_image = False
            except Exception as e:
                self._interface.warning(str(e))
                self.make_image = False
