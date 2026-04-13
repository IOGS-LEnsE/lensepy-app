__all__ = ["ZygoAcquisitionController"]

import numpy as np
from lensepy import translate
from lensepy.drivers.ids_camera import *

from PyQt6.QtWidgets import QWidget, QDialog, QLabel
from PyQt6.QtCore import QThread, QObject
from PyQt6 import sip
from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.acquisition.nidaq_piezo import *
from lensepy_app.modules.optics.zygo.acquisition.acquisition_view import *
from lensepy.optics.zygo.dataset import DataSet
from lensepy.optics.zygo.utils import generate_images_grid
from lensepy.css import *


class ZygoAcquisitionController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.data_set = DataSet()
        self.acquiring = False
        self.camera_connected = False
        self.piezo_connected = False
        self.zoom_activated = False
        self.volt_list = []
        self.images = []
        self.nb_images = 0

        # Thread / Worker
        self.thread = None
        self.worker = None

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.top_right = AcquisitionView(self)
        self.bot_left = CameraParamsView()
        self.bot_right = PiezoControlView(self)
        self.zoom_widget = ImageDisplayWidget()
        
        # Setup widgets

        # Signals
        self.bot_right.voltage_changed.connect(self.handle_voltage_changed)
        self.bot_left.exposure_changed.connect(self.handle_exposure_changed)
        self.top_right.acquisition_started.connect(self.handle_acquisition_started)
        self.top_right.zoom_clicked.connect(self.handle_zoom_clicked)

    def handle_acquisition_started(self):
        # TO DO - import from configuration !
        self.volt_list = [0.80, 1.62, 2.43, 3.24, 4.05]
        if self.get_variables("camera") is None or self.get_variables('piezo') is None:
            print('NO PIEZO OR CAM')
            return
        self.stop_live()
        self.start_acquisition()

    def handle_zoom_clicked(self):
        self.stop_live()
        self.zoom_activated = True
        self.zoom_widget.showMaximized()
        self.zoom_widget.closeEvent = self.zoom_closed
        self.start_live()

    def zoom_closed(self, event):
        """
        Deactivate zoom window.
        """
        self.stop_live()
        self.zoom_activated = False
        self.top_right.set_zoom_enabled()
        self.start_live()

    def init_view(self):
        ## Test if a camera is connected
        if CameraIDS.is_connected():
            # Check if camera is connected
            self.init_camera()
            # Test if piezo connected ?
            if NIDaqPiezo.is_piezo_here():
                piezo = NIDaqPiezo()
                if piezo.find_first_piezo():
                    self.bot_right.set_connected()
                    self.top_right.set_acq_enabled()
                    # INIT PIEZO to move here
                    self.set_variables('piezo', piezo)
            self.top_right.set_acq_enabled()
            self.init_piezo()   # only if piezo (to move - tab)
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
            print('No Camera YET')
            # Init Camera
            self.parent.variables["camera"] = CameraIDS()
            self.camera_connected = self.parent.variables["camera"].find_first_camera()
            if self.camera_connected is False:
                self.parent.variables["camera"] = None
            else:
                self.parent.variables["camera"].init_camera()
                # Initial parameters
                camera_ini_file = self.parent.parent.config.get('camera_ini')
            '''
                if os.path.isfile(camera_ini_file):
                    camera.init_camera_parameters(camera_ini_file)
                    print(f'Camera ini file {camera_ini_file} successfully initialized.')
            '''
        else:
            self.camera_connected = True
        print(f'Connected ? {self.camera_connected}')

    def init_piezo(self):
        """Initialization of the piezo wrapper."""
        piezo = self.parent.variables["piezo"]
        # Check if a piezo is connected
        if piezo is None:
            self.parent.variables["piezo"] = NIDaqPiezo()
            self.piezo_connected = self.parent.variables["piezo"].find_first_piezo()
            if self.piezo_connected is False:
                self.parent.variables["piezo"] = None
                return
        else:
            self.piezo_connected = True
        piezo.set_channel(1)    # To change if Channel changed (default param)

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        camera = self.parent.variables["camera"]
        if self.camera_connected:
            camera.start_acquisition()
            self.acquiring = True
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
        if self.acquiring:
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
                self.acquiring = False

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        # Update Image
        if self.zoom_activated:
            self.zoom_widget.set_image_from_array(image)
        else:
            self.top_left.set_image_from_array(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_acquisition_done(self, images, voltages):
        # Reinit UI
        self.top_right.set_acq_enabled()
        # Store new data in data_set
        self.data_set.add_set_images(images)
        self.set_variables('dataset', self.data_set)

        # Display grid of images in an external view
        if images:
            g_images = generate_images_grid(images)
            self.zoom_widget.set_image_from_array(g_images)
            self.zoom_activated = True
            self.top_right.set_zoom_enabled(False)
            self.zoom_widget.showMaximized()
            self.zoom_widget.closeEvent = self.acquisition_closed

        # Tu peux lancer ton traitement ici
        # ex : phase reconstruction

    def acquisition_closed(self, event):
        self.zoom_activated = False
        self.top_right.set_zoom_enabled()

    def handle_exposure_changed(self, value):
        """
        Action performed when the exposure time changed.
        """
        camera = self.parent.variables["camera"]
        try:
            if camera is not None:
                # Read available formats
                camera.set_exposure(value)
                time.sleep(0.01)
        except Exception as e:
            print(f'camera_expo {e}')

    def handle_voltage_changed(self, value):
        print(f'Voltage = {value} V')

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        self.stop_live()
        self.stop_acquisition()
        time.sleep(0.1)
        camera = self.parent.variables["camera"]
        if camera is not None:
            camera.disconnect()
            camera.camera_acquiring = False
        self.worker = None
        self.thread = None
        self.camera_connected = False
        self.parent.variables["camera"] = None

    def start_acquisition(self):
        self.top_right.set_zoom_enabled(False)
        self.bot_right.set_enabled(False)
        self.bot_left.set_enabled(False)

        camera = self.parent.variables.get("camera")
        piezo = self.parent.variables.get("piezo")

        if camera is None:
            return

        self.thread = QThread()
        self.worker = AcquisitionLive(self, self.volt_list, camera, piezo)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)

        self.worker.acquisition_done.connect(self.handle_acquisition_done)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def stop_acquisition(self):
        if self.camera_connected:
            # Reactivate UI
            self.top_right.set_zoom_enabled()
            self.bot_right.set_enabled()
            self.bot_left.set_enabled()
            self.top_right.set_acq_enabled()

            # 🔥 SAFE STOP
            if self.worker is not None:
                try:
                    self.worker.stop()
                except RuntimeError:
                    pass  # déjà deleted

            if self.thread is not None:
                try:
                    if self.thread.isRunning():
                        self.thread.quit()
                        self.thread.wait()
                except RuntimeError:
                    pass  # déjà deleted

            self.worker = None
            self.thread = None

    def update_progress_bar(self, value):
        self.top_right.update_progress_bar(value)


