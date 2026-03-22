# -*- coding: utf-8 -*-
"""*analyses_controller.py* file.

./controllers/analyses_controller.py contains AnalysesController class to manage "analyses" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.analyses_options_view import AnalysesOptionsView
from views.surface_2D_view import Surface2DView
from views.double_3d_view import DoubleGraph3DView, Surface3DView
from lensepy import load_dictionary, translate, dictionary
from models.phase import process_statistics_surface
from lensepy.css import *
from lensepy.pyqt6.widget_histogram import HistogramWidget
from PyQt6.QtWidgets import QWidget
from models.zernike_coefficients import Zernike
from utils.dataset_utils import generate_images_grid, DataSetState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel


def is_float(element: any) -> bool:
    """
    Return if any object is a float number.
    :param element: Object to test.
    :return: True if the object is a float number.
    """
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


class AnalysesController:
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
        self.phase: "PhaseModel" = self.manager.phase
        self.zernike_coeffs: Zernike = Zernike(self.phase)
        self.main_widget: MainView = self.manager.main_widget
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.data_set.get_masks_list()) >= 1)
        self.tilt_possible = False
        self.sub_mode = ''
        self.corrected_phase = None
        # Other parameters
        if 'colormap_2D' in self.manager.main_app.default_parameters:
            self.colormap_2D = self.manager.main_app.default_parameters['colormap_2D']
        else:
            self.colormap_2D = 'cividis'

        # Graphical elements
        self.top_left_widget = ImagesDisplayView()  # Display first image of a set
        self.top_right_widget = QWidget()  # ??
        self.bot_right_widget = HTMLView()  # HTML Help on analyses ?
        # Submenu
        self.submenu = SubMenu(translate('submenu_analyses'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/analyses_menu.txt')
        else:
            self.submenu.load_menu('menu/analyses_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        #self.update_submenu_view('correctedphase_analyses')
        # Option 1
        self.options1_widget = AnalysesOptionsView()  # Analyses Options
        # Option 2
        self.options2_widget = QWidget()  # ??

        self.w_3d_view = QWidget()
        # Update menu and view
        self.init_view()
        # Start Analyses
        set_number = 1
        self.submenu.set_button_enabled(1, False)
        self.submenu.set_button_enabled(3, False)
        self.submenu.set_button_enabled(4, False)
        if not self.data_set.is_wrapped():
            self.process_wrapped_phase_calculation(set_number)
        if not self.data_set.is_unwrapped():
            self.process_unwrapped_phase_calculation(set_number)
        if self.data_set.is_unwrapped() and not self.data_set.is_analyzed():
            self.zernike_coeffs.set_phase(self.phase)
            for k in range(3):
                self.process_zernike_calculation(k)
            self.data_set.set_analyzed_state()
            self.tilt_possible = True  # ???
        self.update_submenu('correctedphase_analyses')

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.clear_all()
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/analyses.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/analyses.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)

        # Update grid of images
        images = self.data_set.get_images_sets(1)
        mask = self.data_set.get_global_mask()
        g_images = images[0] * mask
        self.top_left_widget.set_image_from_array(g_images)

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        self.submode = submode
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, False)
        self.submenu.set_button_enabled(1, True)
        self.submenu.set_button_enabled(3, True)
        self.submenu.set_button_enabled(4, True)
        # Activate submenu
        match self.submode:
            case 'wrappedphase_analyses':
                self.submenu.set_activated(3)
            case 'correctedphase_analyses':
                self.submenu.set_activated(1)
        # Update views
        self.main_widget.clear_bot_right()
        # For all submodes
        self.options1_widget.analyses_changed.connect(self.analyses_changed)
        wedge_factor = self.phase.get_wedge_factor()
        self.options1_widget.wedge_edit.set_value(str(wedge_factor))
        # Specific submodes
        match self.submode:
            case 'wrappedphase_analyses':
                self.options1_widget.widget_2D_3D.setEnabled(False)
                self.options1_widget.widget_2D_3D.setStyleSheet(disabled_button)
                self.options1_widget.widget_2D_3D_gain.setEnabled(False)
                self.options1_widget.widget_2D_3D_gain.setStyleSheet(disabled_button)
                # Display wrapped in 2D
                if self.data_set.is_wrapped():
                    self.display_2D_wrapped()
                # Options
                self.options1_widget.wedge_edit.setEnabled(False)
                self.options1_widget.hide_correction()

            case 'correctedphase_analyses':
                # Options
                self.options1_widget.widget_2D_3D.setEnabled(True)
                self.options1_widget.widget_2D_3D.setStyleSheet(unactived_button)
                self.options1_widget.wedge_edit.setEnabled(True)
                self.options1_widget.show_correction()
                if self.options1_widget.is_tilt_checked():
                    self.display_2D_correction()
                else:
                    self.display_2D_unwrapped()

            case _:
                self.options1_widget.wedge_edit.setEnabled(False)
                self.options1_widget.widget_2D_3D.setStyleSheet(disabled_button)
                self.display_help()  # Help in bottom right

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        if self.data_set.is_analyzed():
            self.tilt_possible = True
        #print(event)
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'wrappedphase_analyses':
                # Display Wrapped array in top right area
                self.options1_widget.erase_pv_rms()
                # Process unwrapped phase
                if self.data_set.is_wrapped() and not self.data_set.is_unwrapped():
                    self.process_unwrapped_phase_calculation()

    def display_help(self):
        self.main_widget.clear_bot_right()
        self.bot_right_widget = HTMLView()
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/analyses.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/analyses.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)

    def display_2D_wrapped(self):
        """
        Display Wrapped phase in 2D at the top right corner.
        """
        wrapped = self.phase.get_wrapped_phase()
        wrapped_array = wrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.main_widget.clear_top_right()
        self.top_right_widget = Surface2DView(translate('wrapped_phase'), colormap_2D=self.colormap_2D)

        self.main_widget.set_right_widget(self.top_right_widget)
        self.top_right_widget.set_array(wrapped_array)

    def display_2D_unwrapped(self, gain=1):
        """
        Display unwrapped phase in 2D at the bottom right corner.
        """
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.bot_right_widget = Surface2DView(translate('unwrapped_surface'), colormap_2D=self.colormap_2D)
        self.main_widget.set_right_widget(self.bot_right_widget)
        self.bot_right_widget.set_array(unwrapped_array * gain)
        pv, rms = process_statistics_surface(unwrapped_array)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def display_2D_correction(self, gain=1):
        """
        Display correction depending on tilt checkbox value.
        """
        self.main_widget.clear_top_right()
        self.top_right_widget = Surface2DView(translate('corrected_surface'), colormap_2D=self.colormap_2D)
        self.main_widget.set_right_widget(self.top_right_widget)
        ## TO DO : update colorbar depending on the max range of TOP and BOT right area.
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)

        # Test if tilt !
        if self.options1_widget.is_tilt_checked():
            wedge_factor = self.phase.get_wedge_factor()
            _, corrected = self.zernike_coeffs.process_surface_correction(['piston', 'tilt'])
            corrected = corrected * wedge_factor
        else:
            corrected = unwrapped
        self.corrected_phase = corrected.filled(np.nan)
        self.top_right_widget.set_array(self.corrected_phase * gain)
        # Test if range is checked
        self.top_right_widget.reset_z_range()
        self.options1_widget.erase_pv_rms()
        pv, rms = process_statistics_surface(self.corrected_phase)
        self.options1_widget.set_pv_corrected(pv, '\u03BB')
        self.options1_widget.set_rms_corrected(rms, '\u03BB')
        pv, rms = process_statistics_surface(unwrapped_array)

        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def display_3D(self, gain=1):
        self.w_3d_view = Surface3DView()
        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        Z2 = np.ma.masked_where(np.logical_not(mask), unwrapped_array)
        if self.options1_widget.is_tilt_checked():
            Z1 = np.ma.masked_where(np.logical_not(mask), self.corrected_phase) * gain
            self.w_3d_view.add_labels(name1='Corrected Phase', name2='Unwrapped Phase')
        else:
            Z1 = Z2 * gain
        x, y, w_s = self.w_3d_view.prepare_data_for_mesh(Z1, undersampling=4)
        self.w_3d_view.create_mesh_surface(x, y, w_s)
        self.w_3d_view.showMaximized()
        self.w_3d_view.raise_()

    def analyses_changed(self, event):
        """
        Update controller data and views when options changed.
        :param event: Signal that triggers the event.
        """
        change = event.split(',')
        if change[0] == 'tilt':
            if change[1] == 'on':
                self.display_2D_correction()
            else:
                self.display_2D_unwrapped()
        if change[0] == 'disp_3D':
            self.display_3D(gain=2)

        if change[0] == 'disp_3D_gain':
            self.display_3D(gain=10)

        if change[0] == 'wedge':
            if is_float(change[1]):
                self.phase.set_wedge_factor(float(change[1]))
                if self.submode == 'unwrappedphase_analyses':
                    self.display_2D_unwrapped()
                elif self.submode == 'correctedphase_analyses':
                    self.display_2D_correction()

    def process_wrapped_phase_calculation(self, set_number: int = 1):
        """
        Process wrapped phase from 5 images.
        :param set_number: Number of the set to process.
        """
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        if self.data_set.is_data_ready():
            self.phase.prepare_data()
            # Process Phase
            self.phase.process_wrapped_phase()
            # End of process
            self.data_set.set_wrapped_state(True)

    def process_unwrapped_phase_calculation(self, set_number: int = 1):
        """
        Process unwrapped phase from the wrapped phase.
        :param set_number: Number of the set to process.
        """
        if self.data_set.is_data_ready() and self.data_set.is_wrapped():
            # Process Phase
            self.phase.process_unwrapped_phase()
            # End of process
            self.data_set.set_unwrapped_state(True)

    def process_zernike_calculation(self, coeff: int):
        """Process Zernike coefficients for correction."""
        self.zernike_coeffs.process_zernike_coefficient(coeff)


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

    # Test controller
    manager.mode_controller = AnalysesController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())
