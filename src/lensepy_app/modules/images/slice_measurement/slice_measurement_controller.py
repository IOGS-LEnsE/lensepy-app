import os
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from lensepy import translate
from lensepy.css import *
from lensepy.appli._app.template_controller import TemplateController, ImageLive
from lensepy.widgets import ImageDisplayWithCrosshair, XYMultiChartWidget, HistoStatsWidget
from lensepy.modules.images.slice_measurement.slice_measurement_views import SliceMeasurementWidget


class SliceMeasurementController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None
        self.y_cross = None
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.thread = None
        self.worker = None

        # Widgets
        self.top_left = XYMultiChartWidget()
        self.bot_left = ImageDisplayWithCrosshair()
        self.bot_right = QWidget()
        self.top_right = SliceMeasurementWidget()
        self.top_left.set_background('white')
        # Bits depth
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.bot_left.set_bits_depth(bits_depth)

        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.bot_left.set_image_from_array(initial_image)
            self.update_slices(initial_image)
        # Camera infos
        camera = self.parent.variables['camera']
        # Signals
        self.bot_left.point_selected.connect(self.handle_xy_changed)
        self.top_left.horizontal_point_selected.connect(self.handle_horizontal_meas)
        self.top_left.vertical_point_selected.connect(self.handle_vertical_meas)
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

    def handle_horizontal_meas(self, x0, y0, x1, y1):
        self.top_right.set_horizontal_xy(x0, y0, x1, y1)

    def handle_vertical_meas(self, x0, y0, x1, y1):
        self.top_right.set_vertical_xy(x0, y0, x1, y1)

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        self.bot_left.set_image_from_array(image)
        # Update Slices
        self.update_slices(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_xy_changed(self, x, y):
        """
        Action performed when a crosshair is selected.
        :param x: X coordinate.
        :param y: Y coordinate.
        """
        self.x_cross = x
        self.y_cross = y
        image = self.parent.variables.get('image')
        if image is not None:
            self.update_slices(image)

    def handle_exposure_changed(self, value):
        """
        Action performed when the color mode changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            camera.set_parameter('ExposureTime', value)
            camera.initial_params['ExposureTime'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    # Slices
    def update_slices(self, image):
        """
        Update slice values from image.
        :param image:   Numpy array containing the new image.
        """
        if self.x_cross is None or self.y_cross is None or image is None:
            return
        # Image format detection : grayscale or RGB
        if image.ndim == 2:  # grayscale
            gray_image = image
        elif image.ndim == 3 and image.shape[2] == 3:  # RGB
            gray_image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            raise ValueError("Image format unsupported")
        x_idx, y_idx = int(self.x_cross), int(self.y_cross)
        x_data = gray_image[y_idx, :]
        y_data = gray_image[:, x_idx]

        # Utilise np.arange pour générer directement les positions
        xx = np.arange(1, x_data.size + 1)
        yy = np.arange(1, y_data.size + 1)

        # Structure plus compacte
        self.top_left.set_data(
            [xx, yy],
            [x_data, y_data],
            y_names=[translate('horizontal'), translate('vertical')],
            x_label='position',
            y_label='intensity'
        )
        self.top_left.refresh_chart()
        self.top_left.set_information(
            f'Mean H = {np.mean(x_data):.1f} / Min = {np.min(x_data):.1f} / Max = {np.max(x_data):.1f} [] '
            f'Mean V = {np.mean(y_data):.1f} / Min = {np.min(y_data):.1f} / Max = {np.max(y_data):.1f}')

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