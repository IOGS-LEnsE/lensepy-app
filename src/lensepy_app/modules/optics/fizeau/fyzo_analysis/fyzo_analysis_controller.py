import os
import time
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from lensepy import translate
from lensepy.css import *
from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
from lensepy_app.widgets import ImageDisplayWidget


class FyzoAnalysisController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None
        self.y_cross = None
        self.contrast_enabled = False       # Enhance contrast
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.thread = None
        self.worker = None

        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = ImageDisplayWidget()
        self.top_right = QWidget()
        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.bot_right.set_image_from_array(initial_image)
        # Signals
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
        bits_depth = self.parent.variables["bits_depth"]
        pow = bits_depth - 8
        if pow > 0:
            image_8bits = image_raw // (2**pow)
        else:
            image_8bits = image_raw

        if self.parent.variables["mask"] is not None:
            mask = self.parent.variables["mask"]
            image_disp = np.ma.masked_where(np.logical_not(mask), image_8bits)
        self.bot_right.set_image_from_array(image_disp)
        # Store new image.
        self.parent.variables['image'] = image_raw
        # Process and display FFT
        fft_raw = self._process_fft(image_8bits)
        fft_disp = self._disp_fft(fft_raw)
        self.top_left.set_image_from_array(fft_disp)
        '''
        fft_disp = fft_disp // np.max(fft_disp
 * 255        time.sleep(0.1)
        '''

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

    def _process_fft(self, image):
        fft = np.fft.fftshift(np.fft.fft2(image))
        return fft

    def _disp_fft(self, fft):
        fft_disp = np.log(np.abs(fft) + 0.001)
        return fft_disp

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