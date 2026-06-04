__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy.optics.zygo.psf import PSFModel
from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import *
from lensepy.optics.zygo import *
from lensepy.utils import downsample_array
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

        self.colormap_2D = 'plasma'
        self.tilt = False
        self.focus = False

        # Graphical layout
        ### TO DO  - default colormap in default_parameters
        self.top_left = AberrationsView(colormap=self.colormap_2D) # Surface2DView('', self.colormap_2D)
        self.bot_left = CoefficientsView(self, number=nb_coeff)
        self.bot_right = Surface2DView('', self.colormap_2D)
        self.top_right = SimulationChoiceView()
        
        # Setup widgets

        # Signals
        self.top_right.wavelength_changed.connect(self.handle_wavelength_changed)
        self.bot_left.correction_changed.connect(self.handle_correction_changed)
        self.bot_left.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_left.focus_changed.connect(self.handle_focus_changed)

    def init_view(self):
        # Process zernike coefficients from phase
        self._process_correction_coeff()
        coeffs = self.zernike_coeffs.get_coeffs()
        self.bot_left.set_coeffs(coeffs)
        super().init_view()

    def handle_tilt_changed(self, value):
        self.tilt = value
        self._process_correction_coeff()

    def handle_focus_changed(self, value):
        self.focus = value
        self._process_correction_coeff()

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

        # Downsampling  ?
        downsampling_factor = 4
        unwrapped_phase_down = downsample_array(unwrapped_phase, downsampling_factor)
        new_mask = downsample_array(self.phase.get_mask().astype(np.uint8), downsampling_factor)
        new_mask = new_mask < 0.5
        # TEST
        '''
        unwrapped_phase_down = unwrapped_phase
        new_mask = self.phase.get_mask()
        '''

        print(f'Unw Type = {unwrapped_phase_down.dtype}')
        psf_uncorr = PSFModel(wavefront=unwrapped_phase_down, mask=new_mask)
        psf_uncorr_display, psf_uncorr_display_perfect = psf_uncorr.get_psf()
        self.top_left.set_psf_uncorrect(psf_uncorr_display)


    def handle_correction_changed(self, coeffs):
        print(f'Correction changed: {coeffs}')
        self._process_correction_coeff(coeffs)

    def handle_wavelength_changed(self, value):
        print(f'Value = {value}')

