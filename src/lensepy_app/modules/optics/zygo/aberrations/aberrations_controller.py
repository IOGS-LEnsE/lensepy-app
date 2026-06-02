__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.modules.optics.zygo._old.models.psf import PSFModel
from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import *
from lensepy.optics.zygo import *
from lensepy.images.conversion import downsample_and_upscale
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView

from matplotlib import pyplot as plt

class ZygoAberrationsController(TemplateController):
    """

    """

    def __init__(self, parent=None, nb_coeff=36):
        """

        """
        super().__init__(parent)
        self.data_set : DataSet = self.parent.variables['dataset']
        self.number_of_repetition = 1
        if self.parent.variables['phase'] is None:
            self.phase = PhaseModel(phase=self.data_set)
            self.parent.variables['phase'] = self.phase
        else:
            self.phase = self.parent.variables['phase']
        self.zernike_coeffs = Zernike(self.phase)
        self.zernike_coeffs.process_zernike_coefficient(0)
        for k in range(nb_coeff + 1):
            self.zernike_coeffs.process_zernike_coefficient(k)
        print(self.zernike_coeffs.get_coeffs())
        # TO DO  - default colormap in default_parameters
        self.unwrapped_phase = self.phase.get_unwrapped_phase()

        self.new_surface, _ = downsample_and_upscale(self.unwrapped_phase, 2)
        new_mask, _ = downsample_and_upscale(self.phase.get_mask().astype(np.uint8), 2)
        self.new_mask = (new_mask > 0.5)
        #self.new_surface = np.ma.masked_where(np.logical_not(self.new_mask), new_surface)
        self.colormap_2D = 'cividis'
        self.colormap_2D = 'plasma'
        self.psf_display = None
        self.psf_display_perfect = None
        self.mode_display = 'surface'
        self.wavelength = 632.8 # nm
        self.tilt = False
        self.focus = False

        # Graphical layout
        self.top_left = AberrationsView(colormap=self.colormap_2D) # Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=nb_coeff)
        self.bot_right = Surface2DView('', self.colormap_2D)
        self.top_right = SimulationChoiceView()
        
        # Setup widgets
        self.bot_right.hide()
        self.top_right.set_wavelength(self.wavelength)
        # Signals
        self.top_right.wavelength_changed.connect(self.handle_wavelength_changed)
        self.bot_left.correction_changed.connect(self.handle_correction_changed)
        self.bot_left.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_left.focus_changed.connect(self.handle_focus_changed)

    def init_view(self):
        # Process zernike coefficients from phase
        if self.new_surface is not None:
            # Down sampling
            self.top_left.set_array_uncorrect(self.new_surface)
            self.top_left.reset_z_range()
            self.top_left.set_title_uncorrect(translate('unwrapped_surface'))
            psf = PSFModel(wavefront=self.new_surface, mask=self.new_mask)
            self.psf_display, self.psf_display_perfect = psf.get_psf()
            coeffs = self.zernike_coeffs.get_coeffs()
            self.bot_left.set_coeffs(coeffs)
        super().init_view()

    def _create_2D_display(self):
        widget = Surface2DView('', self.colormap_2D)
        return widget

    def _create_xy_chart(self):
        widget = TwoChartWidget()
        widget.set_background('white')
        return widget

    def handle_tilt_changed(self, value):
        self.tilt = value
        self._process_correction_coeff()

    def handle_focus_changed(self, value):
        self.focus = not value

    def _process_correction_coeff(self, coeffs=None):
        coeff_list = []
        if self.tilt:
            coeff_list.append(1)
            coeff_list.append(2)
        if self.focus:
            coeff_list.append(3)

        _, unwrapped_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeff_list)
        self.top_left.set_array_uncorrect(unwrapped_phase)

        if coeffs is not None:
            _, corrected_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeffs)
            self.top_left.set_array_correct(corrected_phase)
        else:
            self.top_left.set_array_correct(unwrapped_phase)


    def handle_correction_changed(self, coeffs):
        print(f'Correction changed: {coeffs}')
        self._process_correction_coeff(coeffs)

    def handle_wavelength_changed(self, value):
        print(f'Value = {value}')

