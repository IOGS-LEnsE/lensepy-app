"""
@file    firmware_update.py
@author  IDS Imaging Development Systems GmbH
@date    2024-07-12

@brief   This application demonstrates how to update the firmware of devices using a .guf file

@version 1.0.0

Copyright (C) 2024 - 2026, IDS Imaging Development Systems GmbH.

The information in this document is subject to change without notice
and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
that may appear in this document.

This document, or source code, is provided solely as an example of how to utilize
IDS Imaging Development Systems GmbH software libraries in a sample application.
IDS Imaging Development Systems GmbH does not assume any responsibility
for the use or reliability of any portion of this document.

General permission to copy or modify is hereby granted.
"""
import sys
from ids_peak import ids_peak

VERSION = "1.0.0"


class FirmwareUpdateExample:
    """
    Example class demonstrating how to update firmware on connected devices
    using the ids_peak firmware update API.
    """

    def __init__(self):
        self.device_manager = ids_peak.DeviceManager.Instance()

        self.update_started_callback = None
        self.update_started_callback_handle = None
        self.update_finished_callback = None
        self.update_finished_callback_handle = None
        self.update_failed_callback = None
        self.update_failed_callback_handle = None
        self.update_step_started_callback = None
        self.update_step_started_callback_handle = None
        self.update_step_progress_callback = None
        self.update_step_progress_callback_handle = None

    def run_updates(self, guf_path):
        """
        Run the firmware update process using the given GUF (Generic Update Format) file.

        This method:
        - Refreshes the device list
        - Filters for compatible and openable devices
        - Prompts user for confirmation
        - Executes the update process
        """

        # Update the device manager.
        # When `Update` is called, it searches for all producer libraries
        # contained in the directories found in the official GenICam GenTL
        # environment variable GENICAM_GENTL{32/64}_PATH. It then opens all
        # found ProducerLibraries, their Systems, their Interfaces, and lists
        # all available DeviceDescriptors.
        self.device_manager.Update()

        if not self.device_manager.Devices():
            print("No device found. Exiting program.")
            return

        updater = ids_peak.FirmwareUpdater()
        # Get a list of devices compatible with the firmware file
        compatible_device_updates = self.find_compatible_devices(updater, guf_path)

        if not compatible_device_updates:
            print("No compatible devices found.")
            return

        print("The following devices will be updated:")
        for device, update_information in compatible_device_updates:
            print(f"\t{device.ModelName()} ({device.SerialNumber()})")

        answer = input("Continue? y/n: ")
        if answer != "y":
            print("Update aborted!")
            return

        for device, update_information in compatible_device_updates:
            observer = ids_peak.FirmwareUpdateProgressObserver()
            self.register_callbacks(device, observer)

            updater.UpdateDevice(device, update_information, observer)

    def register_callbacks(self, device, observer):
        """
        Register callback functions to receive firmware update progress for a device.
        """

        # NOTE: Copy values beforehand since device is
        #       invalidated once the update is started
        model_name = device.ModelName()
        serial_number = device.SerialNumber()

        # Callback: Called once when the update process starts for a device.
        # The `update_information` includes the `Version()` and `Description()`,
        # among other firmware details.
        def update_started(update_information, estimated_duration_ms):
            print(f"Updating {model_name} ({serial_number}) to version {update_information.Version()}")

        self.update_started_callback = observer.UpdateStartedCallback(update_started)
        self.update_started_callback_handle = observer.RegisterUpdateStartedCallback(self.update_started_callback)

        # Callback: Called once after the firmware update completes successfully.
        def update_finished():
            print(f"Finished updating {model_name} ({serial_number})")

        self.update_finished_callback = observer.UpdateFinishedCallback(update_finished)
        self.update_finished_callback_handle = observer.RegisterUpdateFinishedCallback(self.update_finished_callback)

        # Callback: Called if the firmware update fails at any point.
        # Provides an error description explaining why it failed.
        def update_failed(error_description):
            print(f"Update failed {model_name} ({serial_number}): {error_description}")

        self.update_failed_callback = observer.UpdateFailedCallback(update_failed)
        self.update_failed_callback_handle = observer.RegisterUpdateFailedCallback(self.update_failed_callback)

        # Callback: Called when an individual step in the firmware update
        # starts (e.g., reboot, or write).
        # Provides the step type, a description, and an estimated duration.
        def update_step_started(update_step, estimated_duration_ms, description):
            print(
                f"{model_name} ({serial_number}) | "
                f"{ids_peak.FirmwareUpdateStepEnumEntryToString(update_step)} | {description}")

        self.update_step_started_callback = observer.UpdateStepStartedCallback(update_step_started)
        self.update_step_started_callback_handle = observer.RegisterUpdateStepStartedCallback(
            self.update_step_started_callback)

        # NOTE: There also is a `RegisterUpdateStepFinishedCallback()` if
        # additional granularity is needed.
        # observer.RegisterUpdateStepFinishedCallback

        # Callback: Called continuously in certain intervals as the
        # current update step progresses.
        # Provides the step type and a percentage (0–100) indicating progress.
        def update_step_progress(update_step, progress_percentage):
            print(f"\r\tProgress: {progress_percentage:.2f}%", end="")
            if progress_percentage == 100:
                print()
            sys.stdout.flush()

        self.update_step_progress_callback = observer.UpdateStepProgressChangedCallback(update_step_progress)
        self.update_step_progress_callback_handle = observer.RegisterUpdateStepProgressChangedCallback(
            self.update_step_progress_callback)

    def find_compatible_devices(self, updater, guf_path):
        """
        Identify devices that are openable and compatible with the
        Generic Update Format (GUF) file.

        Devices are filtered to:
        - Ensure they are openable with control access
        - Avoid duplicates (e.g., from multiple transport layers)
        - Check if FirmwareUpdateInformation is available for the GUF file and
          device signaling that the device is compatible.
        """

        compatible_device_updates = []
        for device in self.device_manager.Devices():
            if not device.IsOpenable(ids_peak.DeviceAccessType_Control):
                print(f"Skipped device {device.ModelName()} ({device.SerialNumber()}), since it could not be opened!")
                continue

            # NOTE: Skip devices that were already added, since they can show
            #       up over multiple interfaces (transport layers, network cards, ...)
            def device_already_added(existingUpdate):
                return device.SerialNumber() == existingUpdate[0].SerialNumber()

            if any(device_already_added(u) for u in compatible_device_updates):
                continue

            # Returns all the `FirmwareUpdateInformation` compatible with the device.
            # If the list is empty, the GUF file is not compatible.
            update_information_list = updater.CollectFirmwareUpdateInformation(guf_path, device)
            if update_information_list:
                latest_update_information = update_information_list[0]
                compatible_device_updates.append((device, latest_update_information))
        return compatible_device_updates


def main():
    print("firmware_update Sample v" + VERSION)

    if len(sys.argv) != 2:
        print("Wrong number of arguments! Usage: firmware_update.py <gufPath>")
        sys.exit(-1)

    guf_path = sys.argv[1]

    try:
        # The library must be initialized before use.
        ids_peak.Library.Initialize()

        example = FirmwareUpdateExample()
        example.run_updates(guf_path)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # Each `Initialize` call must be matched with a corresponding call
        # to `Close`.
        ids_peak.Library.Close()


if __name__ == '__main__':
    main()
