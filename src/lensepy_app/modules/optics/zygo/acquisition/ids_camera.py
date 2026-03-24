from pyueye import ueye
import numpy as np


class CameraIDS:

    def __init__(self, camera_id=0):
        self.h_cam = ueye.HIDS(camera_id)  # Handle de la caméra
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.INT()
        self.width = 640
        self.height = 480
        self.color_mode = ueye.IS_CM_MONO8  # Par défaut : image monochrome
        self.exposure = 10000  # en microsecondes

        # Initialisation de la caméra
        if ueye.is_InitCamera(self.h_cam, None) != ueye.IS_SUCCESS:
            raise RuntimeError("Impossible d'initialiser la caméra IDS.")

        # Définir la taille de l'image
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = 0
        rect_aoi.s32Y = 0
        rect_aoi.s32Width = self.width
        rect_aoi.s32Height = self.height
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        # Allouer la mémoire pour l'image
        ueye.is_AllocImageMem(self.h_cam, self.width, self.height, 8, self.mem_ptr, self.mem_id)
        ueye.is_SetImageMem(self.h_cam, self.mem_ptr, self.mem_id)

        # Activer le mode d'exposition automatique (facultatif)
        ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, self.exposure, ueye.sizeof(self.exposure))

    def set_exposure(self, exposure_us):
        """Définir le temps d'intégration (microsecondes)"""
        self.exposure = int(exposure_us)
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
        array = ueye.get_data(self.mem_ptr, self.width, self.height, 1, self.color_mode)
        return np.reshape(array, (self.height, self.width, -1) if self.color_mode != ueye.IS_CM_MONO8
        else (self.height, self.width))

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