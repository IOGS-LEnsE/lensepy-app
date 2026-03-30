__all__ = ["ZygoSimulationController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.modules.optics.zygo._old.models.psf import PSFModel
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
        self.psf_display = None
        self.psf_display_perfect = None
        self.mode_display = 'surface'

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=8)
        self.bot_right = Surface2DView('', self.colormap_2D)
        self.top_right = SimulationChoiceView()
        
        # Setup widgets
        self.bot_right.hide()
        # Signals
        self.bot_left.sliders_changed.connect(self.handle_coeffs_changed)
        self.top_right.display_changed.connect(self.handle_display_changed)

    def init_view(self):
        coeffs = self.bot_left.get_coeffs()
        self.simulated_phase.set_coefficients(coeffs)
        self.simulated_phase.process_unwrapped_phase()
        self.new_surface = self.simulated_phase.get_unwrapped_phase()
        self.top_left.set_array(self.new_surface)
        self.top_left.reset_z_range()
        self.top_left.set_title(translate('unwrapped_notilt_surface'))
        self.update_pv_rms()
        c_pupil, N = self.simulated_phase.get_complex_pupil()
        psf = PSFModel(self.simulated_phase)
        self.psf_display, self.psf_display_perfect = psf.get_psf()
        super().init_view()

    def _create_2D_display(self):
        widget = Surface2DView('', self.colormap_2D)
        return widget

    def _create_xy_chart(self):
        widget = TwoChartWidget()
        widget.set_background('white')
        return widget


    def handle_display_changed(self, value):
        self.mode_display = value
        surface, N = self.simulated_phase.get_surface()
        if value == 'surface':
            self.bot_right.hide()
            disp_2D = self._create_2D_display()
            disp_2D.set_array(surface)
            disp_2D.set_title(translate('unwrapped_notilt_surface'))
            disp_2D.reset_z_range()
            self.replace_top_left_widget(disp_2D)
        elif value == 'PSF':
            self.bot_right.show()
            self.bot_right.reset_z_range()
            self.bot_right.set_array(surface)
            disp_2D = self._create_2D_display()
            disp_2D.set_array(self.psf_display)
            disp_2D.set_title(translate('psf_display'))
            disp_2D.reset_z_range()
            self.replace_top_left_widget(disp_2D)
        elif value == 'PSF_slice':
            self.bot_right.show()
            self.bot_right.reset_z_range()
            self.bot_right.set_array(surface)
            psf_slice = self.psf_display[N//2, :]
            psf_p_slice = self.psf_display_perfect[N//2, :]
            psf_slice_y = self.psf_display[:, N//2]
            psf_p_slice_y = self.psf_display_perfect[:, N//2]
            psf_x = np.arange(1, N+1, 1)
            xy_chart = self._create_xy_chart()
            xy_chart.set_data1(psf_x, [psf_slice, psf_p_slice])
            xy_chart.set_legend1([translate('psf_real_disp_legend'),
                                 translate('psf_perf_disp_legend')])
            xy_chart.set_title1(translate('psf_in_x_axe'))
            xy_chart.set_data2(psf_x, [psf_slice_y, psf_p_slice_y])
            xy_chart.set_legend2([translate('psf_real_y_disp_legend'),
                                 translate('psf_perf_y_disp_legend')])
            xy_chart.set_title2(translate('psf_in_y_axe'))
            self.replace_top_left_widget(xy_chart)
            self.top_left.refresh_chart()
        self.update_view()

    def handle_coeffs_changed(self, index, value):
        coeffs = self.bot_left.get_coeffs()
        # Process new surface
        self.simulated_phase.set_coefficients(coeffs)
        self.simulated_phase.process_unwrapped_phase()
        self.new_surface = self.simulated_phase.get_unwrapped_phase()
        # Process PSF
        psf = PSFModel(self.simulated_phase)
        self.psf_display, self.psf_display_perfect = psf.get_psf()
        self.update_pv_rms()
        self.handle_display_changed(self.mode_display)

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def update_pv_rms(self):
        pv, rms = process_statistics_surface(self.new_surface)
        self.top_right.set_rms_uncorrected(rms)
        self.top_right.set_pv_uncorrected(pv)