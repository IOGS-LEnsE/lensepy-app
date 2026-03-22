# -*- coding: utf-8 -*-
"""*camera_options_view.py* file.

./views/camera_options_view.py contains CameraOptionsView class to display options
for camera in acquisition mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6.widget_slider import SliderBloc
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.images_display_view import ImagesDisplayView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.acquisition_controller import AcquisitionController


class CameraOptionsView(QWidget):

    settings_changed = pyqtSignal(str)

    def __init__(self, controller: "AcquisitionController" = None):
        """

        """
        super().__init__()
        self.controller: "AcquisitionController" = controller
        self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.camera = self.controller.data_set.acquisition_mode.camera
        self.zoom_activated = False
        self.zoom_window = ImagesDisplayView()
        self.default_parameters = self.controller.main_app.default_parameters
        # Default parameters to update on loading
        if 'Exposure Time' in self.default_parameters:
            self.default_exposure = int(self.default_parameters['Exposure Time'])
        else:
            self.default_exposure = 1000
        self.camera.set_exposure(self.default_exposure)
        if 'Max Expo Time' in self.default_parameters:
            self.default_max_expo = int(self.default_parameters['Max Expo Time'])
        else:
            self.default_max_expo = 5000
        self.default_fps = 8
        self.default_black = 9

        # Title
        self.label_title_camera_settings = QLabel(translate('title_camera_settings'))
        self.label_title_camera_settings.setStyleSheet(styleH1)
        # Camera ID
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()

        self.label_title_camera_id = QLabel(translate("label_title_camera_id"))
        self.label_title_camera_id.setStyleSheet(styleH2)

        self.label_value_camera_id = QLabel()
        if self.camera is not None:

            id_camera, name_camera = self.camera.get_cam_info()
            self.label_value_camera_id.setText(f'{name_camera} / SN = {id_camera}')
        self.label_value_camera_id.setStyleSheet(styleH3)

        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)

        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)

        # Settings
        max_expo = self.default_max_expo
        default_expo = self.default_exposure
        self.slider_exposure_time = SliderBloc(name=translate('name_slider_exposure_time'),
                                               unit='us',
                                               min_value=0, max_value=max_expo, integer=True)
        self.slider_exposure_time.set_value(default_expo)
        self.slider_exposure_time.slider_changed.connect(self.slider_exposure_time_changing)

        default_black = self.default_black
        self.slider_black_level = SliderBloc(name=translate('name_slider_black_level'),
                                             unit='gray',
                                             min_value=0, max_value=100, integer=True)
        self.slider_black_level.set_value(default_black)
        self.slider_black_level.slider_changed.connect(self.slider_black_level_changing)

        self.fps_label = QLabel(f'{translate("frame_rate_label")} = {self.default_fps} FPS')
        self.fps_label.setStyleSheet(styleH2)

        self.zoom_button = QPushButton(translate('camera_zoom_button'))
        self.zoom_button.setStyleSheet(unactived_button)
        self.zoom_button.setFixedHeight(BUTTON_HEIGHT)
        self.zoom_button.clicked.connect(self.zoom_button_clicked)

        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.zoom_button)
        self.layout.addStretch()
        self.layout.addWidget(self.slider_exposure_time)
        self.layout.addWidget(self.slider_black_level)
        self.layout.addWidget(self.fps_label)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def slider_exposure_time_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            exposure_time_value = self.slider_exposure_time.get_value()
            self.camera.set_exposure(exposure_time_value)
            self.settings_changed.emit('camera_settings_changed')
        else:
            print('No Camera Connected')

    def slider_black_level_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            black_level_value = self.slider_black_level.get_value()
            self.camera.set_black_level(black_level_value)
            self.settings_changed.emit('camera_settings_changed')
        else:
            print('No Camera Connected')

    def update_parameters(self) -> None:
        """Update displayed parameters values, from the camera.

        """
        exposure_time = self.camera.get_exposure()
        self.slider_exposure_time.set_value(exposure_time)
        bl = self.camera.get_black_level()
        self.slider_black_level.set_value(bl)
        fps = self.camera.get_frame_rate()
        self.fps_label.setText(f'{translate("frame_rate_label")} = {fps} FPS')

    def zoom_button_clicked(self, event):
        """
        Create the zoom window.
        """
        self.zoom_activated = True
        camera = self.controller.data_set.acquisition_mode.camera
        self.zoom_window.showMaximized()
        self.zoom_window.closeEvent = self.zoom_closed

    def zoom_closed(self, event):
        """
        Deactivate zoom window.
        """
        self.zoom_activated = False


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from controllers.modes_manager import ModesManager
    from views.main_structure import MainView
    from models.dataset import DataSetModel
    from views.main_menu import MainMenu
    from controllers.acquisition_controller import AcquisitionController

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            widget = MainView()
            menu = MainMenu()
            menu.load_menu('')
            widget.set_main_menu(menu)
            data_set = DataSetModel()
            manager = ModesManager(menu, widget, data_set)

            # Test controller
            self.controller = AcquisitionController(manager)
            manager.mode_controller = self.controller
            main_widget = CameraOptionsView(self.controller)
            main_widget.settings_changed.connect(self.settings_changed)
            self.setCentralWidget(main_widget)

        def closeEvent(self, event):
            self.controller.stop_acquisition()

        def settings_changed(self, value):
            print(value)


    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())