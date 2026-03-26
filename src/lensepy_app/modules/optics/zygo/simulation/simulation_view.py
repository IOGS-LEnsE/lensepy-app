# -*- coding: utf-8 -*-
"""
.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os, time
from lensepy import load_dictionary, translate, dictionary, is_float
from lensepy.css import *
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

class SimulationChoiceView(QWidget):
    """Images Choice."""

    analyses_changed = pyqtSignal(str)
    wedge_changed = pyqtSignal(str)

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
        self.pv_rms_uncorrected = PVRMSView(size='s')
        # PV/RMS displayed (for corrected phase)
        self.label_pv_rms_corrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_corrected.setStyleSheet(styleH3)
        self.pv_rms_corrected = PVRMSView(size='s')

        # Add graphical elements to the layout.
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addWidget(self.label_pv_rms_corrected)
        self.layout.addWidget(self.pv_rms_corrected)
        self.layout.addWidget(make_hline())
        self.layout.addStretch()
        self.layout.addWidget(make_hline())


        self.psf_button = QPushButton("PSF")
        self.psf_button.setStyleSheet(unactived_button)
        self.psf_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
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

        self.layout.addWidget(self.psf_button)
        self.layout.addWidget(self.airy_button)
        self.layout.addWidget(self.mtf_button)
        self.layout.addWidget(self.foca_button)
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
        self.psf_button.clicked.connect(self.update_action)
        self.airy_button.clicked.connect(self.update_action)
        self.mtf_button.clicked.connect(self.update_action)
        self.foca_button.clicked.connect(self.update_action)
        self.cir_button.clicked.connect(self.update_action)

        # Setup Plugin

    def inactivate_buttons(self):
        self.psf_button.setStyleSheet(unactived_button)
        self.airy_button.setStyleSheet(unactived_button)
        self.mtf_button.setStyleSheet(unactived_button)
        self.foca_button.setStyleSheet(unactived_button)
        self.cir_button.setStyleSheet(unactived_button)

    def update_action(self):
        sender = self.sender()
        self.inactivate_buttons()
        sender.setStyleSheet(actived_button)

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

    def set_pv_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_corrected.set_pv(value, unit)

    def set_rms_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_corrected.set_rms(value, unit)

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
        self.pv_rms_corrected.erase_pv_rms()


class CoefficientsView(QWidget):

    sliders_changed = pyqtSignal(int, float)

    def __init__(self, parent = None, number=36):
        super().__init__()
        self.parent = parent
        self.number = number

        self.sliders = []

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

        # Setup
        self.init_view()

    def init_view(self):
        print('Init')
        for k in range(self.number+1):
            slider = SliderBlocVertical(f'C{k}', '',-5,5)
            slider.slider_changed.connect(self.handle_slider_changed)
            self.sliders.append(slider)
            self.sliders[k].set_value(0)
            self.slider_layout.addWidget(self.sliders[k])
        self.update()

    def handle_slider_changed(self):
        sender = self.sender()
        for k, slider in enumerate(self.sliders):
            if sender == self.sliders[k]:
                value = self.sliders[k].get_value()
                self.sliders_changed.emit(k, value)

    def get_coeffs(self):
        coeffs = []
        for slider in self.sliders:
            coeffs.append(slider.get_value())
        return coeffs


def main():
    app = QApplication(sys.argv)
    window = CoefficientsView()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()