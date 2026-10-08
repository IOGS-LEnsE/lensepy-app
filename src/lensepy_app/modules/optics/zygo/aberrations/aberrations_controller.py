__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.QtCore import QThread
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController, Worker
from lensepy.optics.zygo.psf import PSFModel
from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import AnalysisInProgressView
from lensepy_app.modules.optics.zygo.aberrations.aberrations_coeff_view import *
from lensepy_app.modules.optics.zygo.aberrations.aberrations_surface_view import *
from lensepy.optics.zygo import *
from lensepy.utils import downsample_array
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView
from .aberrations_models import *


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
        self.zernike_coeffs = None
        self.colormap_2D = 'plasma'
        self.tilt = False
        self.focus = False
        self.params_window = ParamsView(self)
        self.coeffs_window = CoefficientsValueView(self)
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

        # Signals
        self.params_window.window_closed.connect(self.handle_params_window_closed)
        self.coeffs_window.window_closed.connect(self.handle_coeffs_window_closed)
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
        '''
        self.thread.finished.connect(
            self.process_PSF
        )
        '''
        self.thread.start()

    def process_PSF(self):
        self.thread = QThread()
        self.worker = ProcessPSFWorker(self.parent)
        # Déplacement du worker dans le thread
        self.worker.moveToThread(self.thread)
        # Démarrage du traitement
        self.thread.started.connect(self.worker.run)
        # Progression
        self.worker.progress.connect(
            self.update_progress_psf
        )
        # End of processes
        self.worker.finished.connect(
            self.display_results_psf
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

    def update_progress_psf(self, step):
        print(f'PSF step = {step}')

    def display_results(self, results):
        ## Update Local Variables / Results
        self.zernike_coeffs = results['zernike_coeffs']
        self.params_window.set_phase(self.parent.variables['phase'])

        self._replace_top_left_widget(Surface2DView(
            translate('interferogram'), colormap_2D='gray'))
        self._replace_bot_left_widget(Surface2D3DView(
            translate('unwrapped_surface'), parent=self,
            colormap=self.colormap_2D))
        self._replace_bot_right_widget(QWidget())
        self._replace_top_right_widget(QWidget())
        self._replace_zernike_widget(CoefficientsView(self, number=self.nb_coeff))

        # Signals
        # self.top_right.wavelength_changed.connect(self.handle_wavelength_changed)
        self.bot_zernike.correction_changed.connect(self.handle_correction_changed)
        self.bot_zernike.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_zernike.focus_changed.connect(self.handle_focus_changed)
        self.bot_zernike.params_windowed.connect(self.handle_params_windowed)
        self.bot_zernike.coeffs_windowed.connect(self.handle_coeffs_windowed)

        ## Interferogram
        image1 = self.data_set.get_image_from_set(1, 1)
        mask = self.data_set.get_global_mask()  # TO CHANGE WITH AUTO MASK
        self.top_left.set_array(image1 * mask)

        ## Zernike Coefficients
        coeffs = self.zernike_coeffs.get_coeffs()
        self.bot_zernike.set_coeffs(coeffs)

        # Process zernike coefficients correction from phase
        self._process_correction_coeff()
        coeffs = self.zernike_coeffs.get_coeffs()

    def display_results_psf(self, results):
        ## Update Local Variables / Results
        print('FINISHED')

    def init_view(self):
        super().init_view()

    def handle_tilt_changed(self, value):
        self.tilt = value
        self._process_correction_coeff()

    def handle_focus_changed(self, value):
        self.focus = value
        self._process_correction_coeff()

    def handle_params_windowed(self, value):
        if value:
            self.params_window.show()

    def handle_params_window_closed(self):
        self.bot_zernike.reactivate_params_button()

    def handle_coeffs_windowed(self, value):
        if value:
            self.coeffs_window.show()
            self.coeffs_window.set_coeffs(self.zernike_coeffs.get_coeffs())

    def handle_coeffs_window_closed(self):
        self.bot_zernike.reactivate_coeffs_button()

    def _process_correction_coeff(self, coeffs=None):
        coeff_list = []
        if self.tilt:
            coeff_list.append(1)
            coeff_list.append(2)
        if self.focus:
            coeff_list.append(3)

        if coeffs is not None:
            _, corrected_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeffs)
            self.bot_left.set_surface(corrected_phase)
            pv, rms = process_statistics_surface(corrected_phase)
        else:
            _, unwrapped_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeff_list)
            self.bot_left.set_surface(unwrapped_phase)
            pv, rms = process_statistics_surface(unwrapped_phase)
        self.bot_zernike.set_pv_rms(pv, rms, units=LAMBDA)

    def handle_correction_changed(self, coeffs):
        self._process_correction_coeff(coeffs)

    def handle_wavelength_changed(self, value):
        print(f'Value = {value}')


class ProcessDataWorker(Worker):

    def __init__(self, parent, nb_coeff):
        super().__init__()
        self.parent = parent # Manager
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


class ProcessPSFWorker(Worker):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent # Manager
        self.phase = None
        self.surface, self.mask = None, None
        self.psf = None
        self.psf_perfect = None

    def run(self):
        try:
            self.process_step(1)
            self.emit_progress(1)

            # Result
            ## Create all data then send in a dict ??
            results = {
                'psf': self.psf,
                'psf_perfect': self.psf_perfect
            }
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(e)

    def process_step(self, index):
        match index:
            case 1:
                ## GET PHASE
                self.phase = self.parent.variables['phase']
                surface = self.phase.get_surface()
                mask = self.phase.get_mask()
                ## PROCESS PSF
                psf = PSFModel(wavefront=surface, mask=mask)
                psf_c, psf_perfect, center_x, padding = psf.get_psf(normalized=True)
                return
