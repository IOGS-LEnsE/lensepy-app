import time
from PyQt6.QtCore import QObject, QThread
from lensepy.appli._app.template_controller import TemplateController, ImageLive
from lensepy.modules.camera.basler.basler_views import *
from lensepy.modules.camera.basler.basler_models import *
from lensepy.widgets import *
from lensepy import translate


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
        self.camera_range = [0, 0, 0, 0]
        # Widgets
        self.top_left = RectangleDisplayWidget()
        self.bot_left = HistogramWidget()
        self.top_right = CameraInfosWidget(self)
        self.bot_right = CameraParamsWidget(self)
        # Widgets setup and signals
        self.bot_left.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))
        self.top_left.set_enabled(True)
        self.top_left.rectangle_changed.connect(self.handle_rect_changed)
        self.top_right.roi_changed.connect(self.handle_rect_changed)
        self.top_right.roi_centered.connect(self.handle_roi_centered)
        self.top_right.roi_reset.connect(self.handle_roi_reset)
        self.top_right.roi_activated.connect(self.handle_roi_activated)
        # Check if camera is connected
        self.init_camera()
        x0, y0, x1, y1 = self.camera_range
        self.top_right.set_roi([x0, y0, x1, y1])
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_right.label_fps.set_value(str(fps))
        if self.parent.variables['roi_coords'] is not None:
            self.top_right.set_roi(self.parent.variables['roi_coords'])
            self.top_left.draw_rectangle(self.parent.variables['roi_coords'])

    def init_view(self):
        """
        Update graphical objects of the interface.
        """
        # Update view
        if self.parent.variables['camera'] is not None:
            super().init_view()
            self.set_color_mode()
            self.set_max_exposure_time()
            self.top_right.label_color_mode.set_values(self.colormode)
            self.update_color_mode()
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
            self.top_right.color_mode_changed.connect(self.handle_color_mode_changed)
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
                if os.path.isfile(camera_ini_file):
                    camera.init_camera_parameters(camera_ini_file)
                    print(f'Camera ini file {camera_ini_file} successfully initialized.')

                # ROI management
                x0, y0, x1, y1 = self._get_max_coords()
                self.camera_range = [x0, y0, x1, y1]
                self.parent.variables["roi_coords"] = self.camera_range
        else:
            self.camera_connected = True
            self.parent.variables["first_connexion"] = 'No'
            x0, y0, x1, y1 = self._get_max_coords()
            self.camera_range = [x0, y0, x1, y1]

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
        pix_format = camera.get_parameter('PixelFormat')
        if 'first_connexion' in self.parent.variables:
            if self.parent.variables['first_connexion'] == 'Yes':
                first_mode_color = self.colormode[0]
                camera.open()
                camera.set_parameter("PixelFormat", first_mode_color)
                camera.initial_params["PixelFormat"] = first_mode_color
                camera.close()
                first_bits_depth = self.colormode_bits_depth[0]
                self.parent.variables["bits_depth"] = first_bits_depth
            else:
                idx = self.colormode.index(pix_format)
                self.top_right.label_color_mode.set_choice(idx)
                new_bits_depth = self.colormode_bits_depth[idx]
                self.parent.variables["bits_depth"] = new_bits_depth
            black_level = camera.get_parameter('BlackLevel')
            self.bot_right.set_black_level(black_level)

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
        # Update Image
        self.top_left.set_image_from_array(image)
        # Update Histo
        self.bot_left.set_image(image, checked=False)
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
            # Restart live
            camera.open()
            self.start_live()

    def handle_color_mode_changed(self, event):
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
            available_formats = []
            try:
                if camera.camera_device is not None:
                    camera.open()
                    available_formats = list(camera.camera_device.PixelFormat.Symbolics)
                    camera.close()
            except Exception as e:
                print(f"Unable to read PixelFormat.Symbolics: {e}")
            # Select new format
            idx = int(event)
            new_format = self.colormode[idx] if idx < len(self.colormode) else None

            if new_format is None:
                return
            if new_format in available_formats:
                camera.open()
                camera.set_parameter("PixelFormat", new_format)
                camera.initial_params["PixelFormat"] = new_format
                camera.close()
            # Change bits depth
            self.parent.variables['bits_depth'] = self.colormode_bits_depth[idx]
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            if 'Bayer' in new_format:
                self.bot_left.reinit_checkbox('RGB')
            elif 'Mono' in new_format:
                self.bot_left.reinit_checkbox('Gray')
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

    def handle_rect_changed(self, coords):
        """Action performed when a new rectangle has been drawn."""
        coords = [int(x) for x in coords]
        roi_coords = self.check_order(coords)
        if self.check_roi_range(roi_coords):
            self.parent.variables['roi_coords'] = roi_coords
            self.top_right.set_roi(self.parent.variables['roi_coords'])
        # Update Top_Right widget
        self.top_left.draw_rectangle(self.parent.variables['roi_coords'])

    def handle_roi_activated(self, value):
        self.parent.variables["roi_activated"] = value
        camera = self.parent.variables["camera"]
        self.stop_live()
        self.top_right.set_enabled_roi_widget(not value)
        self.top_left.set_enabled(not value)
        if value:
            x0, y0, x1, y1 = self.parent.variables["roi_coords"]
            new_w = min((x1-x0) + (4-(x1-x0)%4), camera.get_parameter('WidthMax'))
            new_h = min((y1-y0) + (4-(y1-y0)%4), camera.get_parameter('HeightMax'))
            x0, y0 = x0 - x0%4, y0 - y0%4
            x1 = x0 + new_w
            y1 = y0 + new_h
            self.parent.variables["roi_coords"] = [x0, y0, x1, y1]
        else:
            x0, y0, x1, y1 = self._get_max_coords()
            new_w = x1
            new_h = y1
            self.top_left.draw_rectangle(self.parent.variables["roi_coords"])
        self.top_right.set_roi([x0, y0, x1, y1])
        camera.set_parameter('Width', new_w)
        camera.set_parameter('Height', new_h)
        camera.set_parameter('OffsetX', x0)
        camera.set_parameter('OffsetY', y0)
        time.sleep(0.05)
        self.start_live()
        self.top_left.update()

    def check_order(self, coords: list):
        """
        Check coordinates order.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        x0, y0, x1, y1 = coords
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        coords = [x0, y0, x1, y1]
        return coords

    def check_roi_range(self, coords: list):
        """
        Check ROI range, if in the camera range.
        :param coords: ROI coordinates.
        """
        if (coords[0] < self.camera_range[0] or coords[2] > self.camera_range[2]
                or coords[1] < self.camera_range[1] or coords[3] > self.camera_range[3]):
            return False
        else:
            return True

    def handle_roi_centered(self, coords: list):
        """
        Recenter the ROI.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        new_coords = self.check_order(coords)
        new_w = new_coords[2] - new_coords[0]
        new_x0 = (self.camera_range[2] - self.camera_range[0]) // 2 - new_w // 2
        new_x1 = (self.camera_range[2] - self.camera_range[0]) // 2 + new_w // 2
        new_h = new_coords[3] - new_coords[1]
        new_y0 = (self.camera_range[3] - self.camera_range[1]) // 2 - new_h // 2
        new_y1 = (self.camera_range[3] - self.camera_range[1]) // 2 + new_h // 2
        if self.check_roi_range([new_x0, new_y0, new_x1, new_y1]):
            self.parent.variables["roi_coords"] = [new_x0, new_y0, new_x1, new_y1]
            self.top_right.set_roi(self.parent.variables["roi_coords"])
            self.top_left.draw_rectangle(self.parent.variables["roi_coords"])
        else:
            self.top_right.set_roi(self.parent.variables["roi_coords"])

    def handle_roi_reset(self):
        print("ROI Reset")
        camera = self.parent.variables["camera"]
        self.stop_live()
        x0, y0, x1, y1 = self._get_max_coords()
        self.parent.variables["roi_coords"] = [x0, y0, x1, y1]
        self.top_right.set_roi(self.parent.variables["roi_coords"])
        self.top_left.clear_rect()
        self.top_left.draw_rectangle(self.parent.variables["roi_coords"])
        self.start_live()

    def _get_max_coords(self):
        max_width = self.parent.xml_app.get_sub_parameter('camera', 'maxwidth')
        max_height = self.parent.xml_app.get_sub_parameter('camera', 'maxheight')
        offset = self.parent.xml_app.get_sub_parameter('camera', 'offset')
        x0, y0 = int(offset), int(offset)
        x1, y1 = int(max_width)+x0, int(max_height)+y0
        return x0, y0, x1, y1

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


