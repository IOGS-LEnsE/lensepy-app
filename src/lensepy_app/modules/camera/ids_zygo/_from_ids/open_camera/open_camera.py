# \file    open_camera.py
# \author  IDS Imaging Development Systems GmbH
# \date    2021-03-25
# \since   1.2.0
#
# \brief   This application demonstrates how to use the device manager to open a camera
#
# \version 1.0.1
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

import time
from ids_peak import ids_peak

VERSION = "1.0.1"


def main():
    print("open_camera Sample v" + VERSION)

    # The library must be initialized before use.
    # Each `Initialize` call must be matched with a corresponding call
    # to `Close`.
    ids_peak.Library.Initialize()

    # Create a device manager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # Update the device manager.
        # When `Update` is called, it searches for all producer libraries
        # contained in the directories found in the official GenICam GenTL
        # environment variable GENICAM_GENTL{32/64}_PATH. It then opens all
        # found ProducerLibraries, their Systems, their Interfaces, and lists
        # all available DeviceDescriptors.
        device_manager.Update()

        # Exit program if no device was found.
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return

        # List all available devices.
        for i, device in enumerate(device_manager.Devices()):
            print(str(i) + ": " + device.ModelName() + " ("
                  + device.ParentInterface().DisplayName() + "; "
                  + device.ParentInterface().ParentSystem().DisplayName() + "v."
                  + device.ParentInterface().ParentSystem().Version() + ")")

        # Select a device to open.
        selected_device = None
        while True:
            try:
                selected_device = int(input("Select device to open: "))
                if selected_device in range(len(device_manager.Devices())):
                    break
                else:
                    print("Invalid ID.")
            except ValueError:
                print("Please enter a correct id.")
                continue

        # Open the selected device with control access.
        # The access types correspond to the GenTL `DEVICE_ACCESS_FLAGS`.
        device = device_manager.Devices()[selected_device].OpenDevice(ids_peak.DeviceAccessType_Control)

        # Retrieve the remote device's primary node map, which in GenICam represents
        # a hierarchical set of device parameters (features) such as exposure, gain,
        # and firmware info. The remote nodemap provides access to controls implemented
        # on the device itself, primarily following the GenICam Standard Feature Naming Convention (SFNC),
        # while also supporting custom nodes to accommodate device-specific features.
        nodemap_remote_device = device.RemoteDevice().NodeMaps()[0]

        # Print model name and user ID
        print("Model Name: " + nodemap_remote_device.FindNode("DeviceModelName").Value())
        try:
            print("User ID: " + nodemap_remote_device.FindNode("DeviceUserID").Value())
        except ids_peak.Exception:
            print("User ID: (unknown)")

        # Print sensor information, not knowing if device has the node "SensorName"
        try:
            print("Sensor Name: " + nodemap_remote_device.FindNode("SensorName").Value())
        except ids_peak.Exception:
            print("Sensor Name: " + "(unknown)")

        # Print resolution
        try:
            print("Max. resolution (w x h): "
                  + str(nodemap_remote_device.FindNode("WidthMax").Value()) + " x "
                  + str(nodemap_remote_device.FindNode("HeightMax").Value()))
        except ids_peak.Exception:
            print("Max. resolution (w x h): (unknown)")

    except Exception as e:
        print("Exception: " + str(e) + "")

    finally:
        input("Press Enter to continue...")

        ## Open Device
        datastreams = device.DataStreams()
        if datastreams.empty():
            print("Error - Device has no DataStream!")
            datastream = None
        else:
            datastream = datastreams[0].OpenDataStream()

        try:
            nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
            nodemap_remote_device.FindNode("UserSetLoad").Execute()
            nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
        except ids_peak.Exception:
            print('No Remote')
            # Userset is not available
            pass

        # Get the payload size for correct buffer allocation
        payload_size = nodemap_remote_device.FindNode("PayloadSize").Value()

        # Get minimum number of buffers that must be announced
        buffer_count_max = datastream.NumBuffersAnnouncedMinRequired()

        # Allocate and announce image buffers and queue them
        for i in range(buffer_count_max):
            # Let the TL allocate the buffers.
            buffer = datastream.AllocAndAnnounceBuffer(payload_size)
            # Put the buffer in the pool.
            datastream.QueueBuffer(buffer)

        ## Start Aquisition and display !!


        ## Close device
        if datastream is not None:
            try:
                for buffer in datastream.AnnouncedBuffers():
                    datastream.RevokeBuffer(buffer)
            except Exception as e:
                print(f"Exception : {e}")

        # One call to `Close` is required for each call to `Initialize`.
        ids_peak.Library.Close()


if __name__ == '__main__':
    main()
