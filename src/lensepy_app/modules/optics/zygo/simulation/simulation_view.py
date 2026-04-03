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

BUTTON_WIDTH = 50

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

    def set_legend1(self, y_legend, position='top_right'):
        self.chart_1.set_legend(y_legend, position=position)

    def set_legend2(self, y_legend, position='top_right'):
        self.chart_2.set_legend(y_legend, position=position)

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
        ##
        widget_nm = QWidget()
        layout_nm = QHBoxLayout()
        widget_nm.setLayout(layout_nm)
        self.switch_scale = SwitchWidget('\u03BB','nm')
        self.wavelength_label = LineEditWidget(translate("wavelength_label"), units='nm')
        layout_nm.addWidget(self.switch_scale)
        layout_nm.addWidget(self.wavelength_label)
        self.layout.addWidget(widget_nm)
        ##
        self.layout.addWidget(make_hline())
        self.strehl_label = LabelWidget(translate("strehl_label"))
        self.layout.addWidget(self.strehl_label)
        self.layout.addWidget(make_hline())
        self.layout.addStretch()

        self.angle_button = QPushButton(translate('surface_display'))
        self.angle_button.setStyleSheet(unactived_button)
        self.angle_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)

        select_widget = QWidget()
        select_layout = QGridLayout()
        select_widget.setLayout(select_layout)

        ## BUTTONS
        self.dict_buttons = {}
        self.list_display = ['psf', 'ftm']
        self.type_display = ['2D', 'slice', '3D']
        for k, disp in enumerate(self.list_display):
            choice = ChoiceItem(select_layout, k, translate(disp), self.update_action)
            buttons = choice.get_list()
            self.dict_buttons[disp] = buttons

        # Circled
        self.circled_button = QPushButton(translate('circled_energy_display'))
        self.circled_button.setStyleSheet(unactived_button)
        self.circled_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)

        self.layout.addWidget(self.angle_button)
        self.layout.addWidget(select_widget)
        self.layout.addWidget(self.circled_button)
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
        self.circled_button.clicked.connect(self.update_action)
        self.wavelength_label.edit_changed.connect(lambda:
                                                   self.wavelength_changed.emit(self.wavelength_label.get_value()))

        # Setup Plugin

    def inactivate_buttons(self):
        self.angle_button.setStyleSheet(unactived_button)
        self.circled_button.setStyleSheet(unactived_button)
        for k, disp in enumerate(self.list_display):
            for j in range(3):
                self.dict_buttons[disp][j].setStyleSheet(unactived_button)

    def set_wavelength(self, value):
        self.wavelength_label.set_value(str(value))

    def set_strehl_ratio(self, value):
        self.strehl_label.set_value(str(value))

    def update_action(self):
        sender = self.sender()
        self.inactivate_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.angle_button:
            self.display_changed.emit('surface')
        elif sender == self.circled_button:
            self.display_changed.emit('circled')
        else:
            for k, disp in enumerate(self.list_display):
                for j in range(3):
                    if sender == self.dict_buttons[disp][j]:
                        self.display_changed.emit(f'{disp}_{self.type_display[j]}')


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


class ChoiceItem:

    def __init__(self, layout, position, base_name, handle_function):
        self.list_button = []
        label = QLabel(translate(f"{base_name}"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(styleH3)
        layout.addWidget(label, position, 0)
        button = QPushButton(translate('2D'))
        button.setStyleSheet(unactived_button)
        button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        button.setFixedWidth(BUTTON_WIDTH)
        button.clicked.connect(handle_function)
        self.list_button.append(button)
        layout.addWidget(button, position, 1)
        button = QPushButton(translate('slice'))
        button.setStyleSheet(unactived_button)
        button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        button.setFixedWidth(BUTTON_WIDTH)
        button.clicked.connect(handle_function)
        self.list_button.append(button)
        layout.addWidget(button, position, 2)
        button = QPushButton(translate('3D'))
        button.setStyleSheet(unactived_button)
        button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        button.setFixedWidth(BUTTON_WIDTH)
        button.clicked.connect(handle_function)
        self.list_button.append(button)
        layout.addWidget(button, position, 3)

    def get_list(self):
        return self.list_button


coeff_order = [1, 1, 1, 3, 3, 3, 3, 3, 5, 5,
               5, 5, 5, 5, 5, 7, 7, 7, 7, 7,
               7, 7, 7, 7, 9, 9, 9, 9, 9, 9,
               9, 9, 9, 9, 9, 11]
coeff_colors = ['orange', 'lightblue', 'red', 'green', 'cyan', 'magenta']

class CoefficientsView(QWidget):

    sliders_changed = pyqtSignal(int, float)

    def __init__(self, parent = None, number=36):
        super().__init__()
        self.parent = parent
        self.number = number
        self.range = (-5, 5)

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
        for k in range(self.number):
            slider = SliderBlocVertical(f'C{k+1}', '',self.range[0],self.range[1])
            color = coeff_colors[coeff_order[k]//2]
            slider.set_background_color(color)
            slider.slider_changed.connect(self.handle_slider_changed)
            self.sliders.append(slider)
            self.sliders[k].set_value(0)
            self.slider_layout.addWidget(self.sliders[k])
        self.update()

    def set_range(self, min, max):
        self.range = (min, max)
        for slider in self.sliders:
            slider.set_range(min, max)

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