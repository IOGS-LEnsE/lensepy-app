# -*- coding: utf-8 -*-
"""*modes_manager.py* file.

./controllers/modes_manager.py contains ModesManager class to manage the different modes of the application.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from enum import Enum
from views.main_structure import MainView
from models.dataset import DataSetModel
from controllers.acquisition_controller import AcquisitionController
from controllers.images_controller import ImagesController
from controllers.masks_controller import MasksController
from controllers.analyses_controller import AnalysesController
from controllers.aberrations_controller import AberrationsController
from controllers.help_controller import HelpController
from controllers.treatment_controller import TreatmentController
from views.html_view import HTMLView
from lensepy.css import actived_button

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zygo_lab_app import ZygoApp
    from views.main_menu import MainMenu

from PyQt6.QtWidgets import QWidget

class ModesManager:
    """
    Main modes manager.
    The different modes are loaded from the main menu file (menu/menu.txt)
    """

    def __init__(self, main_app: "ZygoApp"):
        """
        Default constructor.
        :param menu: Main menu of the application (MainMenu).
        :param widget: Main widget container of the application (MainView).
        :param dataset: Dataset of the application (DataSetModel).
        """
        # Main App
        self.main_app: "ZygoApp" = main_app
        # Menu
        self.main_menu: "MainMenu" = self.main_app.main_menu
        self.main_menu.menu_changed.connect(self.update_mode)
        self.options_list = []
        # Main widget
        self.main_widget = self.main_app.main_widget
        # Data set
        self.data_set = self.main_app.data_set
        # Phase
        self.phase = self.main_app.phase
        # Modes
        self.main_mode = 'first'
        self.mode_controller = None
        # Hardware
        self.piezo_connected = False
        self.camera_connected = False

        self.first_treatment = True
        self.treatment_controller = None

        self.analyses_controller = None
        self.first_analysis = True

        # Main Help
        url = './docs/html/main.html'
        css = './docs/html/styles.css'
        self.main_widget.bot_right_widget = HTMLView(url=url, css=css)
        self.main_widget.set_bot_right_widget(self.main_widget.bot_right_widget)
        # If hardware, start in acquisition mode
        if self.data_set.acquisition_mode.is_camera():
            self.main_mode = 'acquisition'
            self.mode_controller = AcquisitionController(self)
            #self.main_menu.actual_button = self.main_menu.buttons_list[0]
        # First update
        self.update_menu()


    def update_menu(self):
        """

        :return:
        """
        print(f'State = {self.data_set.data_set_state.state}')
        if self.main_mode != 'first':
            nocam = 'nocam' in self.options_list
            nopiezo = 'nopiezo' in self.options_list

        self.options_list = []
        # Check Hardware
        if self.main_mode == 'first':
            if self.data_set.acquisition_mode.is_camera() is False:
                self.options_list.append('nocam')
            if self.data_set.acquisition_mode.is_piezo() is False:
                self.options_list.append('nopiezo')
            self.main_mode = ''
        else:
            # To avoid to check hardware each time
            if nocam:
                self.options_list.append('nocam')
            if nopiezo:
                self.options_list.append('nopiezo')

        # Check dataset
        if self.data_set.is_data_ready() is False:
            self.options_list.append('nodata')
        if self.data_set.images_sets.get_number_of_sets() == 0:
            self.options_list.append('noimages')
        if self.data_set.masks_sets.get_masks_number() == 0:
            self.options_list.append('nomask')
        if self.phase.is_analysis_ready() is False:
            self.options_list.append('noanalysis')
        # Update menu
        self.main_menu.update_options(self.options_list)
        self.main_menu.update_menu_display()

    def update_mode(self, event):
        """

        :return:
        """
        if self.main_mode == 'acquisition':
            self.mode_controller.stop_acquisition()
        self.main_mode = event
        self.main_widget.clear_all()
        self.update_menu()
        match self.main_mode:
            case 'acquisition':
                self.mode_controller = AcquisitionController(self)
                self.first_treatment = True
                self.first_analysis = True
            case 'images':
                self.mode_controller = ImagesController(self)
                self.first_treatment = True
                self.first_analysis = True
            case 'masks':
                self.mode_controller = MasksController(self)
                self.first_treatment = True
                self.first_analysis = True
            case 'analyses':
                """if self.first_analysis or self.analyses_controller is None:
                    self.analyses_controller = AnalysesController(self)
                    self.first_analysis = False"""
                self.mode_controller = AnalysesController(self)
            case 'aberrations':
                self.mode_controller = AberrationsController(self)
            case 'help':
                self.mode_controller = HelpController(self)
            case 'postprocess':
                """if self.first_treatment:
                    self.treatment_controller = TreatmentController(self)
                    self.first_treatment = False"""
                self.mode_controller = TreatmentController(self)