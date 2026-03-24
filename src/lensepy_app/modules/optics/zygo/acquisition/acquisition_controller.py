__all__ = ["ZygoAcquisitionController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app import *
from lensepy_app.modules.optics.zygo.acquisition.ids_camera import *

class ZygoAcquisitionController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = QWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()
        
        # Setup widgets
        ## Test if a camera is connected
        if CameraIDS.is_connected():
            print('Camera connected')

        # Signals

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()
