__all__ = ["ZygoAcquisitionController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog, QLabel
from lensepy import translate
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.acquisition.ids_camera import *
from lensepy_app.modules.optics.zygo.acquisition.acquisition_view import *
from lensepy.css import *


class ZygoAcquisitionController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = QWidget()
        self.top_right = AcquisitionView(self)
        self.bot_left = CameraParamsView()
        self.bot_right = PiezoControlView(self)
        
        # Setup widgets

        # Signals
        self.bot_right.voltage_changed.connect(self.handle_voltage_changed)
        self.bot_left.exposure_changed.connect(self.handle_exposure_changed)

    def init_view(self):
        ## Test if a camera is connected
        if CameraIDS.is_connected():
            super().init_view()
            print('Camera connected')
        else:
            '''
            print('Camera not connected')
            self.top_left = QLabel('No Camera is connected. \n'
                                   'Connect a camera first.\n'
                                   'Then restart the application.')
            self.top_left.setStyleSheet(styleH2)
            self.bot_left = QWidget()
            self.bot_right = QWidget()
            self.top_right = QWidget()
            '''
            super().init_view()

    def handle_voltage_changed(self, value):
        print(f'Voltage = {value} V')

    def handle_exposure_changed(self, value):
        print(f'Exposure = {value} ms')

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()
