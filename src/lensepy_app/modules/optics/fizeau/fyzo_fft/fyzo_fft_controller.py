import os
import time
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from lensepy import translate
from lensepy.css import *
from lensepy.images.masks import *
from lensepy.images.conversion import *
from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
from lensepy_app.widgets import ImageDisplayWidget
from lensepy_app.modules.optics.fizeau.fyzo_fft.fyzo_fft_views import *

FPS_FFT = 3


def gray_to_rgb(image_gray):
    return np.stack([image_gray] * 3, axis=-1)


def add_circle(image, center=None, radius=10, color=(255, 255, 255), thickness=2):
    """
    Draw a circle on the image
    ----------
    image : np.array (H, W, 3)
    centre : tuple (x, y)
    rayon : int
    couleur : tuple (R, G, B)

    Retour
    ------
    np.array : image modifiée
    """

    img = image.copy()
    if center is None:
        x0, y0 = img.shape[1] // 2, img.shape[0] // 2
    else:
        x0, y0 = center
    y, x = np.ogrid[:img.shape[0], :img.shape[1]]
    # Distance from center
    distance = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
    # Disc
    mask = (
            (distance >= radius - thickness / 2)
            & (distance <= radius + thickness / 2)
    )
    img[mask] = color
    return img


class FyzoAnalysisController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None
        self.y_cross = None
        self.contrast_enabled = False       # Enhance contrast
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.disp_mode = 'fft_circled'
        self.thread = None
        self.worker = None

        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = ImageDisplayWidget()
        self.top_right = FyzoFFTOptionsView()
        # Set Up widgets
        self.top_right.activate_mode(self.disp_mode)
        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.bot_right.set_image_from_array(initial_image)
        camera = self.parent.variables["camera"]
        camera.set_parameter("AcquisitionFrameRate", FPS_FFT)
        # Signals
        self.top_right.display_changed.connect(self.handle_display_changed)
        # Crop size / mask
        mask = self.parent.variables['mask']
        top_left, bottom_right = find_mask_limits(mask)
        self.img_height, self.img_width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
        self.img_height_fft, self.img_width_fft = self.img_height//4, self.img_width//4
        self.img_pos_x, self.img_pos_y = top_left[1], top_left[0]
        self.mask = crop_images([mask], (self.img_height, self.img_width), (self.img_pos_x, self.img_pos_y))[0]
        self.mask_fft = crop_images([mask], (self.img_height_fft, self.img_width_fft), (self.img_pos_x, self.img_pos_y))[0]
        # Start live acquisition
        self.start_live()

    def start_live(self):
        """Start live acquisition with camera."""
        self.thread = QThread()
        self.worker = ImageLive(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.handle_image_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def stop_live(self):
        """Stop live acquisition."""
        if self.worker:
            self.worker.stop()
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        image_raw = image.copy()
        # Crop image
        image_crop = crop_images([image_raw], (self.img_height, self.img_width), (self.img_pos_x, self.img_pos_y))[0]
        # Post Image
        bits_depth = self.parent.variables["bits_depth"]
        pow = bits_depth - 8
        if pow > 0:
            image_8bits = image_crop // (2**pow)
        else:
            image_8bits = image_crop

        if self.parent.variables["mask"] is not None:
            image_disp = np.ma.masked_where(np.logical_not(self.mask), image_8bits)
        self.bot_right.set_image_from_array(image_disp)
        # Store new image.
        self.parent.variables['image'] = image_raw
        # Different display
        fft_raw = self._process_fft(image_8bits)
        if self.disp_mode == 'interfer':
            main_disp = image_disp
        elif self.disp_mode == 'fft':
            # Process and display FFT
            main_disp = self._disp_fft(fft_raw)
        elif self.disp_mode == 'fft_circled':
            main_disp = self._get_circled_fft(self._disp_fft(fft_raw))
        else:
            main_disp = image_disp
        self.top_left.set_image_from_array(main_disp)

    def handle_display_changed(self, value):
        self.disp_mode = value

    def set_disp_mode(self, value):
        # Value = {'interfer', 'fft', 'fft_circled'}
        self.disp_mode = value

    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        self.stop_live()
        camera = self.parent.variables["camera"]
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False
        self.worker = None
        self.thread = None

    ### FFT and display
    def _process_fft(self, image):
        fft = np.fft.fftshift(np.fft.fft2(image))
        return fft

    def _disp_fft(self, fft):
        fft_disp = np.log(np.abs(fft) + 1)
        max_disp = np.max(fft_disp)
        fft_disp = ((fft_disp / max_disp) * 255).astype(np.uint8)
        return fft_disp

    def _get_circled_fft(self, fft):
        width = fft.shape[0]
        central_radius = width // 6  # rayon zone centrale
        excent_radius = int(width * 0.4)  # largeur pic latéral
        fft_rgb = gray_to_rgb(fft)
        circled_fft = add_circle(fft_rgb, radius=central_radius, color=(255, 0, 255), thickness=3)
        circled_fft = add_circle(circled_fft, radius=excent_radius, color=(0, 255, 255), thickness=3)
        return circled_fft

    def _get_image_dir(self, filepath):
        if filepath is None:
            return ''
        else:
            # Detect if % in filepath
            if '%USER' in filepath:
                new_filepath = filepath.split('%')
                new_filepath = f'{Path.home()}/{new_filepath[2]}'
                return new_filepath
            else:
                return filepath