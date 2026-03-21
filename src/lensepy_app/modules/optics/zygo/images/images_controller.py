__all__ = ["ZygoImagesController"]

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from lensepy_app.modules.optics.zygo.images.images_views import (
    ImagesOpeningWidget, ImagesChoiceView)
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.utils import generate_images_grid
from lensepy_app.modules.optics.zygo.dataset import DataSet

class ZygoImagesController(TemplateController):
    """

    """

    dataset_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = ImagesChoiceView(self)
        self.bot_right = ImagesOpeningWidget(self)
        self.top_right = ImageDisplayWidget()

        # Setup widgets

        if self.get_variables('dataset') is not None:
            self.data_set = self.get_variables('dataset')
            self.update_images()
        else:
            self.data_set = DataSet()
            self.set_variables('dataset', self.data_set)
            print(f'Var = {self.get_variables('dataset')}')
        # Signals
        self.bot_right.image_opened.connect(self.handle_image_opened)
        self.bot_left.images_changed.connect(self.handle_image_changed)


    def update_images(self):
        images_grid = generate_images_grid(self.data_set.get_images_sets(1))
        self.top_right.set_image_from_array(images_grid)
        image1 = self.data_set.images_sets.get_image_from_set(1,1)
        self.top_left.set_image_from_array(image1)
        self.bot_left.update_dataset(self.data_set)
        self.parent.variables['dataset_loaded'] = True
        self.parent.update_menu()

    def handle_image_opened(self, filepath):
        print(f'OPENING : {filepath}')
        self.data_set.load_images_set_from_file(filepath)
        self.update_images()

    def handle_image_changed(self, index, set_index):
        image = self.data_set.images_sets.get_image_from_set(index, set_index)
        image_disp = image.copy().astype(np.uint8)
        self.top_left.set_image_from_array(image_disp)


