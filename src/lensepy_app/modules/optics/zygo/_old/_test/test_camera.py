from ids_peak import ids_peak
from ids_peak import ids_peak_ipl_extension
from ids_peak_ipl import *
from matplotlib import pyplot as plt

images = []

def main():
    # Initialize library
    ids_peak.Library.Initialize()

    # Create a DeviceManager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # The returned callback object needs to be stored in a variable and
        # needs to live as long as the class that would call it,
        # so as long as the device manager in this case
        # If the callback gets garbage collected it deregisters itself
        device_found_callback = device_manager.DeviceFoundCallback(
            lambda found_device: print(
                "Found-Device-Callback: Key={}".format(
                    found_device.Key()), end="\n\n"))
        device_found_callback_handle = device_manager.RegisterDeviceFoundCallback(
            device_found_callback)

        # Update the DeviceManager
        device_manager.Update()
        # The callback can also be unregistered explicitly using the returned
        # handle
        device_manager.UnregisterDeviceFoundCallback(
            device_found_callback_handle)

        # Exit program if no device was found
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return -1

        # Open the first device
        device = device_manager.Devices()[0].OpenDevice(
            ids_peak.DeviceAccessType_Control)

        # Nodemap for accessing GenICam nodes
        remote_nodemap = device.RemoteDevice().NodeMaps()[0]

        remote_nodemap.FindNode("ExposureTime").SetValue(1000)
        remote_nodemap.FindNode("AcquisitionFrameRate").SetValue(40)

        # Load default camera settings
        remote_nodemap.FindNode("UserSetSelector").SetCurrentEntry("Default")
        remote_nodemap.FindNode("UserSetLoad").Execute()
        remote_nodemap.FindNode("UserSetLoad").WaitUntilDone()

        # Open first data stream
        data_stream = device.DataStreams()[0].OpenDataStream()
        # Buffer size
        payload_size = remote_nodemap.FindNode("PayloadSize").Value()

        # Minimum number of required buffers
        buffer_count_max = data_stream.NumBuffersAnnouncedMinRequired()

        # Allocate buffers and add them to the pool
        for buffer_count in range(buffer_count_max):
            # Let the TL allocate the buffers
            buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
            # Put the buffer in the pool
            data_stream.QueueBuffer(buffer)

        # Lock writeable nodes during acquisition
        remote_nodemap.FindNode("TLParamsLocked").SetValue(1)

        print("Starting acquisition...")
        data_stream.StartAcquisition()
        remote_nodemap.FindNode("AcquisitionStart").Execute()
        remote_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

        print("Getting 100 images...")
        # Process 100 images
        for _ in range(10):
            try:
                # Wait for finished/filled buffer event
                buffer = data_stream.WaitForFinishedBuffer(1000)
                img = ids_peak_ipl_extension.BufferToImage(buffer)
                image = img.ConvertTo(ids_peak_ipl.PixelFormatName_RGBa8,
                                      ids_peak_ipl.ConversionMode_Fast)
                images.append(image)

                # Do something with `img` here ...

                # Put the buffer back in the pool, so it can be filled again
                # NOTE: If you want to use `img` beyond this point, you have
                #       to make a copy, since `img` still uses the underlying
                #       buffer's memory.
                data_stream.QueueBuffer(buffer)
            except Exception as e:
                print(f"Exception: {e}")

        print("Stopping acquisition...")
        remote_nodemap.FindNode("AcquisitionStop").Execute()
        remote_nodemap.FindNode("AcquisitionStop").WaitUntilDone()

        data_stream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)

        # In case another thread is waiting on WaitForFinishedBuffer
        # you can interrupt it using:
        # data_stream.KillWait()

        # Remove buffers from any associated queue
        data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

        for buffer in data_stream.AnnouncedBuffers():
            # Remove buffer from the transport layer
            data_stream.RevokeBuffer(buffer)

        # Unlock writeable nodes again
        remote_nodemap.FindNode("TLParamsLocked").SetValue(0)

        print(type(images[0]))

        try:
            plt.figure()
            plt.imshow(images[0])
            plt.show()

    except Exception as e:
        print("EXCEPTION: " + str(e))
        return -2

    finally:
        ids_peak.Library.Close()


if __name__ == '__main__':
    main()
