__all__ = ["ZygoAberrationsController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.QtCore import QThread
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController, Worker

from lensepy_app.modules.optics.zygo.aberrations.aberrations_view import *
from lensepy_app.modules.optics.zygo.aberrations.aberrations_coeff_view import *
from lensepy_app.modules.optics.zygo.aberrations.aberrations_surface_view import *
from lensepy.optics.zygo import *
from lensepy.utils import downsample_array
from lensepy_app.modules.optics.zygo.aberrations.aberrations_params_view import ParamsView
from lensepy_app.widgets.image_cross_sections import *
from .aberrations_models import *
from lensepy_app import *


class ZygoAberrationsController(TemplateController):
    """

    """

    def __init__(self, parent=None, nb_coeff=36):
        """

        """
        super().__init__(parent)
        self.manager = parent
        self.psf_processing = False
        self.psf_processed = False
        self.psf_update_pending = False
        '''
        TO DELETE
        '''
        file_path = '../lensepy-data/optics/zygo/test3.mat'
        data_set = DataSet()
        data_set.load_images_set_from_file(file_path)
        data_set.load_masks_from_file(file_path)
        self.manager.variables['dataset'] = data_set
        '''
        END DELETE
        '''

        self.nb_coeff = nb_coeff
        self.data_set : DataSet = self.manager.variables['dataset']
        self.number_of_repetition = 1
        self.phase = None
        self.zernike_coeffs = None
        self.colormap_2D = 'plasma'
        self.tilt = False
        self.focus = False
        self.params_window = ParamsView(self)
        self.coeffs_window = CoefficientsValueView(self)
        self.wavefront_disp = None
        # Threads
        self.thread = QThread()
        self.worker = None
        self.manager.variables['pad_factor'] = self.params_window.get_padding_value()

        # Graphical layout
        ### TO DO  - default colormap in default_parameters
        self.top_left = AnalysisInProgressView(self)
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()  # SimulationChoiceView()
        self.bot_zernike = QWidget()

        # Signals
        self.params_window.window_closed.connect(self.handle_params_window_closed)
        self.coeffs_window.window_closed.connect(self.handle_coeffs_window_closed)

        # Start surface processing
        if self.manager.variables['phase_results'] is None:
            self.process_surface()
        else:
            results = self.manager.variables['phase_results']
            self.display_results(results, first=False)
            self.process_PSF()

    def init_view(self):
        super().init_view()

    def _start_psf_if_needed(self):
        if self.psf_processing:
            return
        if not self.psf_update_pending:
            return
        self.psf_update_pending = False
        self.process_PSF()

    def process_surface(self):
        self.thread = QThread()
        self.worker = ProcessDataWorker(self.manager, self.nb_coeff)
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
        self.thread.finished.connect(
            self.process_PSF
        )
        self.thread.start()

    def process_PSF(self):
        if self.psf_processing:
            return
        self.psf_processing = True
        self.thread = QThread()
        self.worker = ProcessPSFWorker(self.manager)
        # Déplacement du worker dans le thread
        self.worker.moveToThread(self.thread)
        # Démarrage du traitement
        self.thread.started.connect(self.worker.run)
        # Progression
        self.worker.progress.connect(self.update_progress_psf)
        # End of processes
        self.worker.finished.connect(self.display_results_psf)
        # Errors management
        self.worker.error.connect(self.worker_calculation_error)
        # Arrêt propre du thread
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._on_psf_thread_finished)
        self.thread.finished.connect(
            self.thread.deleteLater
        )
        self.thread.start()

    def _on_psf_thread_finished(self):
        self.psf_processing = False
        self._start_psf_if_needed()

    def update_progress(self, step):
        self.top_left.update_text(step)

    def update_progress_psf(self, step):
        if step == 2:
            self.top_left.set_visible('top')
            self.top_left.set_visible('bot')
        print(f'PSF step = {step}')

    def display_results(self, results, first=True):
        self.manager.variables['phase_results'] = results
        ## Update Local Variables / Results
        self.zernike_coeffs = results['zernike_coeffs']
        self.params_window.set_phase(self.manager.variables['phase'])

        if first:
            self._replace_top_left_widget(SurfaceOptionsView())
            self._replace_bot_left_widget(Surface2D3DView(
                translate('unwrapped_surface'), parent=self,
                colormap=self.colormap_2D))
            self._replace_bot_right_widget(QWidget())
            self._replace_top_right_widget(QWidget())
            self._replace_zernike_widget(CoefficientsView(parent=self, number=self.nb_coeff))
        else:
            self.top_left = Surface2DView(translate('interferogram'),
                                          colormap_2D='gray', parent=self)
            self.bot_left = Surface2D3DView(translate('unwrapped_surface'), parent=self,
                colormap=self.colormap_2D)
            self.bot_zernike = CoefficientsView(parent=self, number=self.nb_coeff)

        self.bot_zernike.set_enabled(False)
        # Signals
        self.bot_zernike.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_zernike.focus_changed.connect(self.handle_focus_changed)
        self.bot_zernike.params_windowed.connect(self.handle_params_windowed)
        self.bot_zernike.coeffs_windowed.connect(self.handle_coeffs_windowed)
        self.top_left.selection_changed.connect(self.handle_right_selection_changed)

        ## Interferogram
        image1 = self.data_set.get_image_from_set(1, 1)
        mask = self.data_set.get_global_mask()  # TO CHANGE WITH AUTO MASK
        self.top_left.set_surface(image1 * mask)
        # Display wavefront
        self.bot_left.set_surface(results['surface'])

        ## Zernike Coefficients
        coeffs = self.zernike_coeffs.get_coeffs()
        self.bot_zernike.set_coeffs(coeffs)

        # Process zernike coefficients correction from phase
        self._process_correction_coeff()
        coeffs = self.zernike_coeffs.get_coeffs()

    def display_results_psf(self, results):
        self.psf_processing = False
        self.manager.variables['psf_results'] = results
        ## Update Local Variables / Results
        self.psf = results['psf']
        ## Display
        self._replace_top_right_widget(ImageCrossSections(parent=self, cmap='gray'))
        self.top_right.set_data(self.psf)
        self.top_right.set_color_map('gray')
        self.bot_zernike.set_enabled(True)
        self.bot_zernike.correction_changed.connect(self.handle_correction_changed)

    def init_view(self):
        super().init_view()

    def handle_right_selection_changed(self, index, value):
        """
        :param index:   'top' or 'bot'
        :param value:
                translate('psf_and_slice'),
                translate('psf_only'),
                translate('psf_log'),
                translate('psf_slice'),
                translate('ftm_and_slice'),
                translate('ftm_only'),
                translate('ftm_slice')
        """
        if index == 'top':
            if value == translate('psf_and_slice'):
                widget = ImageCrossSections(parent=self, cmap='gray')
                widget.set_data(self.psf)
                widget.set_color_map('gray')
                self.top_right.deleteLater()
                self._replace_top_right_widget(widget)
            elif value == translate('psf_log'):
                widget = ImageCrossSections(parent=self, cmap='gray')
                widget.set_data(np.log(self.psf+0.001))
                widget.set_color_map('gray')
                self.top_right.deleteLater()
                self._replace_top_right_widget(widget)
            else:
                widget = QWidget()
                self.top_right.deleteLater()
                self._replace_top_right_widget(widget)

        if index == 'bot':
            if value == translate('psf_and_slice'):
                widget = ImageCrossSections(parent=self, cmap='gray')
                widget.set_data(self.psf)
                widget.set_color_map('gray')
                self.bot_right.deleteLater()
                self._replace_bot_right_widget(widget)
            elif value == translate('psf_log'):
                widget = ImageCrossSections(parent=self, cmap='gray')
                widget.set_data(np.log(self.psf+0.001))
                widget.set_color_map('gray')
                self.bot_right.deleteLater()
                self._replace_bot_right_widget(widget)
            else:
                widget = QWidget()
                self.bot_right.deleteLater()
                self._replace_bot_right_widget(widget)

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
        if isinstance(self.bot_zernike, CoefficientsView):
            self.bot_zernike.reactivate_params_button()
        # Restart process of PSF
        print(f'New PAD = {self.manager.get_variable("pad_factor")}')


    def handle_coeffs_windowed(self, value):
        if value:
            self.coeffs_window.show()
            self.coeffs_window.set_coeffs(self.zernike_coeffs.get_coeffs())

    def handle_coeffs_window_closed(self):
        if isinstance(self.bot_zernike, CoefficientsView):
            self.bot_zernike.reactivate_coeffs_button()

    def _process_correction_coeff(self, coeffs=None):
        coeff_list = []
        coeff_list.append(0)
        if self.tilt:
            coeff_list.append(1)
            coeff_list.append(2)
        if self.focus:
            coeff_list.append(3)

        if coeffs is not None:
            _, corrected_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeffs)
            self.wavefront_disp = corrected_phase
        else:
            _, unwrapped_phase = self.zernike_coeffs.process_surface_correction_by_coeff(coeff_list)
            self.wavefront_disp = unwrapped_phase

    def handle_correction_changed(self, coeffs):
        # BLOCK INTERFACE - Especially PSF/FTM display
        self.top_left.set_visible('top', value=False)
        self.top_left.set_visible('bot', value=False)
        self.bot_zernike.set_enabled(False)
        # Process correction - new wavefront
        self._process_correction_coeff(coeffs)
        # Display Wavefront
        pv, rms = process_statistics_surface(self.wavefront_disp)
        self.bot_left.set_surface(self.wavefront_disp)
        self.bot_zernike.set_pv_rms(pv, rms, units=LAMBDA)
        # Process new PSF
        self.psf_update_pending = True
        self._start_psf_if_needed()

    def handle_wavelength_changed(self, value):
        print(f'Value = {value}')

    def cleanup(self):
        self.params_window.deleteLater()
        self.coeffs_window.deleteLater()


