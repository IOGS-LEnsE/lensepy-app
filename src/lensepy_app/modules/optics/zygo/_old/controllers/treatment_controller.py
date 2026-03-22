# -*- coding: utf-8 -*-
"""*analyses_controller.py* file.

./controllers/analyses_controller.py contains AnalysesController class to manage "analyses" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
import numpy as np
from matplotlib import pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.surface_2D_view import Surface2DView
from views.bar_graph_view import BarGraphView
from lensepy import load_dictionary, translate, dictionary
from models.phase import process_statistics_surface
from views.aberrations_options_view import AberrationsOptionsView
from views.aberrations_start_view import AberrationsStartView
from views.aberrations_choice_view import AberrationsChoiceView
from views.table_view import TableView
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget
)
from PyQt6.QtCore import QTimer
from models.zernike_coefficients import Zernike, aberrations_type, aberrations_list
from models.fourier_manager import FourierManager
from utils.dataset_utils import generate_images_grid, DataSetState
from views.treatment_view import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel
from lensepy.images.conversion import resize_image_ratio, resize_image

class TreatmentController:
    """
    Analyses mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.manager: "ModesManager" = manager
        self.data_set: DataSetModel = self.manager.data_set
        self.phase: "PhaseModel"= self.manager.phase
        self.zernike_coeffs: Zernike = Zernike(self.phase)
        self.main_widget: MainView = self.manager.main_widget
        self.sub_mode = ''
        self.corrected_initial_list = ['piston','tilt']

        self.masks_loaded = self.data_set.get_global_mask()
        """plt.figure()
        plt.imshow(self.masks_loaded)
        plt.show()"""
        self.lambda_check = False
        self.lambda_value = 632.8
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)

        # Graphical elements
        self.top_left_widget = QWidget()
        self.top_right_widget = Surface2DView('Unwrapped Phase')
        self.bot_right_widget = HTMLView()
        self.lambda_check = False
        self.lambda_value = 632.8
        self.defocus = False
        # Submenu
        self.submenu = SubMenu(translate('submenu_postprocess'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/postprocess_menu.txt')
        else:
            self.submenu.load_menu('menu/postprocess_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)

        # Option 1
        self.options1_widget = QWidget()
        # Option 2
        self.options2_widget = QWidget()        # ??

        # Update menu and view
        self.init_view()

        ### Secondary window displays
        self.fourier = FourierManager()
        self.image = self.phase.get_unwrapped_phase()
        size = self.image.shape

        """x_pad = 800 - size[0] * (800 >= size[0])
        y_pad = 800 - size[1] * (800 >= size[1])
        pad_width = ((x_pad//2 + 1, x_pad//2), (y_pad//2 + 1, y_pad//2))"""

        self.fourier.rpupil = 75
        self.image = resize_image(self.image, 800, 800)
        #self.image = np.pad(self.image, pad_width, mode='constant', constant_values=0)
        self.size = self.image.shape

        self.reserve_coefficients = self.zernike_coeffs.get_coeffs()
        self.reserve_coefficients[0] = 0
        self.reserve_coefficients[1] = 0
        self.reserve_coefficients[2] = 0

        self.coefficients = self.reserve_coefficients.copy()

        self.fourier.center = [self.size[0] // 2, self.size[1] // 2]

        self.rf, self.psf_diff_lim, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
        #self.rf, self.psf_diff_lim, self.psf_image = self.fourier.find_rf_from_image(np.exp(1j*self.image).astype(np.complex128))
        self.mtf_image = self.fourier.MTF_from_PSF(self.psf_image)
        self.mtf_diff = self.fourier.MTF_from_PSF(self.psf_diff_lim)

        self.airy_view = AiryView(self)
        self.psf_view = QWidget()
        self.mtf_view = QWidget()
        self.focal_view = QWidget()

        ###

        self.options1_widget = TreatmentOption1Widget(self)
        self.options1_widget.update_treatment_progress_bar(0)
        self.main_widget.set_options1_widget(self.options1_widget)
        self.options1_widget.checkBoxSignal.connect(self.enhance_coeffs_action)
        self.options1_widget.buttonsSignal.connect(self.further_actions)

        self.fourier.scanProgress.connect(self.scan_progress_action)

    def enhance_coeffs_action(self, event):
        #print(event)
        if event:
            self.coefficients = 10 * self.reserve_coefficients.copy()
        else:
            self.coefficients = self.reserve_coefficients.copy()

        self.rf, self.psf_diff_lim, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
        self.mtf_image = self.fourier.MTF_from_PSF(self.psf_image)
        self.mtf_diff = self.fourier.MTF_from_PSF(self.psf_diff_lim)
        self.Initialize()
        QApplication.processEvents()

    def further_actions(self, event):
        self.close_all()

    def Initialize(self):
        self.close_all()
        self.airy_view = AiryView(self)
        self.psf_view = QWidget()
        self.mtf_view = QWidget()
        self.focal_view = QWidget()
        self.options1_widget.opened = 0
        self.options1_widget.update_treatment_progress_bar(0)

    def scan_progress_action(self, event):
        self.options1_widget.update_treatment_progress_bar(int(event))

    def close_all(self):
        self.psf_view.close()
        self.airy_view.close()
        self.mtf_view.close()
        self.focal_view.close()
        self.options1_widget.close()

    def calculate_psf_from_coefs(self, coefficients, size):
        _, psf_diff_lim, psf_image = self.fourier.find_rf_from_coefs(coefficients, size)
        return psf_diff_lim, psf_image

    def calculate_psf_from_image(self, phase_map):
        _, psf_diff_lim, psf_image = self.fourier.find_rf_from_image(phase_map)
        return psf_diff_lim.astype(np.uint8), psf_image.astype(np.uint8)

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)
        self.display_2D_corrected_phase()

        # Process Zernike coefficients
        for k in range(self.zernike_coeffs.max_order + 1):
            self.zernike_coeffs.process_zernike_coefficient(k)

        self.display_bar_graph_coeff()


    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        self.submode = submode
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()

        # Update views
        #self.main_widget.clear_bot_right()
        #self.main_widget.clear_options()
        # For all submodes
        #self.display_bar_graph_coeff()

        self.bot_right_widget = HTMLView()
        url = 'docs/html/FR/process.html'
        css = 'docs/html/styles.css'
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../' + url, '../' + css)
        else:
            self.bot_right_widget.set_url(url, css)
        self.main_widget.set_bot_right_widget(self.bot_right_widget)

        # Specific submodes
        match self.submode:
            case 'psf_process':
                self.close_all()
                if not isinstance(self.psf_view, PSFView):
                    self.submenu.disable_buttons()
                    self.options1_widget.enhance_coeffs.setEnabled(False)
                    QApplication.processEvents()
                    self.psf_view = PSFView(self)
                    self.options1_widget.enhance_coeffs.setEnabled(True)
                self.psf_view.show()
            case 'airy_process':
                self.close_all()
                if not isinstance(self.airy_view, AiryView):
                    self.submenu.disable_buttons()
                    self.options1_widget.enhance_coeffs.setEnabled(False)
                    QApplication.processEvents()
                    self.airy_view = AiryView(self)
                    self.options1_widget.enhance_coeffs.setEnabled(True)
                self.airy_view.show()
            case 'mtf_process':
                self.close_all()
                if not isinstance(self.mtf_view, MTFView):
                    self.submenu.disable_buttons()
                    self.options1_widget.enhance_coeffs.setEnabled(False)
                    QApplication.processEvents()
                    self.mtf_view = MTFView(self)
                    self.options1_widget.enhance_coeffs.setEnabled(True)
                self.mtf_view.show()
            case 'focal_process':
                self.close_all()
                if not isinstance(self.focal_view, FocalView):
                    self.submenu.disable_buttons()
                    self.options1_widget.enhance_coeffs.setEnabled(False)
                    QApplication.processEvents()
                    self.focal_view = FocalView(self)
                    self.options1_widget.enhance_coeffs.setEnabled(True)
                self.focal_view.show()


    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """

        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'psf_process':
                pass


    def display_bar_graph_coeff(self, disp_correct: bool = False, first: bool = False):
        """
        Display the Zernike coefficients in a bargraph, in the top left area.
        :param disp_correct: True if all the coefficients must be displayed.
        :param first: True if only the first coefficients (piston, tilt and defocus) must be set to 0.
        """
        self.main_widget.clear_top_left()
        # Create bargraph
        self.top_left_widget = BarGraphView()
        self.main_widget.set_top_left_widget(self.top_left_widget)
        # Labels
        x_axis_label = translate('coeff_noll_index')
        if self.lambda_check:
            unit = ' (um)'
        else:
            unit = ' (\u03BB)'
        y_axis_label = translate('coeff_y_axis_label') + unit
        # Data
        max_order = self.zernike_coeffs.max_order
        x_axis = np.arange(max_order + 1)
        coeffs_disp = self.zernike_coeffs.get_coeffs().copy()

        self.update_color_aberrations()
        # Force to 0 corrected coefficients
        for jj, aberration in enumerate(self.corrected_initial_list):
            for k in aberrations_type[aberration]:
                coeffs_disp[k] = 0
        y_axis = np.array(coeffs_disp)
        self.top_left_widget.set_data(x_axis, y_axis, color_x=self.colors)
        self.top_left_widget.set_labels(x_axis_label, y_axis_label)


    def display_2D_corrected_phase(self):
        """
        Display tilt and piston corrected phase in the top right corner.
        """
        self.main_widget.clear_top_right()
        # Display wrapped in 2D
        self.top_right_widget = Surface2DView(translate('ab_corrected_phase'))
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Correction of the phase with tilt and piston
        wedge_factor = self.phase.get_wedge_factor()
        correction_list = self.corrected_initial_list
        _, corrected = self.zernike_coeffs.process_surface_correction(correction_list)
        unwrapped_array = -corrected * wedge_factor
        if self.lambda_check:
            unwrapped_array = unwrapped_array * self.lambda_value * 1e-9 * 1e6
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.top_right_widget.set_array(unwrapped_array)

    def update_color_aberrations(self):
        """
        Return a list of color to apply on Zernike bar graph.
        Orange : corrected value, blue : order 1, ...
        """
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)
        #
        for k, ab_type in enumerate(aberrations_list):
            if '3' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#0f4d7a'
            elif '5' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1567a5'
            elif '7' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1a82cf'
            elif '9' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1f9cfa'
            else:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#051725'

        for jj, aberration in enumerate(self.corrected_initial_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        if self.colors[k] is None:
            self.colors[k] = BLUE_IOGS


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    data_set = DataSetModel()
    m_app.data_set = data_set
    m_app.phase = PhaseModel(m_app.data_set)
    m_app.main_widget = MainView()
    m_app.main_menu = MainMenu()
    m_app.main_menu.load_menu('')
    manager = ModesManager(m_app)
    # Update data
    manager.data_set.load_images_set_from_file("../_data/test4.mat")
    manager.data_set.load_mask_from_file("../_data/test4.mat")
    manager.phase.prepare_data()
    manager.phase.process_wrapped_phase()
    manager.phase.process_unwrapped_phase()

    # Test controller
    manager.mode_controller = TreatmentController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())
