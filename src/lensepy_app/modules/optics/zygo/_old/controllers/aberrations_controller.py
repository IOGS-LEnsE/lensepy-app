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
from models.zernike_coefficients import Zernike, aberrations_type, aberrations_list
from utils.dataset_utils import generate_images_grid, DataSetState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

class AberrationsController:
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
        #
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.data_set.get_masks_list()) >= 1)
        self.sub_mode = ''
        self.corrected_aberrations_list = []
        self.corrected_initial_list = ['piston','tilt']
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)
        self.correct_disp = False
        self.correct_first = False
        self.lambda_check = False
        self.lambda_value = 632.8
        self.defocus = False
        # Graphical elements
        self.top_left_widget = QWidget()        # ??
        self.top_right_widget = Surface2DView('Unwrapped Phase')        # ??
        self.bot_right_widget = HTMLView()             # HTML Help on analyses ?
        # Submenu
        self.submenu = SubMenu(translate('submenu_aberrations'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/aberrations_menu.txt')
        else:
            self.submenu.load_menu('menu/aberrations_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        self.options1_widget = AberrationsStartView(self)        # ??
        # Option 2
        self.options2_widget = QWidget()        # ??

        # Update menu and view
        self.update_submenu_view("")
        self.init_view()


    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)

        ## Test 2D or 3D ??
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display wrapped in 2D
        self.top_right_widget.set_array(unwrapped_array)

        # Process Zernike coefficients
        for k in range(self.zernike_coeffs.max_order + 1):
            self.zernike_coeffs.process_zernike_coefficient(k)
            val_progression = int((k + 1) * 100 / self.zernike_coeffs.max_order)
            self.options1_widget.update_progress_bar(val_progression)
            self.submenu.set_button_enabled(1, True)
            self.submenu.set_button_enabled(2, True)
            self.submenu.set_button_enabled(4, True)

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        self.submode = submode
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        # Activate submenu
        match self.submode:
            case '':
                for k in range(len(self.submenu.buttons_list)):
                    self.submenu.set_button_enabled(k + 1, False)
            case 'Zernikecoefficients_aberrations':
                self.submenu.set_activated(1)
            case 'Seidelcoefficients_aberrations':
                self.submenu.set_activated(2)
            case 'coefficientscorrection_aberrations':
                self.submenu.set_activated(4)
        # Update views
        self.main_widget.clear_bot_right()
        self.main_widget.clear_options()
        # For all submodes

        # Specific submodes
        match self.submode:
            case 'Zernikecoefficients_aberrations':
                self.options1_widget = AberrationsOptionsView()
                self.options1_widget.set_checkboxes(self.correct_disp,
                                                    self.correct_first, self.lambda_check)
                self.main_widget.set_options1_widget(self.options1_widget)
                self.display_2D_ab_init(defocus=self.defocus)
                self.display_bar_graph_coeff()
                self.display_zernike_table()

            case 'Seidelcoefficients_aberrations':
                self.options1_widget = AberrationsOptionsView()
                self.options1_widget.set_checkboxes(self.correct_disp,
                                                    self.correct_first, self.lambda_check)
                self.main_widget.set_options1_widget(self.options1_widget)
                self.display_2D_ab_init(defocus=self.defocus)
                self.bot_right_widget = TableView(5, 4)
                self.main_widget.set_bot_right_widget(self.bot_right_widget)

            case 'coefficientscorrection_aberrations':
                self.options1_widget = AberrationsOptionsView()
                self.options1_widget.set_checkboxes(self.correct_disp,
                                                    self.correct_first, self.lambda_check)
                self.main_widget.set_options1_widget(self.options1_widget)

                self.options2_widget = AberrationsChoiceView()
                self.main_widget.set_options2_widget(self.options2_widget)

            case _:
                self.bot_right_widget = HTMLView()
                url = 'docs/html/FR/aberrations.html'
                css = 'docs/html/styles.css'
                if __name__ == "__main__":
                    self.bot_right_widget.set_url('../' + url, '../' + css)
                else:
                    self.bot_right_widget.set_url(url, css)
                self.main_widget.set_bot_right_widget(self.bot_right_widget)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'Zernikecoefficients_aberrations':
                self.options1_widget.set_wedge(self.phase.get_wedge_factor())
                self.options1_widget.aberrations_changed.connect(self.aberration_changed)

            case 'Seidelcoefficients_aberrations':
                self.options1_widget.set_wedge(self.phase.get_wedge_factor())
                self.options1_widget.aberrations_changed.connect(self.aberration_changed)

            case 'coefficientscorrection_aberrations':
                self.options1_widget.set_wedge(self.phase.get_wedge_factor())
                self.options1_widget.aberrations_changed.connect(self.aberration_changed)

            case 'aberrationsanalyses_aberrations':
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
        if first:
            for jj, aberration in enumerate(self.corrected_initial_list):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0
        if disp_correct:
            for jj, aberration in enumerate(self.corrected_aberrations_list):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0
        y_axis = np.array(coeffs_disp)
        self.top_left_widget.set_data(x_axis, y_axis, color_x=self.colors)
        self.top_left_widget.set_labels(x_axis_label, y_axis_label)

    def display_2D_ab_init(self, defocus: bool = False):
        """
        Display tilt and piston corrected phase in the top right corner.
        :param defocus: If defocus aberration has to be corrected on display.
        """
        self.main_widget.clear_top_right()
        # Display wrapped in 2D
        self.top_right_widget = Surface2DView(translate('initial_corrected_phase'))
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Correction of the phase with tilt and piston
        # Check if defocus has to be corrected
        if defocus:
            if 'defocus' not in self.corrected_aberrations_list:
                self.corrected_aberrations_list.append('defocus')
        else:
            if 'defocus' in self.corrected_aberrations_list:
                self.corrected_aberrations_list.remove('defocus')

        new_list = self.corrected_initial_list + self.corrected_aberrations_list
        wedge_factor = self.phase.get_wedge_factor()
        _, corrected = self.zernike_coeffs.process_surface_correction(new_list)
        unwrapped_array = -corrected * wedge_factor
        z_label = translate('phase_value_in') + ' (\u03BB)'
        if self.lambda_check:
            unwrapped_array = unwrapped_array * self.lambda_value * 1e-9 * 1e6
            z_label = translate('phase_value_in') + ' (um)'
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.top_right_widget.set_array(unwrapped_array)
        self.top_right_widget.set_z_axis_label(z_label)
        pv, rms = process_statistics_surface(unwrapped_array)
        # TO DO : depending on lambda or nm -> PV RMS to modify (and units !)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def display_2D_ab_corrected(self):
        """
        Display tilt and piston corrected phase in the top right corner.
        """
        self.main_widget.clear_bot_right()
        # Display wrapped in 2D
        self.bot_right_widget = Surface2DView(translate('ab_corrected_phase'))
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        # Correction of the phase with tilt and piston
        wedge_factor = self.phase.get_wedge_factor()
        correction_list = self.corrected_initial_list + self.corrected_aberrations_list
        _, corrected = self.zernike_coeffs.process_surface_correction(correction_list)
        unwrapped_array = -corrected * wedge_factor
        if self.lambda_check:
            unwrapped_array = unwrapped_array * self.lambda_value * 1e-9 * 1e6
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.bot_right_widget.set_array(unwrapped_array)
        '''
        pv, rms = process_statistics_surface(unwrapped_array)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')
        '''

    def display_seidel_table(self):
        """
        list of the first five coefficients of the Seidel decomposition:
                    | Amplitude        | Angle             |
        Tilt        | sqrt(C1^2+C2^2)  | arctan(C2/C1)     |
        Focus       |    2C3 - 6C8     |                   |
        Astig       | 2sqrt(C4^2+C5^2) | (1/2)arctan(C5/C4)|
        Coma        | 3sqrt(C6^2+C7^2) | arctan(C7/C6)     |
        Spherical   |       6C8        |                   |
        """
        self.main_widget.clear_bot_right()
        rows = 5
        cols = 3
        self.bot_right_widget = TableView(rows=rows, cols=cols, height=30,
                                          title=translate('zernike_table'))
        self.bot_right_widget.set_cols_size([120, 100, 100, 100, 100, 100, 100, 100])
        self.bot_right_widget.set_rows_colors(['H', 'N', 'N', 'N', 'N'])
        self.bot_right_widget.set_cols_colors(['N', 'N', 'N'])
        coeff = list(map(lambda x: round(x, 4), self.zernike_coeffs.get_coeffs().copy()))
        data = [[0] * cols for _ in range(rows)]
        unit = 'um' if self.lambda_check else '\u03BB'
        data[0] = [unit, translate('Amplitude'), translate('Angle')]
        data[1] = [translate('ab_tilt_title'), coeff[4], coeff[11], coeff[20], coeff[31]]
        data[2] = ['', coeff[5], coeff[12], coeff[21], coeff[32]]
        data[3] = [translate('ab_coma_title'), coeff[6], coeff[13], coeff[22], coeff[33]]
        data[4] = ['', coeff[7], coeff[14], coeff[23], coeff[34]]
        self.bot_right_widget.set_data(data)
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        pass

    def display_zernike_table(self):
        """
        Display Zernike coefficients value in a table.
                    | Order 3 | Order 5 | Order 7 | Order 9
        Astig       | C4 / C5 | C11 /12 | C20 /21 | C31 /32
        Coma        | C6 / C7 | C13 /14 | C22 /23 | C33 /34
        Ab Sph      | C8      | C15     | C24     | C35
        Trefoil     |         | C11 /12 | C20 /21 | C31 /32
        """
        self.main_widget.clear_bot_right()
        rows = 8
        cols = 5
        self.bot_right_widget = TableView(rows=rows, cols=cols, height=30,
                                          title=translate('zernike_table'))
        self.bot_right_widget.set_cols_size([120, 100, 100, 100, 100, 100, 100, 100])
        self.bot_right_widget.set_rows_colors(['H', 'N', 'N', 'L', 'L', 'N', 'L', 'L'])
        self.bot_right_widget.set_cols_colors(['N', 'N', 'N', 'N', 'N'])
        coeff = list(map(lambda x: round(x, 4), self.zernike_coeffs.get_coeffs().copy()))
        data = [[0] * cols for _ in range(rows)]
        unit = 'um' if self.lambda_check else '\u03BB'
        data[0] = [unit, translate('order_3'), translate('order_5'),
                   translate('order_7'), translate('order_9')]
        data[1] = [translate('ab_astig_title'), coeff[4], coeff[11], coeff[20], coeff[31]]
        data[2] = ['', coeff[5], coeff[12], coeff[21], coeff[32]]
        data[3] = [translate('ab_coma_title'), coeff[6], coeff[13], coeff[22], coeff[33]]
        data[4] = ['', coeff[7], coeff[14], coeff[23], coeff[34]]
        data[5] = [translate('ab_sphere_title'), coeff[8], coeff[15], coeff[24], coeff[35]]
        data[6] = [translate('ab_trefoil_title'), '', coeff[9], coeff[18], coeff[29]]
        data[7] = ['', '', coeff[10], coeff[19], coeff[30]]
        self.bot_right_widget.set_data(data)
        self.main_widget.set_bot_right_widget(self.bot_right_widget)

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

        for jj, aberration in enumerate(self.corrected_aberrations_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        for jj, aberration in enumerate(self.corrected_initial_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        if self.colors[k] is None:
            self.colors[k] = BLUE_IOGS

    def aberration_changed(self, event):
        """
        Action to perform when an option in the aberrations options view changed.
        """
        if 'wedge' in event:
            d = event.split(',')
            wedge_factor = float(d[1])
            self.zernike_coeffs.set_wedge_factor(wedge_factor)

        if 'correct_disp' or 'correct_first' in event:
            # Test if checkboxes are checked
            self.correct_disp, self.correct_first = self.options1_widget.get_checkboxes()

        if 'defocus_correct' in event:
            if 'True' in event:
                self.defocus = True
            else:
                self.defocus = False

        if 'wavelength' in event:
            self.lambda_check = self.options1_widget.is_lambda_checked()
            self.lambda_value = float(self.options1_widget.get_lambda())
            self.zernike_coeffs.update_lambda(value=self.lambda_value, um_check=self.lambda_check)

        self.display_2D_ab_init(defocus=self.defocus)
        self.display_bar_graph_coeff(disp_correct=self.correct_disp, first=self.correct_first)
        if self.submode == 'Zernikecoefficients_aberrations':
            self.display_zernike_table()

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
    manager.data_set.load_images_set_from_file("../_data/test3.mat")
    manager.data_set.load_mask_from_file("../_data/test3.mat")
    manager.phase.prepare_data()
    manager.phase.process_wrapped_phase()
    manager.phase.process_unwrapped_phase()

    # Test controller
    manager.mode_controller = AberrationsController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())