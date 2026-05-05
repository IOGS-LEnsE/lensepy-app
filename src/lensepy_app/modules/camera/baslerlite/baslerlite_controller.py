import time
from PyQt6.QtCore import QObject, QThread
from PyQt6.QtWidgets import QDialog

from lensepy_app.appli._app.template_controller import TemplateController, ImageLive
from lensepy_app.modules.camera.baslerlite.baslerlite_views import *
from lensepy_app.modules.camera.basler.basler_models import *
#from lensepy_app.widgets.camera_widget import *
from lensepy_app.widgets.image_display_widget import *
from lensepy_app.widgets.histogram_widget import *
from lensepy import translate
from lensepy_app.modules.optics.zygo.masks.masks_view import MasksView


class BaslerController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """
        :param parent:
        """
        super().__init__(parent)
        # Attributes initialization
        self.camera_connected = False       # Camera is connected
        self.thread = None
        self.worker = None
        self.colormode = []
        self.colormode_bits_depth = []
        self.masked = False
        # Check if camera is connected
        self.init_camera()
        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = HistogramWidget()
        self.top_right = CameraInfosWidget(self)
        self.bot_right = CameraParamsWidget(self)
        # Widgets setup and signals
        self.bot_left.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))

        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_right.label_fps.set_value(str(fps))
        # Signals
        self.top_right.mask_updated.connect(self.handle_mask)
        self.top_right.mask_applied.connect(self.handle_mask_applied)
        # Widgets setup
        mask = self.parent.variables["mask"]
        if mask is not None:
            self.top_right.activate_mask_check(True)

    def init_view(self):
        """
        Update graphical objects of the interface.
        """
        # Update view
        if self.parent.variables['camera'] is not None:
            super().init_view()
            self.set_color_mode()
            self.set_max_exposure_time()
            self.update_color_mode()
            camera = self.parent.variables['camera']
            # Setup widgets
            self.bot_left.set_background('white')
            self.top_right.update_infos()
            # Init widgets
            if self.parent.variables['bits_depth'] is not None:
                self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
                self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            else:
                self.bot_left.set_bits_depth(8)
            if self.parent.variables['image'] is not None:
                self.top_left.set_image_from_array(self.parent.variables['image'])
                self.bot_left.set_image(self.parent.variables['image'])
            self.bot_left.refresh_chart()
            # Signals
            self.bot_right.exposure_time_changed.connect(self.handle_exposure_time_changed)
            self.bot_right.black_level_changed.connect(self.handle_black_level_changed)
            self.start_live()
        else:
            self.top_left = QLabel('No Camera is connected. \n'
                                   'Connect a camera first.\n'
                                   'Then restart the application.')
            self.top_left.setStyleSheet(styleH2)
            self.bot_left = QWidget()
            self.top_right = QWidget()
            self.bot_right = QWidget()
            super().init_view()

    def init_camera(self):
        """
        Initialize the camera.
        """
        camera = self.parent.variables["camera"]
        # Check if a camera is already connected
        if camera is None:
            # Init Camera
            self.parent.variables["camera"] = BaslerCamera()
            self.camera_connected = self.parent.variables["camera"].find_first_camera()
            if self.camera_connected is False:
                self.parent.variables["camera"] = None
            else:
                camera = self.parent.variables["camera"]
                self.parent.variables["first_connexion"] = 'Yes'
                # Initial parameters
                camera_ini_file = self.parent.parent.config.get('camera_ini')
                if camera_ini_file is not None:
                    if os.path.isfile(camera_ini_file):
                        camera.init_camera_parameters(camera_ini_file)
        else:
            self.camera_connected = True
            self.parent.variables["first_connexion"] = 'No'

    def set_color_mode(self):
        # Get color mode list
        colormode_get = self.parent.xml_app.get_sub_parameter('camera','colormode')
        colormode_get = colormode_get.split(',')
        for colormode in colormode_get:
            colormode_v = colormode.split(':')
            self.colormode.append(colormode_v[0])
            self.colormode_bits_depth.append(int(colormode_v[1]))

    def set_max_exposure_time(self):
        exposuretime_get = self.parent.xml_app.get_sub_parameter('camera', 'exposuretime')
        self.bot_right.set_max_exposure_time(exposuretime_get)

    def update_color_mode(self):
        camera = self.parent.variables["camera"]
        # Update to first mode if first connection
        first_mode_color = self.colormode[0]
        camera.open()
        camera.set_parameter("PixelFormat", first_mode_color)
        camera.initial_params["PixelFormat"] = first_mode_color
        camera.close()
        first_bits_depth = self.colormode_bits_depth[0]
        self.parent.variables["bits_depth"] = first_bits_depth
        pix_format = camera.get_parameter('PixelFormat')
        self.top_right.label_color_mode.set_value(pix_format)

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
            # Arrêter le worker
            self.worker._running = False

            # Attendre la fin du thread
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # bloque jusqu'à la fin

            # Supprimer les références
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        image_disp = image.copy()
        if self.masked and self.parent.variables["mask"] is not None:
            mask = self.parent.variables["mask"]
            image_disp = np.ma.masked_where(np.logical_not(mask), image_disp)
        # Update Image
        self.top_left.set_image_from_array(image_disp)
        # Update Histo
        self.bot_left.set_image(image_disp)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_exposure_time_changed(self, value):
        """
        Action performed when the exposure time changed.
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
            print(f'EXPO  TIME CHANGED: {value}')
            # Restart live
            camera.open()
            self.start_live()

    def handle_black_level_changed(self, value):
        """
        Action performed when the black level changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            camera.set_parameter('BlackLevel', value)
            camera.initial_params['BlackLevel'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

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

    def handle_mask(self):
        type = 'circular'
        help = 'Select 3 different points and then Click Enter'
        bits_depth = self.parent.variables["bits_depth"]
        pow = bits_depth - 8
        if pow > 0:
            first_image = self.parent.variables["image"] // (2**pow)
        else:
            first_image = self.parent.variables["image"]
        dialog = MasksView(first_image, type, help)
        result = dialog.exec()
        if result == QDialog.DialogCode.Rejected:
            message_box('No mask added', 'No mask will be added to the list of masks.')
            self.top_right.activate_mask_button(False)
        else:
            mask = dialog.mask.copy()
            self.parent.variables["mask"] = mask
            self.top_right.activate_mask_button(False)
            self.top_right.activate_mask_check()
            self.parent.update_menu()

    def handle_mask_applied(self, value):
        self.masked = value