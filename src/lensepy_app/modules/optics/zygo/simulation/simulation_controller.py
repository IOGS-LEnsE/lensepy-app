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
from lensepy_app.widgets.double_3d_view import Surface3DView

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
        self.wavelength = 632.8 # nm

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=8)
        self.bot_right = Surface2DView('', self.colormap_2D)
        self.top_right = SimulationChoiceView()
        
        # Setup widgets
        self.bot_right.hide()
        self.top_right.set_wavelength(self.wavelength)
        # Signals
        self.bot_left.sliders_changed.connect(self.handle_coeffs_changed)
        self.top_right.display_changed.connect(self.handle_display_changed)
        self.top_right.wavelength_changed.connect(self.handle_wavelength_changed)

    def init_view(self):
        coeffs = self.bot_left.get_coeffs()
        self.simulated_phase.set_coefficients(coeffs)
        self.simulated_phase.process_unwrapped_phase()
        self.new_surface = self.simulated_phase.get_unwrapped_phase()
        self.mask = self.simulated_phase.get_mask()
        self.top_left.set_array(self.new_surface)
        self.top_left.reset_z_range()
        self.top_left.set_title(translate('unwrapped_notilt_surface'))
        self.update_pv_rms()
        c_pupil, N = self.simulated_phase.get_complex_pupil()
        psf = PSFModel(self.simulated_phase)
        mask = np.ones_like(self.simulated_phase, dtype=bool)
        self.psf_display, self.psf_display_perfect = psf.get_psf()
        self.psf_display = np.ma.masked_where(np.logical_not(mask), self.psf_display)
        self.ftm, self.ftm_perfect = psf.get_ftm()
        self.ftm = np.ma.masked_where(np.logical_not(mask), self.ftm)
        self.strehl = psf.get_strehl_ratio()
        self.top_right.set_strehl_ratio(self.strehl)
        self.circled, self.circled_perfect = psf.get_circled_energy()
        super().init_view()

    def _create_2D_display(self):
        widget = Surface2DView('', self.colormap_2D)
        return widget

    def _create_3D_display(self):
        widget = Surface3DView('')
        return widget

    def _create_xy_chart(self):
        widget = TwoChartWidget()
        widget.set_background('white')
        return widget

    def _create_1xy_chart(self):
        widget = XYChartWidget()
        widget.set_background('white')
        return widget

    def handle_wavelength_changed(self, value):
        print(f'Value = {value}')

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
        elif 'psf' in value:
            self.bot_right.show()
            self.bot_right.reset_z_range()
            self.bot_right.set_array(surface)
            if '2D' in value:
                disp_2D = self._create_2D_display()
                disp_2D.set_array(self.psf_display)
                disp_2D.set_title(translate('psf_display'))
                disp_2D.reset_z_range()
                self.replace_top_left_widget(disp_2D)
            elif 'slice' in value:
                self.process_psf_slice()
            elif '3D' in value:
                self.process_psf_3D()

        elif 'ftm' in value:
            self.bot_right.show()
            self.bot_right.reset_z_range()
            self.bot_right.set_array(surface)
            if '2D' in value:
                disp_2D = self._create_2D_display()
                disp_2D.set_array(self.ftm)
                disp_2D.set_title(translate('ftm_display'))
                disp_2D.reset_z_range()
                self.replace_top_left_widget(disp_2D)
            elif 'slice' in value:
                self.process_ftm_slice()
            elif '3D' in value:
                self.process_ftm_3D()

        elif 'circled' in value:
            self.process_circled_slice()
        self.update_view()

    def process_psf_slice(self):
        surface, N = self.simulated_phase.get_surface()
        self.bot_right.show()
        self.bot_right.reset_z_range()
        self.bot_right.set_array(surface)
        psf_disp = self.psf_display / np.max(self.psf_display)  # Normalization
        psf_disp_perfect = self.psf_display_perfect / np.max(self.psf_display_perfect)  # Normalization
        psf_slice = psf_disp[N // 2, :]
        psf_p_slice = psf_disp_perfect[N // 2, :]
        psf_slice_y = psf_disp[:, N // 2]
        psf_p_slice_y = psf_disp_perfect[:, N // 2]
        psf_x = np.arange(1, N + 1, 1)
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

    def process_psf_3D(self):
        disp_3D = self._create_3D_display()
        self.replace_top_left_widget(disp_3D)
        N = self.psf_display.shape[0]
        k = 0.3
        min_N = int(k * N)
        max_N = int((1 - k) * N)
        psf_disp = self.psf_display / np.max(self.psf_display)  # Normalization
        disp_small = psf_disp[min_N:max_N, min_N:max_N]
        x, y, w_s = self.top_left.prepare_data_for_mesh(disp_small, undersampling=1)
        self.top_left.create_mesh_surface(x, y, w_s)
        self.top_left.showMaximized()
        self.top_left.raise_()

    def process_ftm_slice(self):
        surface, N = self.simulated_phase.get_surface()
        self.bot_right.show()
        self.bot_right.reset_z_range()
        self.bot_right.set_array(surface)
        ftm_disp = self.ftm # / np.max(self.psf_display)  # Normalization
        ftm_disp_perfect = self.ftm_perfect # / np.max(self.psf_display_perfect)  # Normalization
        psf_slice = ftm_disp[N // 2, N // 2:3 * N // 4]
        psf_p_slice = ftm_disp_perfect[N // 2, N // 2:3 * N // 4]
        psf_slice_y = ftm_disp[N // 2:3 * N // 4, N // 2]
        psf_p_slice_y = ftm_disp_perfect[N // 2:3 * N // 4, N // 2]
        psf_x = np.arange(1, N // 4 + 1, 1)
        xy_chart = self._create_xy_chart()
        xy_chart.set_data1(psf_x, [psf_slice, psf_p_slice])
        xy_chart.set_legend1([translate('ftm_real_disp_legend'),
                              translate('ftm_perf_disp_legend')], position='top_right')
        xy_chart.set_title1(translate('ftm_in_x_axe'))
        xy_chart.set_data2(psf_x, [psf_slice_y, psf_p_slice_y])
        xy_chart.set_legend2([translate('ftm_real_y_disp_legend'),
                              translate('ftm_perf_y_disp_legend')], position='top_right')
        xy_chart.set_title2(translate('ftm_in_y_axe'))
        self.replace_top_left_widget(xy_chart)
        self.top_left.refresh_chart()

    def process_ftm_3D(self):
        disp_3D = self._create_3D_display()
        self.replace_top_left_widget(disp_3D)
        N = self.psf_display.shape[0]
        k = 0.3
        min_N = int(k * N)
        max_N = int((1 - k) * N)
        psf_disp = self.circled / np.max(self.circled)  # Normalization
        disp_small = psf_disp[min_N:max_N, min_N:max_N]
        x, y, w_s = self.top_left.prepare_data_for_mesh(disp_small, undersampling=1)
        self.top_left.create_mesh_surface(x, y, w_s)
        self.top_left.showMaximized()
        self.top_left.raise_()

    def process_circled_slice(self):
        surface, N = self.simulated_phase.get_surface()
        self.bot_right.show()
        self.bot_right.reset_z_range()
        self.bot_right.set_array(surface)
        circ_disp = self.circled # / np.max(self.psf_display)  # Normalization
        circ_disp_perfect = self.circled_perfect # / np.max(self.psf_display_perfect)  # Normalization
        circ_x = np.arange(1, N // 2 + 1, 1)
        xy_chart = self._create_1xy_chart()
        xy_chart.set_data(circ_x, [circ_disp, circ_disp_perfect])
        xy_chart.set_legend([translate('circ_real_disp_legend'),
                              translate('circ_perf_disp_legend')], position='top_right')
        xy_chart.set_title(translate('circ_in_x_axe'))
        self.replace_top_left_widget(xy_chart)
        self.top_left.refresh_chart()

    def handle_coeffs_changed(self, index, value):
        coeffs = self.bot_left.get_coeffs()
        # Process new surface
        self.simulated_phase.set_coefficients(coeffs)
        self.simulated_phase.process_unwrapped_phase()
        self.new_surface = self.simulated_phase.get_unwrapped_phase()
        # Process PSF
        psf = PSFModel(self.simulated_phase)
        mask = np.ones_like(self.simulated_phase, dtype=bool)
        self.psf_display, self.psf_display_perfect = psf.get_psf(normalized=False)
        self.psf_display = np.ma.masked_where(np.logical_not(mask), self.psf_display)
        self.ftm, self.ftm_perfect = psf.get_ftm(normalized=False)
        self.ftm = np.ma.masked_where(np.logical_not(mask), self.ftm)
        self.update_pv_rms()
        self.strehl = psf.get_strehl_ratio()
        self.top_right.set_strehl_ratio(self.strehl)
        self.circled, self.circled_perfect = psf.get_circled_energy()
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