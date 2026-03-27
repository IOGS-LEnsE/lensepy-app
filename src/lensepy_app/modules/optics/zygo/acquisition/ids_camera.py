from pyueye import ueye
import numpy as np


class CameraIDS:

    def __init__(self):
        self.h_cam = None  # Handle de la caméra
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()
        self.width = 0
        self.height = 0
        self.color_mode = ueye.IS_CM_MONO8  # Monochrome
        self.exposure = ueye.double(100.0)  # microseconds

    def find_first_camera(self):
        if not CameraIDS.is_connected():
            return False
        self.h_cam = ueye.HIDS(0)

        # Camera initialization
        ueye.is_InitCamera(self.h_cam, None)

        ueye.is_SetBinning(self.h_cam, ueye.IS_BINNING_DISABLE)
        ueye.is_SetSubSampling(self.h_cam, ueye.IS_SUBSAMPLING_DISABLE)

        # AOI
        rect_aoi = ueye.IS_RECT()
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        self.width = int(rect_aoi.s32Width)
        self.height = int(rect_aoi.s32Height)

        # Allocation of memory
        ueye.is_AllocImageMem(self.h_cam, self.width, self.height, 8, self.mem_ptr, self.mem_id)
        ueye.is_SetImageMem(self.h_cam, self.mem_ptr, self.mem_id)

        # Start acquisition
        ueye.is_CaptureVideo(self.h_cam, ueye.IS_DONT_WAIT)

        return True

    def set_exposure(self, exposure_us):
        """Définir le temps d'intégration (microsecondes)"""
        self.exposure = ueye.double(exposure_us)
        ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, self.exposure, ueye.sizeof(self.exposure))

    def set_color_mode(self, color=True):
        """Définir le type d'image : True pour couleur, False pour monochrome"""
        if color:
            self.color_mode = ueye.IS_CM_BGRA8_PACKED
        else:
            self.color_mode = ueye.IS_CM_MONO8
        ueye.is_SetColorMode(self.h_cam, self.color_mode)

    def get_image(self):
        """Get an image as a numpy array."""
        ueye.is_CaptureVideo(self.h_cam, ueye.IS_DONT_WAIT)
        pitch = ueye.int()
        ueye.is_GetImageMemPitch(self.h_cam, pitch)
        array = ueye.get_data(
            self.mem_ptr,
            self.width,
            self.height,
            8,  # bits per pixel (ex: 8 pour mono)
            pitch,
            True  # copy → IMPORTANT
        )
        image = np.reshape(array, (self.height, self.width))
        return image

    def is_connected(self):
        return self.h_cam is not None

    @staticmethod
    def is_connected():
        """Test if almost one camera is connected."""
        num_cams = ueye.INT()
        if ueye.is_GetNumberOfCameras(num_cams) == ueye.IS_SUCCESS:
            return num_cams.value > 0
        return False

    def close(self):
        """Free all ressources."""
        ueye.is_FreeImageMem(self.h_cam, self.mem_ptr, self.mem_id)
        ueye.is_ExitCamera(self.h_cam)


# Exemple d'utilisation
if __name__ == "__main__":
    cam = CameraIDS()
    cam.set_exposure(20000)  # 20 ms
    cam.set_color_mode(False)  # Monochrome
    img = cam.get_image()
    print("Image capturée de taille :", img.shape)
    cam.close()