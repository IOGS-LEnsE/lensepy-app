__all__ = ["ZygoImagesController"]

import os
import cv2
import numpy as np
from PyQt6.QtCore import pyqtSignal
from lensepy_app.modules.optics.zygo.images.images_views import (
    ImagesOpeningWidget, ImagesChoiceView)
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy.optics.zygo.utils import generate_images_grid
from lensepy.optics.zygo.dataset import DataSet

class ZygoImagesController(TemplateController):
    """

    """

    dataset_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.name = 'ZygoImagesController'
        self.mask_displayed = 0

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = ImagesChoiceView(self)
        self.bot_right = ImagesOpeningWidget(self)
        self.top_right = ImageDisplayWidget()

        # Setup widgets

        if self.get_variables('dataset') is not None:
            self.data_set = self.get_variables('dataset')
            print('Data_set OK')
            if not self.data_set.is_empty():
                self.update_images()
                self.data_set.reset_processes()
                self.bot_right.set_enabled()
        else:
            self.data_set = DataSet()
            self.set_variables('dataset', self.data_set)
        # Signals
        self.bot_right.image_opened.connect(self.handle_image_opened)
        self.bot_right.image_png_saving.connect(self.handle_saving_png)
        self.bot_right.image_mat_saving.connect(self.handle_saving_mat)
        self.bot_left.images_changed.connect(self.handle_image_changed)
        self.bot_left.masks_changed.connect(self.handle_mask_changed)

    def update_images(self):
        images_grid = generate_images_grid(self.data_set.get_images_sets(1))
        self.top_right.set_image_from_array(images_grid)
        image1 = self.data_set.images_sets.get_image_from_set(1,1)
        self.top_left.set_image_from_array(image1)
        self.bot_left.update_dataset(self.data_set)
        self.parent.variables['dataset_loaded'] = True
        self.parent.update_menu()

    def handle_saving_png(self, filepath):
        """Save grid and first image to png file."""
        # Save first image of the first set in filepath
        image1 = self.data_set.images_sets.get_image_from_set(1, 1).astype(np.uint8)
        cv2.imwrite(filepath, image1)
        # Save grid in filepath_grid.png file
        images_grid = generate_images_grid(self.data_set.get_images_sets(1)).astype(np.uint8)
        filepath_grid = f'{os.path.splitext(filepath)[0]}_grid.png'
        cv2.imwrite(filepath_grid, images_grid)

    def handle_saving_mat(self, filepath):
        """Save data to a MAT file."""
        print('SAVE MAT - TO DO')
        self.data_set.save_file(filepath)

    def handle_image_opened(self, filepath):
        im_ok = self.data_set.load_images_set_from_file(filepath)
        if im_ok:
            mask_ok = self.data_set.load_masks_from_file(filepath)
            if mask_ok:
                self.parent.variables['mask_loaded'] = True
                self.parent.update_menu()
            self.update_images()

    def handle_image_changed(self, index, set_index):
        image = self.data_set.images_sets.get_image_from_set(index, set_index)
        image_disp = image.copy().astype(np.uint8)
        if self.mask_displayed != 0:
            mask, _ = self.data_set.masks_sets.get_mask(self.mask_displayed)
            image_disp = (mask * image).astype(np.uint8)
        self.top_left.set_image_from_array(image_disp)

    def handle_mask_changed(self, index, set_index, mask_index):
        image = self.data_set.images_sets.get_image_from_set(index, set_index)
        image_disp = image.copy().astype(np.uint8)
        self.mask_displayed = mask_index
        if mask_index != 0:
            mask, _ = self.data_set.masks_sets.get_mask(mask_index)
            image_disp = (mask * image).astype(np.uint8)
        self.top_left.set_image_from_array(image_disp)

