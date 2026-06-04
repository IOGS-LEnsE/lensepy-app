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
from lensepy_app.modules.optics.fizeau.fyzo_analysis.fyzo_analysis_views import FyzoAnalysisOptionsView
from lensepy_app.widgets.double_3d_view import Surface3DView
from lensepy_app.widgets.surface_2D_view import Surface2DView
from skimage.restoration import unwrap_phase

FPS_FFT = 3
LAMBDA_LASER = 0.670 #micron

class FyzoAnalysisController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None
        self.y_cross = None
        self.contrast_enabled = False       # Enhance contrast
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.disp_mode = 'surface'
        self.image_disp = None
        self.fft_raw = None
        self.fft_masked = None
        self.fft_center = None
        self.unwrapped_phase = None
        self.surface = None

        self.view_2D = None
        self.view_3D = None

        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = ImageDisplayWidget()
        self.top_right = FyzoAnalysisOptionsView()
        # Set Up widgets
        self.top_right.activate_mode(self.disp_mode)
        # Signals
        self.top_right.display_changed.connect(self.handle_display_changed)
        self.top_right.view_saved.connect(self.handle_png_saved)
        # Crop size / mask
        mask = self.parent.variables['mask']
        top_left, bottom_right = find_mask_limits(mask)
        self.img_height, self.img_width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
        self.img_pos_x, self.img_pos_y = top_left[1], top_left[0]
        self.mask = crop_images([mask], (self.img_height, self.img_width), (self.img_pos_x, self.img_pos_y))[0]
        # Initial Image
        self.initial_image = self.parent.variables.get('image')
        if self.initial_image is not None:
            self.bot_right.set_image_from_array(self.initial_image)
            self.update_view()
            self.process_data()
            self.image_ready()

    def process_data(self):
        image_raw = self.initial_image
        # Crop image
        image_raw = crop_images([image_raw], (self.img_height, self.img_width), (self.img_pos_x, self.img_pos_y))[0]
        # Post Image
        bits_depth = self.parent.variables["bits_depth"]
        pow = bits_depth - 8
        if pow > 0:
            image_8bits = image_raw // (2**pow)
        else:
            image_8bits = image_raw

        if self.parent.variables["mask"] is not None:
            # mask = self.parent.variables["mask"]
            self.image_disp = np.ma.masked_where(np.logical_not(self.mask), image_8bits)
        else:
            self.image_disp = image_8bits
        self.bot_right.set_image_from_array(self.image_disp)
        # Store new image.
        self.parent.variables['image'] = image_raw
        # 3 modes
        self.fft_raw = self._process_fft(image_raw)
        self.fft_masked, idx_X, idx_Y = self._get_masked_fft(self.fft_raw)
        self.fft_center = self._get_centered_fft(self.fft_masked, idx_X, idx_Y)

        # Phase / Surface
        champ = np.fft.ifft2(np.fft.ifftshift(self.fft_center))
        champ[~self.mask] = 0

        wrapped_phase = np.angle(champ)
        self.unwrapped_phase = unwrap_phase(wrapped_phase)
        self.unwrapped_phase[~self.mask] = np.nan

        # Surface
        Masq = self.mask
        xx = (np.arange(-self.img_width // 2, self.img_width // 2) / self.img_width) * 2
        yy = (np.arange(-self.img_height // 2, self.img_height // 2) / self.img_height) * 2
        Xg, Yg = np.meshgrid(xx, yy)
        A = np.column_stack((np.ones(np.sum(self.mask)), Xg[self.mask], Yg[self.mask]))
        Z = self.unwrapped_phase[self.mask]
        coeffs, *_ = np.linalg.lstsq(A, Z, rcond=None)
        phase_corr = np.full_like(self.unwrapped_phase, np.nan)
        phase_corr[self.mask] = Z - A @ coeffs
        # Process surface
        self.surface = phase_corr / (4 * np.pi) * LAMBDA_LASER  # d éfaut en réflexion
        self.surface[~self.mask] = np.nan
        self.surface = np.ma.masked_where(np.logical_not(self.mask), self.surface)

    def process_stats(self):
        surface_val = self.surface[self.mask & ~np.isnan(self.surface)]
        PV_micron = np.max(surface_val) - np.min(surface_val)
        RMS_micron = np.sqrt(np.mean((surface_val - np.mean(surface_val)) ** 2))
        print(f'PV = {PV_micron:.2f} um | RMS = {RMS_micron:.2f} um')

    def image_ready(self):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        # default display
        widget = ImageDisplayWidget()
        self.replace_top_left_widget(widget)
        # Display mode
        if self.disp_mode == 'interfer':
            self.top_left.set_image_from_array(self.image_disp)
        elif self.disp_mode == 'fft':
            # Process and display FFT
            self.top_left.set_image_from_array(self._disp_fft(self.fft_raw))
        elif self.disp_mode == 'fft_masked':
            self.top_left.set_image_from_array(self._disp_fft(self.fft_masked))
        elif self.disp_mode == 'fft_centered':
            self.top_left.set_image_from_array(self._disp_fft(self.fft_center))
        elif self.disp_mode == 'phase':
            view_2D = Surface2DView()
            view_2D.set_array2(self.unwrapped_phase)
            view_2D.update()
            # TO UPDATE
            self.replace_top_left_widget(view_2D)
        elif self.disp_mode == 'surface':
            print('Init OK')
            self.view_2D = Surface2DView()
            self.view_2D.set_array2(self.surface)
            self.replace_top_left_widget(self.view_2D)
            # TO UPDATE
        elif self.disp_mode == 'surface_3D':
            self.view_3D = Surface3DView()
            x, y, w_s = self.view_3D.prepare_data_for_mesh(self.surface, undersampling=1) # TO CHANGE
            self.view_3D.create_mesh_surface(x, y, w_s)
            self.replace_top_left_widget(self.view_3D)
        else:
            self.top_left.set_image_from_array(self.image_disp)


    def handle_display_changed(self, value):
        self.disp_mode = value
        self.image_ready()

    def set_disp_mode(self, value):
        # Value = {'interfer', 'fft', 'fft_masked', 'fft_centered', 'phase', 'surface'}
        self.disp_mode = value

    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False

    ### FFT and display
    def _process_fft(self, image):
        fft = np.fft.fftshift(np.fft.fft2(image))
        return fft

    def _disp_fft(self, fft):
        fft_disp = np.log(np.abs(fft) + 1)
        max_disp = np.max(fft_disp)
        fft_disp = ((fft_disp / max_disp) * 255).astype(np.uint8)
        return fft_disp

    def _get_masked_fft(self, fft):
        central_radius = 80  # rayon zone centrale
        excent_radius = 50  # largeur pic latéral
        central_mask = circular_mask(central_radius, fft, inverted=True)
        imx, jmx = np.unravel_index(np.argmax(np.abs(central_mask)), fft.shape)
        excent_mask = circular_mask(excent_radius, fft, center=(imx, jmx))
        return excent_mask, imx, jmx

    def _get_centered_fft(self, fft, imx, jmx):
        Itf_filtr = np.zeros_like(fft)
        fft_center_Y, fft_center_X = fft.shape
        centered_fft = np.roll(fft, shift=(fft_center_X - imx, fft_center_Y - jmx), axis=(0, 1))  # démodulation
        return np.fft.fftshift(centered_fft)

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

    def replace_top_left_widget(self, new_widget):
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def handle_png_saved(self, filepath):
        if filepath is not None:
            # Display mode
            if self.disp_mode == 'interfer':
                cv2.imwrite(filepath, self.image_disp)
            elif self.disp_mode == 'fft':
                cv2.imwrite(filepath, self._disp_fft(self.fft_raw))
            elif self.disp_mode == 'fft_masked':
                cv2.imwrite(filepath, self._disp_fft(self.fft_masked))
            elif self.disp_mode == 'fft_centered':
                cv2.imwrite(filepath, self._disp_fft(self.fft_center))
            elif self.disp_mode == 'phase':
                self.view_2D.save_image(filepath)
            elif self.disp_mode == 'surface':
                self.view_2D.save_image(filepath)
            elif self.disp_mode == 'surface_3D':
                self.view_3D.save_image(filepath)