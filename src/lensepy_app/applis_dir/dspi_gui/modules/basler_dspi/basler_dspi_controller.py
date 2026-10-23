from lensepy import translate
from lensepy_app import *
from lensepy_app.appli import *
from lensepy_app.appli._app.template_controller import *
from lensepy_app.widgets import RectangleDisplayWidget, HistogramWidget

from .basler_dspi_views import *
from .basler_dspi_models import *
from modules.camera_dspi_widget import *


class BaslerDSPIController(TemplateController):
    """
    Controller for Camera Acquisition
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.camera_connected = False       # Camera is connected
        self.thread = None                  # Thread to run parallel tasks (image grabbing)
        self.worker = None                  # Worker to run on the parallel thread
        self.colormode = []
        self.colormode_bits_depth = []
        self.camera_range = [0, 0, 0, 0]
        # Widgets
        self.top_left = RectangleDisplayWidget(parent=self)    # Widget where the image is displayed
        self.bot_left = HistogramWidget(parent=self)           # Widget where the histogram of the image is displayed
        self.top_right = CameraInfosWidget(parent=self)    # Widget with camera infos and ROI selection buttons
        self.bot_right = CameraParamsWidget(parent=self)   # Widget used to change parameters of the camera
        self.fft_window = None  # Window where the Fourier Transform of an image is displayed
        self.do_fft = False  # Boolean used to initiate fft processing
        self.autocorr_window = None  # Window where the Fourier Transform of an image is displayed
        self.do_autocorr = False  # Boolean used to initiate fft processing

        # Check if camera is connected
        self.init_camera()
        x0, y0, x1, y1 = self.camera_range
        self.top_right.set_roi([x0, y0, x1, y1])
        # Camera infos
        camera = self.get_variables("camera")
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)
            self.bot_right.slider_expo.slider.setEnabled(True)
            self.bot_right.slider_black_level.slider.setEnabled(True)
        if self.get_variables('roi_coords') is not None:
            self.top_right.set_roi(self.get_variables('roi_coords'))
            self.top_left.draw_rectangle(self.get_variables('roi_coords'))

    def init_view(self):
        """
        Update graphical objects of the interface.
        """
        # Update view
        if self.get_variables("camera") is None:
            super().init_view()
            self.set_color_mode()
            self.set_max_exposure_time()
            self.top_right.label_color_mode.set_values(self.colormode)
            self.update_color_mode()
            # Setup widgets
            self.bot_left.set_background('white')
            self.bot_left.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))
            self.top_left.set_enabled(True)
            self.top_right.update_infos()
            # Init widgets
            if self.get_variables('bits_depth') is not None:
                self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
                self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            else:
                self.bot_left.set_bits_depth(8)
            if self.get_variables('image') is not None:
                self.top_left.set_image_from_array(self.get_variables('image'))
                self.bot_left.set_image(self.get_variables('image'))
            self.bot_left.refresh_chart()
            # Signals
            self.top_left.rectangle_changed.connect(self.handle_rect_changed)
            self.top_right.roi_changed.connect(self.handle_rect_changed)
            self.top_right.roi_centered.connect(self.handle_roi_centered)
            self.top_right.roi_reset.connect(self.handle_roi_reset)
            self.top_right.roi_activated.connect(self.handle_roi_activated)
            self.top_right.open_fft.connect(self.handle_open_fft)
            self.top_right.open_autocorr.connect(self.handle_open_autocorr)
            self.bot_right.exposure_time_changed.connect(self.handle_exposure_time_changed)
            self.bot_right.black_level_changed.connect(self.handle_black_level_changed)
            self.start_live()
        else:
            self.top_left = QLabel('No Camera is connected. \n'
                                   'Connect a camera first.\n'
                                   'Then restart the application.')
            theme = self.get_config('global_theme')
            mode = self.get_config('global_mode')
            self.top_left.setStyleSheet(STYLE_H2[theme][mode])
            self.bot_left = QWidget()
            self.top_right = QWidget()
            self.bot_right = QWidget()
            super().init_view()

    def init_camera(self):
        """
        Initialize the camera.
        """
        camera = self.get_variables("camera")
        # Check if a camera is already connected
        if camera is None:
            # Init Camera
            self.set_variables("camera", BaslerDSPICamera())
            self.camera_connected = self.get_variables("camera").find_first_camera()
            if self.camera_connected is False:
                self.set_variables("camera", None)
            else:
                camera = self.get_variables("camera")
                self.set_variables("first_connexion", 'Yes')
                # Initial parameters
                camera_ini_file = self.manager.get_config('camera_ini')
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
        """
        Get possible color mode list
        """
        colormode_get = self.manager.xml_app.get_sub_parameter('camera','colormode')
        colormode_get = colormode_get.split(',')
        for colormode in colormode_get:
            colormode_v = colormode.split(':')
            self.colormode.append(colormode_v[0])
            self.colormode_bits_depth.append(int(colormode_v[1]))

    def set_max_exposure_time(self):
        exposuretime_get = self.manager.xml_app.get_sub_parameter('camera', 'exposuretime')
        self.bot_right.set_max_exposure_time(exposuretime_get)

    def update_color_mode(self):
        camera = self.get_variables("camera")
        if camera is None:
            return
        # Update to first mode if first connection
        pix_format = camera.get_parameter('PixelFormat')
        if 'first_connexion' in self.parent.variables:
            if self.get_variables('first_connexion') == 'Yes':
                first_mode_color = self.colormode[0]
                camera.open()
                camera.set_parameter("PixelFormat", first_mode_color)
                camera.initial_params["PixelFormat"] = first_mode_color
                camera.close()
                first_bits_depth = self.colormode_bits_depth[0]
                self.set_variables("bits_depth", first_bits_depth)
            else:
                idx = self.colormode.index(pix_format)
                self.top_right.label_color_mode.set_choice(idx)
                new_bits_depth = self.colormode_bits_depth[idx]
                self.set_variables("bits_depth", new_bits_depth)
            black_level = camera.get_parameter('BlackLevel')
            self.bot_right.set_black_level(black_level)

    def start_live(self):
        """
        Start live acquisition from camera.
        """
        if self.camera_connected:
            self.thread = QThread()
            self.worker = ImageLive(self)
            self.worker.moveToThread(self.thread)   # Worker associated to the thread

            self.thread.started.connect(self.worker.run)    # Worker runs while the thread is active
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
            self.worker.stop()

            # Wait for the end of the thread
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # Blocks until the end

            # Delete the references
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image (to be displayed).
        """
        # Update Image
        self.top_left.set_image_from_array(image)
        # Update FFT
        if self.do_fft:
            # Computation of the Fourier Transform
            m = cv2.mean(image.astype(np.uint8))
            x0, y0, x1, y1 = self.parent.variables["roi_coords"]
            processed = image - m[0] * np.ones((abs(y1-y0), abs(x1-x0)), dtype=np.uint8)    # Subtracts the mean value of the image

            dft = cv2.dft(processed, flags=cv2.DFT_COMPLEX_OUTPUT)      # Discrete FT (returns real and imaginary parts in an 3D array)
            dft_shift = np.fft.fftshift(dft)
            fft_amplitude = np.sqrt(dft_shift[:, :, 0] ** 2 + dft_shift[:, :, 1] ** 2)

            fft_data = np.log(fft_amplitude + 1)    # log scale

            fft_display = cv2.normalize(fft_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            # Display the result
            self.fft_window.fft_widget.set_image_from_array(fft_display)
            self.do_fft = False
        # Update Autocorrelation - TF-1(TF(Intensité)*Conj(TF(Intensité))
        if self.do_autocorr:
            image = image.astype(np.uint8)
            # Autocorrelation :
            auto_corr = np.correlate(image.astype(np.uint8), image.astype(np.uint8),
                                     mode='same')
            # OR ?
            tf_image = np.fft.fft2(image)
            tf_image_conj = np.conjugate(tf_image)
            tf_mult = tf_image * tf_image_conj
            # Display the result
            self.autocorr_window.fft_widget.set_image_from_array(auto_corr)
            self.do_autocorr = False

        # Update Histo
        self.bot_left.set_image(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_open_fft(self):
        """
        Action performed when the FFT button is triggered
        """
        camera = self.get_variables("camera")
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Open FFT Window
            self.fft_window = FFTWindow(self)   # Class defined in basler_dspi_views
            self.fft_window.close_fft.connect(self.handle_close_fft)
            self.fft_window.show()
            self.do_fft = True
            # Restart live
            camera.open()
            self.start_live()

    def handle_close_fft(self):
        """
        Action performed when the button to close the FFT window is triggered
        """
        camera = self.get_variables("camera")
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Close FFT Window
            self.fft_window.fft_widget = None
            self.fft_window.close()
            self.fft_window = None
            self.do_fft = False
            # Restart live
            camera.open()
            self.start_live()

    def handle_open_autocorr(self):
        """
        Action performed when the Autocorrelation button is triggered
        """
        print(f'Autocorrelation')
        camera = self.get_variables("camera")
        if camera is not None:
            '''
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            '''
            # Open Autocorrelation Window
            self.autocorr_window = AutoCorrWindow(self)   # Class defined in basler_dspi_views
            self.autocorr_window.close_autocorr.connect(self.handle_close_autocorr)
            self.autocorr_window.show()
            self.do_autocorr = True
            '''
            # Restart live
            camera.open()
            self.start_live()
        '''

    def handle_close_autocorr(self):
        """
        Action performed when the button to close the FFT window is triggered
        """
        camera = self.get_variables("camera")
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Close FFT Window
            self.autocorr_window.fft_widget = None
            self.autocorr_window.close()
            self.autocorr_window = None
            self.do_autocorr = False
            # Restart live
            camera.open()
            self.start_live()

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
        """
        Action performed when a new rectangle has been drawn
        """
        coords = [int(x) for x in coords]
        roi_coords = self.check_order(coords)
        if self.check_roi_range(roi_coords):
            self.parent.variables['roi_coords'] = roi_coords
            self.top_right.set_roi(self.parent.variables['roi_coords'])
        # Update Top_Right widget
        self.top_left.draw_rectangle(self.parent.variables['roi_coords'])

    def handle_roi_activated(self, value):
        """
        Action performed when the button to select a ROI has been triggered
        """
        self.parent.variables["roi_activated"] = value
        camera = self.parent.variables["camera"]
        # Stop live safely
        self.stop_live()
        self.top_right.set_enabled_roi_widget(not value)
        self.top_left.set_enabled(not value)
        if value:
            # Creation of the new ROI
            x0, y0, x1, y1 = self.parent.variables["roi_coords"]
            new_w = min((x1-x0) + (32-(x1-x0)%32), camera.get_parameter('WidthMax'))
            new_h = min((y1-y0) + (4-(y1-y0)%4), camera.get_parameter('HeightMax'))
            x0, y0 = x0 - x0%32, y0 - y0%4
            x1 = x0 + new_w
            y1 = y0 + new_h
            self.parent.variables["roi_coords"] = [x0, y0, x1, y1]
        else:
            x0, y0, x1, y1 = self._get_max_coords()
            new_w = x1
            new_h = y1
            self.top_left.draw_rectangle(self.parent.variables["roi_coords"])
        # Activation of the new ROI
        self.top_right.set_roi([x0, y0, x1, y1])
        camera.set_parameter('Width', new_w)
        camera.set_parameter('Height', new_h)
        camera.set_parameter('OffsetX', x0)
        camera.set_parameter('OffsetY', y0)
        time.sleep(0.05)
        # Restart live
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
        """
        Come back to the full image recorded by the camera
        """
        print("ROI Reset")
        self.stop_live()
        x0, y0, x1, y1 = self._get_max_coords()
        self.parent.variables["roi_coords"] = [x0, y0, x1, y1]
        self.top_right.set_roi(self.parent.variables["roi_coords"])
        self.top_left.clear_rect()
        self.top_left.draw_rectangle(self.parent.variables["roi_coords"])
        self.start_live()

    def _get_max_coords(self):
        """
        Access to the dimensions of the camera
        """
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
        if self.fft_window is not None:
             self.handle_close_fft()
        if self.autocorr_window is not None:
             self.handle_close_autocorr()
        camera = self.get_variables("camera")
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False
        self.worker = None
        self.thread = None



