# \brief   This sample shows how to start and stop acquisition as well as
#          how to capture images using a software trigger
#
# \version 1.0
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

from ids_peak import ids_peak

import threading
import camera


def start(camera_device, ui):
    ui.start_window()
    thread = threading.Thread(target=camera_device.wait_for_signal, args=())
    thread.start()
    ui.acquisition_thread = thread
    ui.start_interface()


def main(interface):
    # Initialize library and device manager
    ids_peak.Library.Initialize()
    device_manager = ids_peak.DeviceManager.Instance()
    camera_device = None
    try:
        # Initialize camera device class
        camera_device = camera.Camera(device_manager, interface)
        # Initialize software trigger and acquisition
        camera_device.init_software_trigger()
        start(camera_device, interface)

    except KeyboardInterrupt:
        print("User interrupt: Exiting...")
    except Exception as e:
        print(f"Exception (main): {str(e)}")

    finally:
        # Close camera and library after program ends
        if camera_device is not None:
            camera_device.close()
        ids_peak.Library.Close()


if __name__ == '__main__':
    from cli_interface import Interface
    main(Interface())