class AcquisitionLive(QObject):
    acquisition_ready = pyqtSignal(np.ndarray)
    acquisition_done = pyqtSignal(list, list)  # images, voltages
    finished = pyqtSignal()

    def __init__(self, controller, volt_list, camera, piezo=None,
                 settle_ms=400, interval_ms=10):
        super().__init__()
        self.controller = controller
        self.volt_list = volt_list
        self.camera = camera
        self.piezo = piezo

        self.settle_ms = settle_ms
        self.interval_ms = interval_ms

        self.index = 0
        self.images = []

        self.timer = None  # Created by start
        self.waiting_settle = False
        self._running = False

    # Start thread / called by thread.started
    def start(self):
        if self.camera is None:
            self.finished.emit()
            return

        self._running = True
        self.camera.camera_acquiring = True

        self.index = 0
        self.images = []
        self.waiting_settle = False

        # Create the timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)  # To control each step time
        self.timer.timeout.connect(self._step)

        self.timer.start(0)  # start timer

    # State machine
    def _step(self):
        if not self._running:
            self._finish()
            return

        # Fin acquisition
        if self.index >= len(self.volt_list):
            self._finish()
            return

        # -------------------------
        # 1️⃣ Appliquer tension
        # -------------------------
        if not self.waiting_settle:
            dac_val = self.volt_list[self.index]
            print(f"DAC = {dac_val}")

            if self.piezo is not None:
                try:
                    self.piezo.write_dac(dac_val)
                except Exception as e:
                    print(f"Piezo error: {e}")

            self.waiting_settle = True
            self.timer.start(self.settle_ms)
            return

        # Acquiring image
        image = None
        try:
            image = self.camera.get_image()
        except Exception as e:
            print(f"Camera error: {e}")

        if image is not None:
            self.images.append(image.copy())
            self.acquisition_ready.emit(image)

        self.index += 1
        self.controller.update_progress_bar(int(100*self.index / len(self.volt_list)))
        self.waiting_settle = False

        # Delay before next point
        self.timer.start(self.interval_ms)

    # External stop
    def stop(self):
        self._running = False

        if self.timer is not None:
            self.timer.stop()

    # =========================
    # 🏁 FIN propre
    # =========================
    def _finish(self):
        if self.timer is not None:
            self.timer.stop()

        if self.camera:
            self.camera.camera_acquiring = False

        # envoyer dataset complet
        self.acquisition_done.emit(self.images, self.volt_list)

        self.finished.emit()

