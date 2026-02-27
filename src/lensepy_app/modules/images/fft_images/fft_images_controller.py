from PyQt6.QtWidgets import QWidget
import numpy as np
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.images.fft_images.fft_images_views import *
from lensepy.modules.images.fft_images.fft_images_models import *
from lensepy.widgets import ImageDisplayWidget, ImageDisplayWithCrosshair


class FFTImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = ImageDisplayWidget()            # Initial Image
        self.top_right = ImageDisplayWithCrosshair()    # FFT of the image
        self.bot_left = ImageDisplayWidget()    # inverse FFT of the image
        self.bot_right = FFTImagesParamsWidget(self)      # Mask on FFT
        # Setup widgets

        # Signals
        self.bot_right.mask_changed.connect(self.handle_mask_changed)
        # FFT Initialization
        image = self.parent.variables['image']
        self.fft_img_shift = process_FFT(image)
        self.magnitude_spectrum_init = 20 * np.log(np.abs(self.fft_img_shift) + 0.001)
        self.parent.variables['fft_image'] = self.magnitude_spectrum_init
        self.display_image_fft()

    def handle_mask_changed(self, form, radius):
        """Action performed when a mask is selected."""
        print(f'type = {form} / {int(radius)}')
        image = self.parent.variables['image']
        mask = create_mask(self.magnitude_spectrum_init, form, int(radius))
        if form != '':
            magnitude_spectrum = self.magnitude_spectrum_init * mask
        else:
            magnitude_spectrum = self.magnitude_spectrum_init
        self.parent.variables['fft_image'] = magnitude_spectrum
        self.display_image_fft()
        # FFT -1
        fft_image_mask = self.fft_img_shift * mask
        new_image = np.fft.ifft2(np.fft.ifftshift(fft_image_mask))
        self.bot_left.set_image_from_array(np.abs(new_image).astype(np.uint8))

    def create_mask(self, type: str = None, radius: int = 10):
        image = self.parent.variables['image']
        H, W = image.shape[:2]
        cx = W // 2
        cy = H // 2
        if type == 'circular':
            y, x = np.ogrid[:H, :W]
            dist2 = (x - cx) ** 2 + (y - cy) ** 2
            mask = dist2 <= (radius ** 2)
            return mask
        elif type == 'square':
            print('square')
        elif type == 'gaussian':
            sigma = 2
            y, x = np.ogrid[:H, :W]
            mask = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma ** 2))
            return mask
        return None

    def display_image_fft(self):
        """
        Display the main image and its FFT.
        :return:
        """
        image = self.parent.variables['image']
        self.top_left.set_image_from_array(image)
        if self.parent.variables['fft_image'] is not None:
            fft_image = self.parent.variables['fft_image']
            self.top_right.set_image_from_array(fft_image)


