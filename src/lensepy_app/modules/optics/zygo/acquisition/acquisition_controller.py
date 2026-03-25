__all__ = ["ZygoAcquisitionController"]

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QDialog, QLabel
from lensepy import translate
from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
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
        self.top_left = ImageDisplayWidget()
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
            # Check if camera is connected
            self.init_camera()
            super().init_view()
            self.start_live()
        else:
            self.top_left = QLabel('No Camera is connected. \n'
                                   'Connect a camera first.\n'
                                   'Then restart the application.')
            self.top_left.setStyleSheet(styleH2)
            self.bot_left = QWidget()
            self.bot_right = QWidget()
            self.top_right = QWidget()
            super().init_view()

    def init_camera(self):
        """
        Initialize the camera.
        """
        camera = self.parent.variables["camera"]
        # Check if a camera is already connected
        if camera is None:
            # Init Camera
            self.parent.variables["camera"] = CameraIDS()
            self.camera_connected = self.parent.variables["camera"].find_first_camera()
            if self.camera_connected is False:
                self.parent.variables["camera"] = None
            else:
                # Initial parameters
                camera_ini_file = self.parent.parent.config.get('camera_ini')
                ''' NOT WORKING
                if os.path.isfile(camera_ini_file):
                    camera.init_camera_parameters(camera_ini_file)
                    print(f'Camera ini file {camera_ini_file} successfully initialized.')
                '''
        else:
            self.camera_connected = True

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        if self.camera_connected:
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
        """
        Stop live mode, i.e. continuous image acquisition.
        """
        if self.worker is not None:
            # Stop the worker
            self.worker._running = False
            # Wait for thread ending
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # bloque jusqu'à la fin
            # Free ressources
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        # Update Image
        self.top_left.set_image_from_array(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_exposure_changed(self, value):
        """
        Action performed when the exposure time changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Read available formats
            camera.set_exposure(value)
            time.sleep(0.1)
            # Restart live
            self.start_live()

    def handle_voltage_changed(self, value):
        print(f'Voltage = {value} V')

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()
