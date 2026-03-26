__all__ = ["ZygoSimulationController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.modules.optics.zygo.simulation.simulation_view import *
from lensepy.optics.zygo import *
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView


class ZygoSimulationController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # TO DO  - default colormap in default_parameters
        self.colormap_2D = 'cividis'
        self.colormap_2D = 'plasma'
        self.corrected_phase = None
        self.simulated_phase = SimulatedPhase()

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=15)
        self.bot_right = QWidget()
        self.top_right = SimulationChoiceView()
        
        # Setup widgets

        # Signals
        self.bot_left.sliders_changed.connect(self.handle_coeffs_changed)

    def init_view(self):
        super().init_view()

    def handle_coeffs_changed(self, index, value):
        print(f'Slider changed / {index} = {value}')
        coeffs = self.bot_left.get_coeffs()
        self.simulated_phase.set_coefficients(coeffs)
        surface = self.simulated_phase.process_surface()
        self.top_left.set_array(surface)


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