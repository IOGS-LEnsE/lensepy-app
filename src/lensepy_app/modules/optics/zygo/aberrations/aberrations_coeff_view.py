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
from lensepy_app.appli._app.main_view import get_disp_mode
from lensepy_app.modules.optics.zygo.interfer_control.interfer_control_view import PVRMSView
from lensepy_app.modules.optics.zygo.aberrations.aberrations_params_view import ParamsView
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


coeff_order = [1, 1, 1, 1, 3, 3, 3, 3, 3, 5, 5,
               5, 5, 5, 5, 5, 7, 7, 7, 7, 7,
               7, 7, 7, 7, 9, 9, 9, 9, 9, 9,
               9, 9, 9, 9, 9, 11]
coeff_colors = ['orange', 'lightblue', 'red', 'green', 'purple', 'magenta', 'black']

class ZernikeCoeffBar(QWidget):

    correction_changed = pyqtSignal(bool)

    def __init__(self, parent=None, title='', min_value=0, max_value=100, min_width=10):
        super().__init__(parent)
        self.parent = parent
        self.general_display_mode = get_disp_mode(self.parent)
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
        self.label.setStyleSheet(STYLE_H3[self.general_display_mode])
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


class CoefficientsView(QWidget):

    correction_changed = pyqtSignal(list)
    tilt_changed = pyqtSignal(bool)
    focus_changed = pyqtSignal(bool)
    params_windowed = pyqtSignal(bool)

    def __init__(self, parent = None, number=36):
        super().__init__()
        self.parent = parent # controller
        self.general_display_mode = get_disp_mode(self.parent)
        self.number = number
        self.range = (-2, 2)

        self.sliders = []
        self.coeffs_correction = [0] * (self.number + 1)
        self.coeffs_correction_bool = [False] * (self.number + 1)
        self.coeffs = []

        # Graphical objects
        layout = QHBoxLayout()
        self.setLayout(layout)

        ## Options Vertical bar
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        options_widget.setLayout(options_layout)
        self.label_zernike_coefficients = QLabel(translate("label_zernike_coefficients"))
        self.label_zernike_coefficients.setStyleSheet(STYLE_H1[self.general_display_mode])
        self.label_zernike_coefficients.setAlignment(Qt.AlignmentFlag.AlignCenter)
        options_layout.addWidget(self.label_zernike_coefficients)
        options_layout.addWidget(make_hline())
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
        options_layout.addWidget(self.params_button, 1)
        options_layout.addStretch()
        ## Options Vertical bar
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_widget.setLayout(results_layout)
        size = '' if self.general_display_mode == 'CLASSIC' else 's'
        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms.setStyleSheet(STYLE_H3[self.general_display_mode])
        self.pv_rms = PVRMSView(size)
        results_layout.addWidget(self.label_pv_rms)
        results_layout.addWidget(self.pv_rms)
        self.strehl_ratio = LabelWidget(translate('strehl_ratio'), size=size)
        results_layout.addWidget(self.strehl_ratio)
        results_layout.addStretch()
        ## Sliders / Gauges
        self.slider_widget = QWidget()
        self.slider_layout = QHBoxLayout()
        self.slider_widget.setLayout(self.slider_layout)

        # Position of objects
        layout.addWidget(results_widget)
        layout.addWidget(make_vline())
        layout.addWidget(options_widget)
        layout.addWidget(make_vline())
        layout.addWidget(self.slider_widget)

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
        self.params_button.setEnabled(False)
        self.params_button.setStyleSheet(INACTIVATED_)
        self.params_windowed.emit(True)

    def set_pv_rms(self, pv, rms, units=''):
        self.pv_rms.set_pv(value=pv, unit=units)
        self.pv_rms.set_rms(value=rms, unit=units)


def main():

    app = QApplication(sys.argv)
    window = CoefficientsView()
    window.set_coeffs([1.01, -3.3, 2.5, 5.2, -6.7, 1.01,
                       -3.3, 2.5, 5.2, -6.7, 1.01, -3.3,
                       2.5, 5.2, -6.7, 1.01, -3.3, 2.5,
                       5.2, -0.7, 1.01, -0.3, 2.5, 5.2,
                       -6.7, 0.01, 0, 0.5, 5.2, -6.7,
                       1.01, -3.3, 2.5, 5.2, -0.7, 1.01, 0.5])
    window.set_pv_rms(1.5, -0.2, 'nm')
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()