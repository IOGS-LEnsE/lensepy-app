from ids_peak import ids_peak
from ids_peak_ipl import *
import numpy as np
import cv2

def main():
    # Initialize library
    ids_peak.Library.Initialize()

    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()

    if device_manager.Devices().empty():
        print("No device found")
        return

    # Open first device
    device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)

    # Open datastream
    datastream = device.DataStreams()[0].OpenDataStream()

    # Get nodemap
    nodemap = device.RemoteDevice().NodeMaps()[0]

    # Set acquisition mode
    nodemap.FindNode("AcquisitionMode").SetCurrentEntry("Continuous")

    # Allocate buffers
    payload_size = nodemap.FindNode("PayloadSize").Value()
    num_buffers = datastream.NumBuffersAnnouncedMinRequired()

    for _ in range(num_buffers):
        buffer = datastream.AllocAndAnnounceBuffer(payload_size)
        datastream.QueueBuffer(buffer)

    # Start acquisition
    datastream.StartAcquisition()
    nodemap.FindNode("AcquisitionStart").Execute()
    nodemap.FindNode("AcquisitionStart").WaitUntilDone()

    print("Streaming... press 'q' to quit")

    try:
        while True:
            buffer = datastream.WaitForFinishedBuffer(5000)

            # dimensions
            width = buffer.PixelWidth()
            height = buffer.PixelHeight()

            # format (important !)
            pixel_format = buffer.PixelFormat()

            # pointeur mémoire
            ptr = buffer.BasePtr()

            # tableau numpy brut
            img = np.frombuffer(ptr, dtype=np.uint8)

            # ===== CAS 1 : Mono8 =====
            if pixel_format == "Mono8":
                img = img.reshape((height, width))
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            # ===== CAS 2 : Bayer (très fréquent !) =====
            elif pixel_format == "BayerRG8":
                img = img.reshape((height, width))
                img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR)

            # ===== CAS 3 : RGB8 =====
            elif pixel_format == "RGB8":
                img = img.reshape((height, width, 3))
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            else:
                print("Format non géré:", pixel_format)
                datastream.QueueBuffer(buffer)
                continue

            cv2.imshow("IDS Camera", img)

            # ⚠️ SUPER IMPORTANT
            datastream.QueueBuffer(buffer)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except ids_peak.Exception as e:
        print("IDS Peak error:", str(e))

    finally:
        # Proper shutdown (IMPORTANT)
        print("Stopping acquisition...")

        try:
            nodemap.FindNode("AcquisitionStop").Execute()
        except:
            pass

        try:
            datastream.KillWait()
        except:
            pass

        try:
            datastream.StopAcquisition()
        except:
            pass

        # Flush buffers
        try:
            datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
        except:
            pass

        # Revoke buffers
        for buffer in datastream.AnnouncedBuffers():
            try:
                datastream.RevokeBuffer(buffer)
            except:
                pass

        ids_peak.Library.Close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()