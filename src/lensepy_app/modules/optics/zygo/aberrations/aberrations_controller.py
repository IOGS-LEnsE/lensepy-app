__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.QtCore import QThread
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController, Worker
from lensepy.optics.zygo.psf import PSFModel
from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import *
from lensepy.optics.zygo import *
from lensepy.utils import downsample_array
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView
from .aberrations_models import *

from matplotlib import pyplot as plt

class ZygoAberrationsController(TemplateController):
    """

    """

    def __init__(self, parent=None, nb_coeff=36):
        """

        """
        super().__init__(parent)
        self.nb_coeff = nb_coeff
        self.data_set : DataSet = self.parent.variables['dataset']
        self.number_of_repetition = 1
        self.phase = None
        self.colormap_2D = 'plasma'
        self.tilt = False
        self.focus = False
        # Threads
        self.thread = QThread()
        self.worker = None

        # Graphical layout
        ### TO DO  - default colormap in default_parameters
        self.top_left = AnalysisInProgressView(self)
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()  # SimulationChoiceView()
        self.bot_zernike = QWidget()

        self.update()

        # ANALYSIS in PROGRESS
        self.process_surface()

    def process_surface(self):
        self.thread = QThread()
        self.worker = ProcessDataWorker(self.parent, self.nb_coeff)
        # Déplacement du worker dans le thread
        self.worker.moveToThread(self.thread)
        # Démarrage du traitement
        self.thread.started.connect(self.worker.run)
        # Progression
        self.worker.progress.connect(
            self.update_progress
        )
        # End of processes
        self.worker.finished.connect(
            self.display_results
        )
        # Errors management
        self.worker.error.connect(
            self.worker_calculation_error
        )
        # Arrêt propre du thread
        self.worker.finished.connect(
            self.thread.quit
        )
        self.worker.error.connect(
            self.thread.quit
        )
        self.worker.finished.connect(
            self.worker.deleteLater
        )
        self.worker.error.connect(
            self.worker.deleteLater
        )
        self.thread.finished.connect(
            self.thread.deleteLater
        )
        self.thread.start()

    def update_progress(self, step):
        self.top_left.update_text(step)

    def display_results(self, results):
        print(results['zernike_coeffs'])
        self._replace_top_left_widget(AberrationsView(colormap=self.colormap_2D))
        self._replace_bot_left_widget(QWidget())
        self._replace_bot_right_widget(Surface2DView('', self.colormap_2D))
        self._replace_top_right_widget(QWidget())
        self._replace_zernike_widget(CoefficientsView(self, number=self.nb_coeff))

        # Signals
        # self.top_right.wavelength_changed.connect(self.handle_wavelength_changed)
        self.bot_zernike.correction_changed.connect(self.handle_correction_changed)
        self.bot_zernike.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_zernike.focus_changed.connect(self.handle_focus_changed)

        '''
        # Process zernike coefficients from phase
        self._process_correction_coeff()
        coeffs = self.zernike_coeffs.get_coeffs()
        self.bot_left.set_coeffs(coeffs)
        '''
        #self.bot_right.set_array(self.surface)

    def init_view(self):
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


class ProcessDataWorker(Worker):

    def __init__(self, parent, nb_coeff):
        super().__init__()
        self.parent = parent
        self.nb_coeff = nb_coeff
        self.data_set = self.parent.variables['dataset']
        self.phase = None
        self.surface, self.mask = None, None
        self.mask_center, self.mask_radius = None, None
        self.zernike_coeffs = None

    def run(self):
        try:
            for i in range(4):
                self.process_step(i+1)
                self.emit_progress(i+1)

            # Result
            ## Create all data then send in a dict ??
            results = {
                'mask_center': self.mask_center,
                'mask_radius': self.mask_radius,
                'surface': self.surface,
                'mask': self.mask,
                'zernike_coeffs': self.zernike_coeffs
            }
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(e)

    def process_step(self, index):
        match index:
            case 1:
                ## GET PHASE
                if self.parent.variables['phase'] is None:
                    self.phase = PhaseModel(data_set=self.data_set)
                    self.parent.variables['phase'] = self.phase
                else:
                    self.phase = self.parent.variables['phase']
                return
            case 2:
                ## PROCESS AUTO-MASK
                self.mask_center, self.mask_radius = get_auto_mask(dataset=self.data_set)
                #> TO DO : apply mask
                return
            case 3:
                ## PROCESS PHASE
                self.phase.process_data()
                self.surface, self.mask = self.phase.process_unwrapped_phase()
                return
            case 4:
                ## PROCESS ZERNIKE
                self.zernike_coeffs = Zernike(self.phase)
                self.zernike_coeffs.process_zernike_coefficient(0)
                for k in range(self.nb_coeff + 1):
                    self.zernike_coeffs.process_zernike_coefficient(k)
                return