class ProcessDataWorker(Worker):

    def __init__(self, parent, nb_coeff):
        super().__init__()
        self.manager = parent # Manager
        self.nb_coeff = nb_coeff
        self.data_set = self.manager.variables['dataset']
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
                if self.manager.variables['phase'] is None:
                    self.phase = PhaseModel(data_set=self.data_set)
                    self.manager.variables['phase'] = self.phase
                else:
                    self.phase = self.manager.variables['phase']
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
        self.manager = parent
        self.phase = None
        self.surface, self.mask = None, None
        self.psf = None
        self.psf_perfect = None
        self.center_x = 0
        self.pad_factor = self.manager.controller.get_variables('pad_factor')
        print(f'Padding = {self.pad_factor}')

    def run(self):
        try:
            print(f'PSF Worker - RUNNING')
            for i in range(2):
                self.process_step(i+1)
                self.emit_progress(i+1)

            # Result
            ## Create all data then send in a dict ??
            results = {
                'psf': self.psf,
                'psf_perfect': self.psf_perfect
            }
            print(f'PSF Worker - STOPPING')
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(e)

    def process_step(self, index):
        match index:
            case 1:
                ## GET PHASE
                # Corrected phase :
                wavefront = self.manager.controller.wavefront_disp
                self.phase = self.manager.variables['phase']
                if wavefront is not None:
                    surface, size_s = wavefront, wavefront.shape[0]
                else:
                    surface, size_s = self.phase.get_surface()
                mask = self.phase.get_mask()
                ## PROCESS PSF
                psf = PSFModel(wavefront=surface, mask=mask)
                self.psf, self.psf_perfect, self.center_x, self.pad_factor = (
                    psf.get_psf(normalized=True, pad_factor=self.pad_factor))
                return
            case 2:
                ## PROCESS FTM
                pass
