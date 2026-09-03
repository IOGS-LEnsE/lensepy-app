import os
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from lensepy import translate
from lensepy.css import *
from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
from lensepy_app.widgets import ImageDisplayWidget



class QuantSamplingCameraController(TemplateController):
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
        self.bot_right = QWidget()
        self.top_right = QWidget()
        # Bits depth
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)

        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.top_left.set_image_from_array(initial_image)
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
        # Test if contrast is checked
        if self.contrast_enabled:
            bits_depth = int(self.parent.variables['bits_depth'])
            max_image = np.max(image)
            image_out = (image / max_image * (2**bits_depth - 1)).astype(np.uint16)
        else:
            image_out = image
        self.top_left.set_image_from_array(image_out)
        # Update ??

        # Store new image.
        self.parent.variables['image'] = image.copy()

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