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

from matplotlib import pyplot as plt

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
        self.new_surface = None

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=8)
        self.bot_right = QWidget()
        self.top_right = SimulationChoiceView()
        
        # Setup widgets

        # Signals
        self.bot_left.sliders_changed.connect(self.handle_coeffs_changed)
        self.top_right.display_changed.connect(self.handle_display_changed)

    def init_view(self):
        coeffs = self.bot_left.get_coeffs()
        self.simulated_phase.set_coefficients(coeffs)
        self.new_surface, _ = self.simulated_phase.process_surface()
        self.top_left.set_array(self.new_surface)
        self.top_left.reset_z_range()
        self.top_left.set_title(translate('unwrapped_notilt_surface'))
        self.update_pv_rms()
        super().init_view()

    def handle_display_changed(self, value):
        print(value)
        from matplotlib import pyplot as plt
        plt.figure()
        if value == 'angle':
            c_pupil, x_psf, y_psf, _ = self.simulated_phase.get_complex_pupil()
            print(f'Complex = {c_pupil.dtype}')
            plt.imshow(np.angle(c_pupil))
            plt.colorbar()
        elif value == 'PSF':
            c_pupil, x_psf, y_psf, _ = self.simulated_phase.get_complex_pupil()
            N = c_pupil.shape[0]
            # FFT with padding
            pad_factor = 4
            U_padded_perfect = np.zeros((pad_factor * N, pad_factor * N), dtype=complex)
            U_padded_perfect[N // 2:N // 2 + N, N // 2:N // 2 + N] = c_pupil
            PSF_perfect = np.abs(np.fft.fftshift(np.fft.fft2(U_padded_perfect))) ** 2
            # Centering
            center = pad_factor * N // 2
            half_width = N // 2
            PSF_center_perfect = PSF_perfect[
                center - half_width:center + half_width, center - half_width:center + half_width]
            PSF_center_perfect /= PSF_center_perfect.max()
            plt.imshow(PSF_center_perfect)
            plt.colorbar()

        plt.show()

    def handle_coeffs_changed(self, index, value):
        coeffs = self.bot_left.get_coeffs()
        self.simulated_phase.set_coefficients(coeffs)
        self.new_surface, _ = self.simulated_phase.process_surface()
        self.top_left.set_array(self.new_surface)
        self.top_left.reset_z_range()
        self.top_left.set_title(translate('unwrapped_notilt_surface'))
        self.update_pv_rms()

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def update_pv_rms(self):
        pv, rms = process_statistics_surface(self.new_surface)
        self.top_right.set_rms_uncorrected(rms)
        self.top_right.set_pv_uncorrected(pv)