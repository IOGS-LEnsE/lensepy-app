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




class AnalysisInProgressView(QWidget):
    """Analysis in progress."""
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.general_display_mode = get_disp_mode(self.parent)
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