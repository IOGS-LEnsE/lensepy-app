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
from lensepy_app.appli._app.main_view import get_disp_mode
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

display_options_values = [
    translate('psf_and_slice'),
    translate('psf_only'),
    translate('psf_slice'),
    translate('ftm_and_slice'),
    translate('ftm_only'),
    translate('ftm_slice')
]


class AnalysisInProgressView(QWidget):
    """Analysis in progress."""
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.general_display_mode, self.general_theme = get_disp_mode(self.parent)
        layout = QVBoxLayout()
        self.text = translate('analysis_in_progress')
        self.label = QLabel(self.text)
        self.label.setStyleSheet(STYLE_H2[self.general_display_mode])
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self, step: 0):
        self.text = translate('analysis_in_progress')
        if step >= 1:
            self.text += '\n'+translate('analysis_phase_ok')
        if step >= 2:
            self.text += '\n'+translate('analysis_auto_mask_ok')
        if step >= 3:
            self.text += '\n'+translate('analysis_surface_ok')
        if step >= 4:
            self.text += '\n'+translate('analysis_zernike_ok')

        self.label.setText(self.text)
        self.label.repaint()


class PSFInProgressView(QWidget):
    """Analysis in progress."""
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.general_display_mode = get_disp_mode(self.parent)
        layout = QVBoxLayout()
        self.text = translate('psf_in_progress')
        self.label = QLabel(self.text)
        self.label.setStyleSheet(STYLE_H2[self.general_display_mode])
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self, step: 0):
        self.text = translate('psf_in_progress')
        if step >= 1:
            self.text += '\n'+translate('psf_phase_ok')

        self.label.setText(self.text)
        self.label.repaint()


class SurfaceOptionsView(QWidget):

    selection_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.general_display_mode, self.general_theme = get_disp_mode(self.parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.surface = Surface2DView(
                translate('interferogram'), colormap_2D='gray')
        self.options = OptionsView()

        layout.addWidget(self.surface, 4)
        layout.addWidget(self.options, 1)

        # Signals
        self.options.selection_changed.connect(self.handle_selection_changed)

    def set_surface(self, surface):
        self.surface.set_array(surface)

    def set_visible(self, index):
        self.options.set_visible(index)

    def handle_selection_changed(self, index, value):
        self.selection_changed.emit(index, value)


class OptionsView(QWidget):

    selection_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.general_display_mode, self.general_theme = get_disp_mode(self.parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.top_right_option = ComboBoxBloc(translate('top_right_option'),
                                             display_options_values,
                                             parent=self.parent,
                                             default=False,
                                             vertical=True)
        self.bot_right_option = ComboBoxBloc(translate('bot_right_option'),
                                             display_options_values,
                                             parent=self.parent,
                                             default=False,
                                             vertical=True)

        layout.addWidget(self.top_right_option)
        self.top_right_option.hide()
        layout.addWidget(make_hline())
        layout.addWidget(self.bot_right_option)
        self.bot_right_option.hide()
        layout.addStretch()

        # Signals
        self.top_right_option.selection_changed.connect(self.handle_selection_changed)
        self.bot_right_option.selection_changed.connect(self.handle_selection_changed)

    def set_visible(self, index):
        if index == 'top':
            self.top_right_option.show()
        if index == 'bot':
            self.bot_right_option.show()

    def handle_selection_changed(self):
        sender = self.sender()
        if sender == self.top_right_option:
            value = sender.get_text()
            self.selection_changed.emit('top', value)
        elif sender == self.bot_right_option:
            value = sender.get_text()
            self.selection_changed.emit('bot', value)


class TwoChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.general_display_mode = get_disp_mode(self.parent)
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


def main():

    app = QApplication(sys.argv)
    window = CoefficientsView()
    window.set_coeffs([1.01, -3.3, 2.5, 5.2, -6.7, 1.01,
                       -3.3, 2.5, 5.2, -6.7, 1.01, -3.3,
                       2.5, 5.2, -6.7, 1.01, -3.3, 2.5,
                       5.2, -0.7, 1.01, -0.3, 2.5, 5.2,
                       -6.7, 0.01, 0, 0.5, 5.2, -6.7,
                       1.01, -3.3, 2.5, 5.2, -0.7, 1.01, 0.5])
    window.set_pv_rms_uncorrected(1.5, -0.2, 'nm')
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()