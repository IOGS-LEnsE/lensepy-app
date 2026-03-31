__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import AberrationsChoiceView
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy.optics.zygo import *
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView


class ZygoAberrationsController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.data_set : DataSet = self.parent.variables['dataset']
        self.number_of_repetition = 1
        if self.parent.variables['phase'] is None:
            self.phase = PhaseModel(self.data_set)
            self.parent.variables['phase'] = self.phase
        else:
            self.phase = self.parent.variables['phase']
        # TO DO  - default colormap in default_parameters
        self.colormap_2D = 'cividis'
        self.colormap_2D = 'plasma'
        self.corrected_phase = None

        # Graphical layout
        self.top_left = QWidget()
        self.bot_left = QWidget()
        self.bot_right = Surface2DView('Unwrapped Phase', self.colormap_2D, adapt_size=8)
        self.top_right = AberrationsChoiceView()
        
        # Setup widgets
        self.phase.prepare_data()
        self.zernike_coeffs = Zernike(self.phase)

        # Signals

    def init_view(self):
        super().init_view()
        self.correct_surface()
        self.display_2D_unwrapped()

    def correct_surface(self):
        self.unwrapped_phase = self.phase.get_unwrapped_phase()
        _, self.corrected_phase = self.zernike_coeffs.process_surface_correction(['piston', 'tilt'])
        pv, rms = process_statistics_surface(self.corrected_phase)
        self.top_right.set_pv_uncorrected(pv)
        self.top_right.set_rms_uncorrected(rms)

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def display_2D_unwrapped(self, gain=1):
        """
        Display unwrapped phase in 2D at the bottom right corner.
        """
        unwrapped_array = self.corrected_phase.filled(np.nan)
        title = translate('unwrapped_notilt_surface')
        # Display unwrapped and corrected in 2D
        self.bot_right.set_title(title)
        self.bot_right.set_array(unwrapped_array * gain)

    def process_zernike_calculation(self, coeff: int):
        """Process Zernike coefficients for correction."""
        self.zernike_coeffs.process_zernike_coefficient(coeff)