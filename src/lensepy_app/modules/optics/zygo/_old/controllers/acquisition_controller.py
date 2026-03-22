# -*- coding: utf-8 -*-
"""*acquisition_controller.py* file.

./controllers/acquisition_controller.py contains AcquisitionController class
to manage "acquisition" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views import *
from lensepy import load_dictionary, translate, dictionary
from lensepy.pyqt6.widget_xy_chart import XYChartWidget
from lensepy.css import *
from lensepy.pyqt6.widget_image_histogram import ImageHistogramWidget
from PyQt6.QtWidgets import QWidget
from views.main_structure import MainView
from views.main_structure import RIGHT_WIDTH, LEFT_WIDTH, TOP_HEIGHT, BOT_HEIGHT
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.camera_options_view import CameraOptionsView
from views.piezo_options_view import PiezoOptionsView
from views.simple_acquisition_view import SimpleAcquisitionView
from models.dataset import DataSetModel
from utils.dataset_utils import DataSetState, generate_images_grid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from zygo_lab_app import ZygoApp


class AcquisitionController:
    """
    Acquisition mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager: "ModesManager" = manager
        self.main_widget: MainView = self.manager.main_widget
        self.data_set: DataSetModel = self.manager.data_set
        self.main_app: "ZygoApp" = self.manager.main_app
        self.submode = ''
        self.histo_here = False  # To allow good synchronisation for histogram display
        self.acquiring = False
        self.thread = None
        self.slice_ok = False
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()  # Display first image of a set
        self.top_right_widget = QWidget()  # Histogram or image display, depending on submode
        self.bot_right_widget = HTMLView()  # HTML Help on masks
        # Submenu
        self.submenu = SubMenu(translate('submenu_acquisition'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/acquisition_menu.txt')
        else:
            self.submenu.load_menu('menu/acquisition_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        self.options1_widget = QWidget()  # ??
        # Option 2
        self.options2_widget = QWidget()  # ??
        # Update menu and view
        self.update_submenu_view("")
        self.init_view()
        self.data_set.acquisition_mode.set_default_parameters(self.main_app.default_parameters)
        # Start acquisition
        self.start_acquisition()

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.clear_all()
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/acquisition.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/acquisition.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)


    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.submode = submode
        self.manager.update_menu()
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, True)
        ## Activate button depending on data
        match self.submode:
            case 'camera_acquisition':
                self.submenu.set_activated(1)
            case 'piezo_acquisition':
                self.submenu.set_activated(2)
            case 'simple_acquisition':
                self.submenu.set_activated(4)
            case 'multi_acquisition':
                self.submenu.set_activated(5)
        # Update views
        #self.main_widget.clear_top_left()  # Image from camera
        self.main_widget.clear_top_right()
        self.main_widget.clear_bot_right()
        self.main_widget.clear_options()
        # For all submodes

        # Specific submodes
        match self.submode:
            case 'camera_acquisition':
                self.top_right_widget = ImageHistogramWidget(name=translate('histo_camera'),
                                                             info=True)
                self.top_right_widget.set_background('white')
                self.top_right_widget.set_bit_depth(8)  # Mono8 on the camera#
                # self.top_right_widget.set_axis_labels(translate('x_label_histo'), translate('y_label_histo'))
                self.main_widget.set_top_right_widget(self.top_right_widget)
                self.set_slice_view()
                # Display camera exposure time in options
                self.options1_widget = CameraOptionsView(self)
                self.main_widget.set_options_widget(self.options1_widget)
                self.options1_widget.settings_changed.connect(self.params_changed)

            case 'piezo_acquisition':
                self.options1_widget = PiezoOptionsView(self)
                self.main_widget.set_options_widget(self.options1_widget)
                self.options1_widget.voltage_changed.connect(self.params_changed)
                self.set_slice_view()

            case 'simple_acquisition':
                self.top_right_widget = ImagesDisplayView()
                self.main_widget.set_top_right_widget(self.top_right_widget)
                self.options1_widget = SimpleAcquisitionView(self)
                self.main_widget.set_options_widget(self.options1_widget)
                self.options1_widget.acquisition_end.connect(self.acquisition_update)
                self.set_html_view()

            case 'multi_acquisition':
                self.set_html_view()
                pass


    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'camera_acquisition':
                self.start_acquisition()
                self.histo_here = True

            case 'piezo_acquisition':
                self.start_acquisition()
                self.histo_here = False

            case 'simple_acquisition':
                self.stop_acquisition()
                self.options1_widget.update_view()
                self.histo_here = False

            case 'multi_acquisition':
                self.stop_acquisition()
                self.histo_here = False

    def thread_update_image(self):
        """
        Thread for updating image displaying (and other options).
        """
        try:
            if self.acquiring is False:
                self.start_acquisition()
            # Get image
            if self.data_set.acquisition_mode.is_camera():
                image = self.data_set.acquisition_mode.get_image()
            else:
                ## Random Image
                width, height = 256, 256
                image = np.random.randint(0, 256, (height, width), dtype=np.uint8)
            self.top_left_widget.set_image_from_array(image)
            # Test zoom displaying
            if isinstance(self.options1_widget, CameraOptionsView):
                if not self.options1_widget.zoom_activated:
                    # Display image in top left area
                    self.top_left_widget.set_image_from_array(image)
                else:
                    self.options1_widget.zoom_window.set_image_from_array(image)
            else:
                self.top_left_widget.set_image_from_array(image)
            # Update histogram in camera mode
            if self.submode == 'camera_acquisition':
                if self.histo_here and not self.options1_widget.zoom_activated:
                    self.top_right_widget.set_image(image.squeeze())
                self.update_slice(image)
            elif self.submode == 'piezo_acquisition':
                self.update_slice(image)

            if self.acquiring:
                self.thread = threading.Thread(target=self.thread_update_image)
                self.thread.start()
        except Exception as e:
            print(f'thread_image / acquisition mode / {e}')

    def stop_acquisition(self):
        """
        Stop timed thread for updating images.
        """
        self.acquiring = False
        self.thread.join()
        self.data_set.acquisition_mode.camera.stop_acquisition()

    def start_acquisition(self):
        """
        Stop timed thread for updating images.
        """
        if self.acquiring is False:
            self.acquiring = True
            self.data_set.acquisition_mode.camera.start_acquisition()
            self.thread = threading.Thread(target=self.thread_update_image)
            self.thread.start()

    def acquisition_update(self, event):
        """
        Update step in acquisition process.
        """
        if event == 'acq_end':
            self.data_set.acquisition_mode.thread.join()
            # Display grid of images in top right area.
            time.sleep(0.1)
            nb_of_set = self.data_set.acquisition_mode.get_number_of_acquisition()
            for i in range(nb_of_set):
                images = self.data_set.acquisition_mode.get_images_set(i+1)
                self.data_set.add_set_images(images)
            images = self.data_set.get_images_sets(1)
            g_images = generate_images_grid(images)
            self.top_right_widget.set_image_from_array(g_images)
            if 'nodata' in self.manager.options_list:
                self.manager.options_list.remove('nodata')
            self.manager.update_menu()
            #self.update_submenu('')

    def params_changed(self, event):
        """
        Open a new window if zoom is activated.
        :param event:
        """
        if event == 'zoom':
            pass
        if event == 'voltage':
            volt = self.options1_widget.get_voltage()
            self.data_set.acquisition_mode.piezo.write_dac(volt)

    def __del__(self):
        if self.acquiring:
            self.stop_acquisition()
            #self.data_set.acquisition_mode.camera.disconnect()
            self.data_set.acquisition_mode.camera.destroy_camera()

    def update_slice(self, image, row = None):
        if self.slice_ok:
            if row is None:
                row = len(image) // 2
            image_slice = image[row][:].squeeze()
            image_row = np.linspace(0, len(image[0])-1, len(image[0]))
            self.bot_right_widget.set_data(image_row, image_slice)
            self.bot_right_widget.refresh_chart()


    def set_slice_view(self):
        self.bot_right_widget = XYChartWidget()
        self.bot_right_widget.set_background("white")
        self.bot_right_widget.set_title("Horizontal slice of the image (brightness 0-255 per pixel)")
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.slice_ok = True

    def set_html_view(self):
        self.bot_right_widget = HTMLView()  # HTML Help on masks
        self.main_widget.set_bot_right_widget(self.bot_right_widget)


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    m_app.mode_manager.mode_controller = AcquisitionController(m_app.mode_manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())

