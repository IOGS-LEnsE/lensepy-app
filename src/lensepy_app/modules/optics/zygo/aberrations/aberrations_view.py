# -*- coding: utf-8 -*-
"""
.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os, time
from lensepy import load_dictionary, translate, dictionary, is_float
from lensepy.css import *
from lensepy_app.widgets import Surface2DView
from lensepy_app.widgets.objects import *
from lensepy_app import make_hline
from lensepy_app.widgets.objects import *
from lensepy_app.modules.optics.zygo.interfer_control.interfer_control_view import PVRMSView
from PyQt6.QtWidgets import (
    QDialog, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QVBoxLayout, QGridLayout,
    QApplication,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QSlider
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent, QFont
from lensepy.optics.zygo.fourier_manager import FourierManager
from lensepy.images import slice_image

import numpy as np
from urllib3.connection import VerifiedHTTPSConnection


class TwoChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_1 = XYChartWidget()
        self.chart_2 = XYChartWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.chart_1)
        layout.addWidget(self.chart_2)
        self.setLayout(layout)

    def set_background(self, color):
        self.chart_1.set_background(color)
        self.chart_2.set_background(color)

    def set_data1(self, x_axis, y_axis, x_label: str = '', y_label: str = ''):
        self.chart_1.set_data(x_axis, y_axis, x_label, y_label)

    def set_legend1(self, y_legend, x=0, y=0):
        self.chart_1.set_legend(y_legend, x, y)

    def set_legend2(self, y_legend, x=0, y=0):
        self.chart_2.set_legend(y_legend, x, y)

    def set_data2(self, x_axis, y_axis, x_label: str = '', y_label: str = ''):
        self.chart_2.set_data(x_axis, y_axis, x_label, y_label)

    def set_title1(self, title):
        self.chart_1.set_title(title)

    def set_title2(self, title):
        self.chart_2.set_title(title)

    def refresh_chart(self):
        self.chart_1.refresh_chart()
        self.chart_2.refresh_chart()

class SimulationChoiceView(QWidget):
    """Images Choice."""

    display_changed = pyqtSignal(str)
    wedge_changed = pyqtSignal(str)
    wavelength_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller = parent
        self.tilt_on = False
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_aberrations_options = QLabel(translate("label_aberrations_options"))
        self.label_aberrations_options.setStyleSheet(styleH1)
        self.label_aberrations_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_aberrations_options)

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH3)
        self.pv_rms_uncorrected = PVRMSView()
        # PV/RMS displayed (for corrected phase)
        self.label_pv_rms_corrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_corrected.setStyleSheet(styleH3)
        self.pv_rms_corrected = PVRMSView()

        # Add graphical elements to the layout.
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addWidget(make_hline())
        self.layout.addStretch()
        self.layout.addWidget(make_hline())
        self.wavelength_label = LineEditWidget(translate("wavelength_label"), units='nm')
        self.layout.addWidget(self.wavelength_label)
        self.switch_scale = SwitchWidget('\u03BB','nm')
        self.layout.addWidget(self.switch_scale)
        self.layout.addWidget(make_hline())
        self.layout.addStretch()

        self.angle_button = QPushButton("surface_display")
        self.angle_button.setStyleSheet(unactived_button)
        self.angle_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.psf_button = QPushButton("PSF")
        self.psf_button.setStyleSheet(unactived_button)
        self.psf_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.psf_slice_button = QPushButton("PSF Slice")
        self.psf_slice_button.setStyleSheet(unactived_button)
        self.psf_slice_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.airy_button = QPushButton("Airy")
        self.airy_button.setStyleSheet(unactived_button)
        self.airy_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.mtf_button = QPushButton("MTF")
        self.mtf_button.setStyleSheet(unactived_button)
        self.mtf_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.foca_button = QPushButton("Focal view")
        self.foca_button.setStyleSheet(unactived_button)
        self.foca_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.cir_button = QPushButton("Circled energy")
        self.cir_button.setStyleSheet(unactived_button)
        self.cir_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)

        self.layout.addWidget(self.angle_button)
        self.layout.addWidget(self.psf_button)
        self.layout.addWidget(self.psf_slice_button)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.airy_button)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.mtf_button)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.foca_button)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.cir_button)
        self.layout.addWidget(make_hline())
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.submenu = QWidget()
        '''
        self.airy_view = AiryView(self)
        self.psf_view = PSFView(self)
        self.mtf_view = MTFView(self)
        self.focal_view = FocalView(self)
        self.cir_view = CircledEnergyView(self)
        '''
        self.angle_button.clicked.connect(self.update_action)
        self.psf_button.clicked.connect(self.update_action)
        self.psf_slice_button.clicked.connect(self.update_action)
        self.airy_button.clicked.connect(self.update_action)
        self.mtf_button.clicked.connect(self.update_action)
        self.foca_button.clicked.connect(self.update_action)
        self.cir_button.clicked.connect(self.update_action)
        self.wavelength_label.edit_changed.connect(lambda:
                                                   self.wavelength_changed.emit(self.wavelength_label.get_value()))

        # Setup Plugin

    def inactivate_buttons(self):
        self.angle_button.setStyleSheet(unactived_button)
        self.psf_button.setStyleSheet(unactived_button)
        self.psf_slice_button.setStyleSheet(unactived_button)
        self.airy_button.setStyleSheet(unactived_button)
        self.mtf_button.setStyleSheet(unactived_button)
        self.foca_button.setStyleSheet(unactived_button)
        self.cir_button.setStyleSheet(unactived_button)

    def set_wavelength(self, value):
        self.wavelength_label.set_value(str(value))

    def update_action(self):
        sender = self.sender()
        self.inactivate_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.angle_button:
            self.display_changed.emit('surface')
        elif sender == self.psf_button:
            self.display_changed.emit('PSF')
        elif sender == self.psf_slice_button:
            self.display_changed.emit('PSF_slice')
        elif sender == self.airy_button:
            self.display_changed.emit('airy')


    def set_pv_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_uncorrected.set_pv(value, unit)

    def set_rms_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_uncorrected.set_rms(value, unit)

    def _clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.pv_rms_uncorrected.erase_pv_rms()


coeff_order = [1, 1, 1, 1, 3, 3, 3, 3, 3, 5, 5,
               5, 5, 5, 5, 5, 7, 7, 7, 7, 7,
               7, 7, 7, 7, 9, 9, 9, 9, 9, 9,
               9, 9, 9, 9, 9, 11]
coeff_colors = ['orange', 'lightblue', 'red', 'green', 'purple', 'magenta', 'black']

class CoefficientsView(QWidget):

    correction_changed = pyqtSignal(list)
    tilt_changed = pyqtSignal(bool)
    focus_changed = pyqtSignal(bool)

    def __init__(self, parent = None, number=36):
        super().__init__()
        self.parent = parent
        self.number = number
        self.range = (-5, 5)

        self.sliders = []
        self.coeffs_correction = [0] * (self.number + 1)
        self.coeffs_correction_bool = [False] * (self.number + 1)
        self.coeffs = []
        self.params_window = ParametersView()

        # Graphical objects
        layout = QVBoxLayout()
        self.setLayout(layout)

        ## Title of the widget
        layout.addWidget(make_hline())
        self.label_zernike_coefficients = QLabel(translate("label_zernike_coefficients"))
        self.label_zernike_coefficients.setStyleSheet(styleH1)
        self.label_zernike_coefficients.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_zernike_coefficients)
        layout.addWidget(make_hline())
        self.slider_widget = QWidget()
        self.slider_layout = QHBoxLayout()
        self.slider_widget.setLayout(self.slider_layout)
        layout.addWidget(self.slider_widget)
        layout.addWidget(make_hline())

        ## Horizontal bar with options
        options_widget = QWidget()
        options_layout = QHBoxLayout()
        options_widget.setLayout(options_layout)
        self.tilt_button = QCheckBox(translate("tilt_button"))
        self.tilt_button.setMinimumWidth(100)
        self.tilt_button.stateChanged.connect(self.handle_tilt_changed)
        self.focus_button = QCheckBox(translate("focus_button"))
        self.focus_button.setMinimumWidth(100)
        self.focus_button.stateChanged.connect(self.handle_focus_changed)
        options_layout.addWidget(self.tilt_button, 1)
        options_layout.addWidget(self.focus_button, 1)
        self.coeffs_button = QPushButton(translate("coeffs_button"))
        self.coeffs_button.setStyleSheet(unactived_button)
        self.coeffs_button.setMinimumWidth(100)
        self.params_button = QPushButton(translate("parameters_button"))
        self.params_button.setStyleSheet(unactived_button)
        self.params_button.clicked.connect(self.handle_parameters_view)
        self.params_button.setMinimumWidth(100)
        options_layout.addWidget(self.coeffs_button, 1)
        options_layout.addWidget(self.params_button, 2)

        layout.addWidget(options_widget)

        # Setup
        self.init_view()

    def init_view(self):
        for k in range(self.number+1):
            gauge = ZernikeCoeffBar(title=f'C{k}', min_value=self.range[0], max_value=self.range[1], min_width=10)
            color = coeff_colors[coeff_order[k]//2]
            gauge.set_colors(BLUE_IOGS, color)
            gauge.set_colors('#FFFFFF', color)
            self.sliders.append(gauge)
            if k != 0:
                gauge.correction_changed.connect(self.handle_correction_changed)
            self.sliders[k].set_value(0)
            self.slider_layout.addWidget(self.sliders[k])
        self.sliders[0].set_value(0)
        self.sliders[0].set_checked(False)
        self.sliders[0].setEnabled(False)
        self.update()

    def _update_checked(self):
        self.coeffs_correction = []
        # Update check boxes
        for k in range(self.number+1):
            self.coeffs_correction_bool[k] = False
            if not self.sliders[k].is_checked():
                self.coeffs_correction_bool[k] = True
                self.coeffs_correction.append(k)
            else:
                self.coeffs_correction_bool[k] = False
        self.auto_set_range()
        # Update bar values
        for k in range(self.number+1):
            if not self.sliders[k].is_checked():
                self.sliders[k].set_value(0)
            else:
                self.sliders[k].set_value(self.coeffs[k])
        self.update()

    def handle_tilt_changed(self):
        # Specific correction for tilt and focus
        if self.tilt_button.isChecked():
            self.sliders[1].set_checked(False)
            self.sliders[2].set_checked(False)
            self.sliders[1].setEnabled(False)
            self.sliders[2].setEnabled(False)
        else:
            self.sliders[1].set_checked(True)
            self.sliders[2].set_checked(True)
            self.sliders[1].setEnabled(True)
            self.sliders[2].setEnabled(True)
        self.tilt_changed.emit(self.tilt_button.isChecked())

    def handle_focus_changed(self):
        # Specific correction for tilt and focus
        if self.focus_button.isChecked():
            self.sliders[3].set_checked(False)
            self.sliders[3].setEnabled(False)
        else:
            self.sliders[3].set_checked(True)
            self.sliders[3].setEnabled(True)
        self.focus_changed.emit(self.focus_button.isChecked())

    def handle_correction_changed(self):
        # Action performed when a coefficient is clicked for correction.
        self._update_checked()
        self.correction_changed.emit(self.coeffs_correction)

    def set_coeffs(self, coeffs):
        """Set a list of coefficients."""
        self.coeffs = coeffs
        self.coeffs_correction = coeffs.copy()
        self._update_checked()
        for i in range(self.number+1):
            if self.coeffs_correction_bool[i]:
                self.sliders[i].set_value(self.coeffs[i])
            else:
                self.sliders[i].set_value(0)
        self.auto_set_range()
        self.handle_correction_changed()
        self.update()

    def set_range(self, min, max):
        self.range = (min, max)
        for slider in self.sliders:
            slider.set_range(min, max)

    def auto_set_range(self):
        coeffs_abs = np.abs(np.array(self.coeffs))
        coeffs_abs[0] = 0
        for k, coeff in enumerate(self.coeffs_correction_bool):
            if coeff is True:
                coeffs_abs[k] = 0
        coeffs_max = np.max(coeffs_abs)
        #coeffs_max = np.ceil(coeffs_max)
        self.set_range(-coeffs_max, coeffs_max)

    def get_coeffs(self):
        coeffs = []
        for slider in self.sliders:
            coeffs.append(slider.get_value())
        return coeffs

    def handle_parameters_view(self):
        print('handle_parameters_view')
        self.params_window.show()


class ZernikeCoeffBar(QWidget):

    correction_changed = pyqtSignal(bool)

    def __init__(self, parent=None, title='', min_value=0, max_value=100, min_width=10):
        super().__init__(parent)
        self.title = title
        self.min_value = min_value
        self.max_value = max_value

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.bg_color = BLUE_IOGS
        self.fg_color = ORANGE_IOGS

        # Label au-dessus
        self.label = QLabel(self.title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(styleH3)
        layout.addWidget(self.label)

        # Vertical Bar
        self.progress = VerticalCenteredGauge(min_width=min_width, min_height=100, min_value=min_value, max_value=max_value)
        self.progress.set_colors(self.bg_color, self.fg_color)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Check box
        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(True)
        self.checkbox.checkStateChanged.connect(self.handle_correction)
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def handle_correction(self):
        self.correction_changed.emit(self.checkbox.isChecked())

    def set_colors(self, bg_color, fg_color):
        self.progress.set_colors(bg_color, fg_color)

    def set_value(self, value):
        self.progress.set_value(value)

    def set_range(self, min, max):
        self.progress.set_range(min, max)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked=True):
        self.checkbox.setChecked(checked)


class AberrationsView(QWidget):
    def __init__(self, parent=None, colormap='plasma'):
        super().__init__(parent)
        m_layout = QVBoxLayout()
        widget1 = QWidget()
        layout1 = QHBoxLayout()
        widget1.setLayout(layout1)
        widget2 = QWidget()
        layout2 = QHBoxLayout()
        widget2.setLayout(layout2)
        m_layout.addWidget(widget1)
        m_layout.addWidget(widget2)
        self.setLayout(m_layout)

        self.unwrapped_surface = Surface2DView(translate('unwrapped_surface_no_correction'), colormap)
        layout1.addWidget(self.unwrapped_surface)
        self.unwrapped_surface_corr = Surface2DView(translate('unwrapped_surface_correction'), colormap)
        layout1.addWidget(self.unwrapped_surface_corr)

        self.psf_unwrapped = Surface2DView(translate('psf_unwrapped_surface'), colormap)
        layout2.addWidget(self.psf_unwrapped)
        self.psf_corrected = Surface2DView(translate('psf_corrected_surface'), colormap)
        layout2.addWidget(self.psf_corrected)

    def set_array_uncorrect(self, image):
        self.unwrapped_surface.set_array(image)

    def set_array_correct(self, image):
        self.unwrapped_surface_corr.set_array(image)

    def set_psf_uncorrect(self, surface):
        self.psf_unwrapped.set_array(surface)

    def reset_z_range(self):
        self.unwrapped_surface.reset_z_range()
        self.unwrapped_surface_corr.reset_z_range()

    def set_title_uncorrect(self, title):
        self.unwrapped_surface.set_title(title)

    def set_title_correct(self, title):
        self.unwrapped_surface_corr.set_title(title)


class ParametersView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)
        title_label = QLabel(translate('aberrations_params_label'))
        layout.addWidget(title_label)


def main():
    app = QApplication(sys.argv)
    window = CoefficientsView()
    window.set_coeffs([1.01, -3.3, 2.5, 5.2, -6.7, 1.01,
                       -3.3, 2.5, 5.2, -6.7, 1.01, -3.3,
                       2.5, 5.2, -6.7, 1.01, -3.3, 2.5,
                       5.2, -0.7, 1.01, -0.3, 2.5, 5.2,
                       -6.7, 0.01, 0, 0.5, 5.2, -6.7,
                       1.01, -3.3, 2.5, 5.2, -0.7, 1.01, 0.5])
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()