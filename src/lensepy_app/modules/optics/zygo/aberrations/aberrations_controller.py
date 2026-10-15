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
from lensepy.utils.images import zoom_image_square, crop_square_radius
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
        self.params_window = ParamsView(parent=self)
        self.coeffs_window = CoefficientsValueView(parent=self)
        self.wavefront_disp = None
        self.top_right_disp = translate('psf_and_slice')
        self.bot_right_disp = ''
        # Threads
        self.thread = QThread()
        self.worker = None
        self.manager.variables['pad_factor'] = self.params_window.get_padding_value()
        self.manager.variables['wavelength'] = self.params_window.get_wavelength()
        self.manager.variables['f_number'] = self.params_window.get_f_number()

        # Graphical layout
        ### TO DO  - default colormap in default_parameters
        self.top_left = AnalysisInProgressView(parent=self)
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

    def display_results(self, results, first=True):
        self.manager.variables['phase_results'] = results
        ## Update Local Variables / Results
        self.zernike_coeffs = results['zernike_coeffs']
        self.params_window.set_phase(self.manager.variables['phase'])

        if first:
            self.top_left.deleteLater()
            self._replace_top_left_widget(SurfaceOptionsView(parent=self))
            self._replace_bot_left_widget(Surface2D3DView(
                translate('unwrapped_surface'), parent=self,
                colormap=self.colormap_2D))
            self._replace_bot_right_widget(QWidget())
            self._replace_top_right_widget(QWidget())
            self._replace_zernike_widget(CoefficientsView(parent=self, number=self.nb_coeff))
        else:
            self.top_left = SurfaceOptionsView(parent=self)
            self.bot_left = Surface2D3DView(translate('unwrapped_surface'),
                                            parent=self,
                                            colormap=self.colormap_2D)
            self.bot_zernike = CoefficientsView(parent=self, number=self.nb_coeff)
            self.update()

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
        ## Display
        self._replace_top_right_widget(ImageCrossSections(parent=self, cmap='gray'))
        self.handle_right_selection_changed('top', self.top_right_disp)
        self.handle_right_selection_changed('bot', self.bot_right_disp)
        self.bot_zernike.correction_changed.connect(self.handle_correction_changed)
        self.bot_zernike.set_enabled(True)

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
                translate('ftm_slice'),
                translate('circled_energy')
        """
        wavelength = float(self.manager.variables['wavelength']) * 1e-9
        pad_factor = float(self.manager.variables['pad_factor'])
        f_number = float(self.manager.variables['f_number'])
        N_size = self.manager.variables['psf_results']['psf'].shape[0]
        # Axis construction
        pupil_ratio = 1
        image_radius = wavelength * f_number * pupil_ratio
        x_ax_surface = np.linspace(-N_size // 2, N_size // 2 - 1, N_size) * image_radius * 1e6  # um

        # Process depending on top/bot and data to display
        if value == translate('psf_and_slice'):
            widget = self._display_psf_and_slice(x_ax_surface)
        elif value == translate('psf_log'):
            widget = self._display_psf_log()
        elif value == translate('ftm_and_slice'):
            widget = self._display_ftm_and_slice()
        else:
            widget = QWidget()

        if index == 'top':
            self.top_right_disp = value
            self._replace_top_right_widget(widget)
        elif index == 'bot':
            self.bot_right_disp = value
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
        self.process_PSF()


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
        self.manager.variables['wavelength'] = value

    def cleanup(self):
        self.params_window.deleteLater()
        self.coeffs_window.deleteLater()

    def _display_psf_and_slice(self, axis=None):
        psf = self.manager.variables['psf_results']['psf']
        # Zoom In ?
        psf_c, size_z = zoom_image_square(psf, threshold=0.001)
        # Axis construction (with zoom)
        N_size = psf.shape[0]
        N_zoom = psf_c.shape[0]
        borne_x1 = (N_size - N_zoom) // 2
        borne_x2 = borne_x1 + N_zoom
        if axis is not None:
            x_axis = axis[borne_x1:borne_x2]
        else:
            x_axis = np.linspace(0, N_size-1, N_size)
        # Display
        widget = ImageCrossSections(parent=self, cmap='gray',
                                    title=translate('psf_and_slice_title'))
        widget.set_data(psf_c)
        widget.set_x_axis(x_axis, label=translate('x_axis_in_um'))
        widget.set_y_axis(x_axis)
        widget.set_color_map('gray')
        return widget

    def _display_psf_log(self, axis=None):
        psf = self.manager.variables['psf_results']['psf']
        # Zoom In ?
        psf_c, size_z = zoom_image_square(psf, threshold=-5)
        # Axis construction (with zoom)
        N_size = psf.shape[0]
        N_zoom = psf_c.shape[0]
        borne_x1 = (N_size - N_zoom) // 2
        borne_x2 = borne_x1 + N_zoom
        print(f'Borne_X1 = {borne_x1} / Borne_X2 = {borne_x2}')
        if axis is not None:
            x_axis = axis[borne_x1:borne_x2]
        else:
            x_axis = np.linspace(0, N_size-1, N_size)

        widget = ImageCrossSections(parent=self, cmap='gray',
                                    title=translate('psf_log_title'))
        widget.set_data(np.log(psf_c + 0.001))
        widget.set_x_axis(x_axis, label=translate('x_axis_in_um'))
        widget.set_y_axis(x_axis)
        widget.set_color_map('gray')
        return widget

    def _display_ftm_and_slice(self, axis=None):
        ftm = self.manager.variables['psf_results']['ftm']
        widget = ImageCrossSections(parent=self, cmap='gray',
                                    title=translate('ftm_and_slice_title'))
        widget.set_data(ftm)
        widget.set_color_map('gray')
        return widget



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
        self.psf_model = None
        self.psf = None
        self.psf_perfect = None
        self.center_x = 0
        self.pad_factor = self.manager.controller.get_variables('pad_factor')
        self.ftm = None
        self.ftm_perfect = None
        self.strehl_ratio = 1

    def run(self):
        try:
            for i in range(2):
                self.process_step(i+1)
                self.emit_progress(i+1)

            # Result
            ## Create all data then send in a dict ??
            results = {
                'psf': self.psf,
                'psf_perfect': self.psf_perfect,
                'ftm': self.ftm,
                'ftm_perfect': self.ftm_perfect,
                'strehl': self.strehl_ratio
            }
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
                self.psf_model = PSFModel(wavefront=surface, mask=mask)
                self.psf, self.psf_perfect, self.center_x, self.pad_factor = (
                    self.psf_model.get_psf(normalized=True,
                                           pad_factor=self.pad_factor))
                return
            case 2:
                ## PROCESS FTM
                self.ftm, self.ftm_perfect = self.psf_model.get_ftm(normalized=True)

                self.strehl_ratio = self.psf_model.get_strehl_ratio()
                # line_slice = self.center_x // self.pad_factor
