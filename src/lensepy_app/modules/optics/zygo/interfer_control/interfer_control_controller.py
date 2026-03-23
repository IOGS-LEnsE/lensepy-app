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
        if self.parent.variables['phase'] is None:
            self.phase = PhaseModel(self.data_set)
            self.parent.variables['phase'] = self.phase
        else:
            self.phase = self.parent.variables['phase']
        self.phase.prepare_data()
        self.zernike_coeffs = Zernike(self.phase)
        self.displayed_surface = '2D_unwrap'

        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        image = self.phase.cropped_images_sets.get_image_from_set(1, 1)
        self.masked_image = image * mask
        # TO DO  - default colormap in default_parameters
        self.colormap_2D = 'cividis'
        self.colormap_2D = 'plasma'
        self.corrected_phase = None
        self.unwrapped_phase = None

        # Graphical layout
        self.top_left = Surface2DView('', self.colormap_2D)
        self.bot_left = InterferControlView()
        self.bot_right = ImageDisplayWidget()
        self.top_right = SurfaceChoiceView(self)
        
        # Setup widgets
        self.bot_right.set_image_from_array(self.masked_image)
        self.process_surfaces()
        self.tilt = False
        self.wedge = 1

        # Signals
        self.top_right.surface_selected.connect(self.handle_surface_selected)
        self.top_right.tilt_changed.connect(self.handle_tilt_changed)
        self.bot_left.wedge_changed.connect(self.handle_wedge_changed)
        self.top_right.view_saved.connect(self.handle_saved)

    def init_view(self):
        super().init_view()
        self.wedge = self.bot_left.get_wedge()
        self.phase.set_wedge_factor(self.wedge)
        self.phase.prepare_data()
        self.correct_surface()
        self.handle_surface_selected(self.displayed_surface)
        self.top_right.activate_button(self.displayed_surface)

    def process_surfaces(self):
        if not self.data_set.is_wrapped():
            self.process_wrapped_phase_calculation(self.number_of_repetition)
        if not self.data_set.is_unwrapped():
            self.process_unwrapped_phase_calculation(self.number_of_repetition)
        if self.data_set.is_unwrapped() and not self.data_set.is_analyzed():
            self.zernike_coeffs.set_phase(self.phase)
            for k in range(3):
                self.process_zernike_calculation(k)
            self.data_set.set_analyzed_state()

    def correct_surface(self):
        self.unwrapped_phase = self.phase.get_unwrapped_phase()
        _, self.corrected_phase = self.zernike_coeffs.process_surface_correction(['piston', 'tilt'])
        pv, rms = process_statistics_surface(self.unwrapped_phase)
        self.bot_left.set_pv_uncorrected(pv, '\u03BB')
        self.bot_left.set_rms_uncorrected(rms, '\u03BB')
        pv, rms = process_statistics_surface(self.corrected_phase)
        self.bot_left.set_pv_corrected(pv, '\u03BB')
        self.bot_left.set_rms_corrected(rms, '\u03BB')

    def handle_saved(self, filepath):
        """Saved the current view."""
        self.top_left.save_image(filepath)

    def handle_surface_selected(self, value):
        value_split = value.split('_')
        self.displayed_surface = value
        if value_split[0] == '2D':
            if value_split[1] == 'wrap':
                self.display_2D_wrapped()
            elif value_split[1] == 'unwrap':
                self.display_2D_unwrapped()
        elif value_split[0] == '3D':
            if value_split[1] == 'wrap':
                self.display_3D_wrapped()
            elif value_split[1] == 'unwrap':
                self.display_3D_unwrapped()

    def handle_tilt_changed(self, value):
        """Action performed when the tilt checkbox changed."""
        self.tilt = value
        self.handle_surface_selected(self.displayed_surface)

    def handle_wedge_changed(self, text):
        wed_s = text.split(',')
        old_value = self.wedge
        if is_float(wed_s[1]):
            self.wedge = float(wed_s[1])
            self.phase.set_wedge_factor(float(wed_s[1]))
            self.data_set.reset_processes()
            self.process_surfaces()
            self.correct_surface()
            self.handle_surface_selected(self.displayed_surface)

    def replace_top_left_widget(self, new_widget):
        self.parent.main_window.top_left_container.deleteLater()
        self.top_left = new_widget
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def display_2D_wrapped(self):
        """
        Display Wrapped phase in 2D at the top right corner.
        """
        widget = Surface2DView('Wrapped Phase', self.colormap_2D)
        self.replace_top_left_widget(widget)
        wrapped = self.phase.get_wrapped_phase()
        wrapped_array = wrapped.filled(np.nan)
        # Display unwrapped and corrected in 2D
        self.top_left.set_title(translate('wrapped_phase'))
        self.top_left.set_array(wrapped_array)

    def display_2D_unwrapped(self, gain=1):
        """
        Display unwrapped phase in 2D at the bottom right corner.
        """
        widget = Surface2DView('Unwrapped Phase', self.colormap_2D)
        self.replace_top_left_widget(widget)
        if self.tilt:
            unwrapped_array = self.corrected_phase.filled(np.nan) * self.wedge
            title = translate('unwrapped_notilt_surface')
        else:
            unwrapped_array = self.unwrapped_phase.filled(np.nan)
            title = translate('unwrapped_surface')
        # Display unwrapped and corrected in 2D
        self.top_left.set_title(title)
        self.top_left.set_array(unwrapped_array * gain)

    def display_3D_wrapped(self, gain=1):
        widget = Surface3DView('Wrapped Phase')
        self.replace_top_left_widget(widget)
        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        wrapped = self.phase.get_wrapped_phase()
        wrapped_array = wrapped.filled(np.nan)
        Z2 = np.ma.masked_where(np.logical_not(mask), wrapped_array)
        # Gain ?
        Z1 = Z2 * gain
        x, y, w_s = self.top_left.prepare_data_for_mesh(Z1, undersampling=4)
        self.top_left.create_mesh_surface(x, y, w_s)
        self.top_left.showMaximized()
        self.top_left.raise_()

    def display_3D_unwrapped(self, gain=1):
        widget = Surface3DView('Unwrapped Phase')
        self.replace_top_left_widget(widget)
        mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        if self.tilt:
            unwrapped_array = self.corrected_phase.filled(np.nan) * self.wedge
            title = translate('unwrapped_notilt_surface')
        else:
            unwrapped_array = self.unwrapped_phase.filled(np.nan)
            title = translate('unwrapped_surface')

        Z2 = np.ma.masked_where(np.logical_not(mask), unwrapped_array)
        # Gain ?
        Z1 = Z2 * gain
        # Tilt ?
        x, y, w_s = self.top_left.prepare_data_for_mesh(Z1, undersampling=4)
        self.top_left.create_mesh_surface(x, y, w_s)
        self.top_left.showMaximized()
        self.top_left.raise_()

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