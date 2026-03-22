__all__ = ["ZygoInterferControlController"]

import numpy as np
from PyQt6.QtWidgets import QWidget, QDialog
from lensepy import translate, is_float
from lensepy.optics.zygo.phase import process_statistics_surface
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.interfer_control.interfer_control_view import (
    InterferControlView, SurfaceChoiceView)
from lensepy.optics.zygo import *
from lensepy_app import *
from lensepy_app.widgets.surface_2D_view import Surface2DView
from lensepy_app.widgets.double_3d_view import Surface3DView, DoubleGraph3DView


class ZygoInterferControlController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.data_set : DataSet = self.parent.variables['dataset']
        self.number_of_repetition = 1
        self.phase = PhaseModel(self.data_set)
        self.phase.prepare_data()
        self.zernike_coeffs = Zernike(self.phase)

        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        image = self.phase.cropped_images_sets.get_image_from_set(1, 1)
        self.masked_image = image * mask
        # TO DO  - default colormap in default_parameters
        self.colormap_2D = 'cividis'
        self.colormap_2D = 'plasma'

        self.w_3d_view = Surface3DView()

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = InterferControlView()
        self.bot_right = ImageDisplayWidget()
        self.top_right = SurfaceChoiceView()
        
        # Setup widgets
        self.bot_right.set_image_from_array(self.masked_image)
        if not self.data_set.is_wrapped():
            self.process_wrapped_phase_calculation(self.number_of_repetition)
        if not self.data_set.is_unwrapped():
            self.process_unwrapped_phase_calculation(self.number_of_repetition)
        if self.data_set.is_unwrapped() and not self.data_set.is_analyzed():
            self.zernike_coeffs.set_phase(self.phase)
            for k in range(3):
                self.process_zernike_calculation(k)
            self.data_set.set_analyzed_state()
            self.tilt_possible = True  # ???
        # Signals
        self.top_right.surface_selected.connect(self.handle_surface_selected)


    def handle_surface_selected(self, value):
        value_split = value.split('_')
        if value_split[0] == '2D':
            if value_split[1] == 'wrap':
                self.display_2D_wrapped()
            elif value_split[1] == 'unwrap':
                self.display_2D_unwrapped()
        elif value_split[0] == '3D':
            if value_split[1] == 'wrap':
                pass
            elif value_split[1] == 'unwrap':
                pass


    def display_2D_wrapped(self):
        """
        Display Wrapped phase in 2D at the top right corner.
        """
        wrapped = self.phase.get_wrapped_phase()
        wrapped_array = wrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.top_left.set_title(translate('wrapped_phase'))
        self.top_left.set_array(wrapped_array)

    def display_2D_unwrapped(self, gain=1):
        """
        Display unwrapped phase in 2D at the bottom right corner.
        """
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.top_left.set_title(translate('unwrapped_surface'))
        self.top_left.set_array(unwrapped_array * gain)
        pv, rms = process_statistics_surface(unwrapped_array)
        self.bot_left.set_pv_uncorrected(pv, '\u03BB')
        self.bot_left.set_rms_uncorrected(rms, '\u03BB')

    def display_2D_correction(self, gain=1):
        """
        Display correction depending on tilt checkbox value.
        """
        self.main_widget.clear_top_right()
        self.top_right_widget = Surface2DView(translate('corrected_surface'), colormap_2D=self.colormap_2D)
        self.main_widget.set_right_widget(self.top_right_widget)
        ## TO DO : update colorbar depending on the max range of TOP and BOT right area.
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)

        # Test if tilt !
        if self.top_right.is_tilt_checked():
            wedge_factor = self.phase.get_wedge_factor()
            _, corrected = self.zernike_coeffs.process_surface_correction(['piston', 'tilt'])
            corrected = corrected * wedge_factor
        else:
            corrected = unwrapped
        self.corrected_phase = corrected.filled(np.nan)
        self.top_right_widget.set_array(self.corrected_phase * gain)
        # Test if range is checked
        self.top_right_widget.reset_z_range()
        self.top_right.erase_pv_rms()
        pv, rms = process_statistics_surface(self.corrected_phase)
        self.top_right.set_pv_corrected(pv, '\u03BB')
        self.top_right.set_rms_corrected(rms, '\u03BB')
        pv, rms = process_statistics_surface(unwrapped_array)

        self.top_right.set_pv_uncorrected(pv, '\u03BB')
        self.top_right.set_rms_uncorrected(rms, '\u03BB')

    def display_3D(self, gain=1):
        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        Z2 = np.ma.masked_where(np.logical_not(mask), unwrapped_array)
        if self.options1_widget.is_tilt_checked():
            Z1 = np.ma.masked_where(np.logical_not(mask), self.corrected_phase) * gain
            self.w_3d_view.add_labels(name1='Corrected Phase', name2='Unwrapped Phase')
        else:
            Z1 = Z2 * gain
        x, y, w_s = self.w_3d_view.prepare_data_for_mesh(Z1, undersampling=4)
        self.w_3d_view.create_mesh_surface(x, y, w_s)
        self.w_3d_view.showMaximized()
        self.w_3d_view.raise_()

    def analyses_changed(self, event):
        """
        Update controller data and views when options changed.
        :param event: Signal that triggers the event.
        """
        change = event.split(',')
        if change[0] == 'tilt':
            if change[1] == 'on':
                self.display_2D_correction()
            else:
                self.display_2D_unwrapped()
        if change[0] == 'disp_3D':
            self.display_3D(gain=2)

        if change[0] == 'disp_3D_gain':
            self.display_3D(gain=10)

        if change[0] == 'wedge':
            if is_float(change[1]):
                self.phase.set_wedge_factor(float(change[1]))
                if self.submode == 'unwrappedphase_analyses':
                    self.display_2D_unwrapped()
                elif self.submode == 'correctedphase_analyses':
                    self.display_2D_correction()

    def process_wrapped_phase_calculation(self, set_number: int = 1):
        """
        Process wrapped phase from 5 images.
        :param set_number: Number of the set to process.
        """
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        if self.data_set.is_data_ready():
            self.phase.prepare_data()
            # Process Phase
            self.phase.process_wrapped_phase()
            # End of process
            self.data_set.set_wrapped_state(True)

    def process_unwrapped_phase_calculation(self, set_number: int = 1):
        """
        Process unwrapped phase from the wrapped phase.
        :param set_number: Number of the set to process.
        """
        if self.data_set.is_data_ready() and self.data_set.is_wrapped():
            # Process Phase
            self.phase.process_unwrapped_phase()
            # End of process
            self.data_set.set_unwrapped_state(True)

    def process_zernike_calculation(self, coeff: int):
        """Process Zernike coefficients for correction."""
        self.zernike_coeffs.process_zernike_coefficient(coeff)