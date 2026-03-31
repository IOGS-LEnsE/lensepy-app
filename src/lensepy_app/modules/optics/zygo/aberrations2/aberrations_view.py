# -*- coding: utf-8 -*-
"""*masks_view.py* file.

./views/masks_view.py contains MasksView class to create masks.

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
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent, QFont
from lensepy.optics.zygo.fourier_manager import FourierManager
from lensepy.images import slice_image

import numpy as np

class AberrationsChoiceView(QWidget):
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


class PSFView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()

        self.left_widget = PSFDisplayWidget(self)
        self.right_widget = PSFDisplayWidget(self)

        self.left_widget.set_title(translate("psf_aberrations"))
        self.right_widget.set_title(translate("diffraction_limit_airy"))

        self.layout.addWidget(self.left_widget)
        self.layout.addWidget(self.right_widget)

        self.setLayout(self.layout)

        bounds = self.parent.airy_view.get_bounds()
        lims = max(bounds[0]//2, bounds[1]//2)

        if not self.linked:
            fourier = FourierManager()
            coefficients, size = fourier.test_params()
            _, psf_diff_lim, psf_image = fourier.find_rf_from_coefs(coefficients, size)
        else:
            size = self.parent.size
            psf_image = self.parent.psf_image.copy()
            psf_diff_lim = self.parent.psf_diff_lim.copy()

        h, w = size
        psf_image = psf_image[h//2 - lims:h//2 + lims, w//2 - lims:w//2 + lims]
        psf_diff_lim = psf_diff_lim[h//2 - lims:h//2 + lims, w//2 - lims:w//2 + lims]

        psf_image = resize_image_ratio(psf_image, 900, 900)
        psf_diff_lim = resize_image_ratio(psf_diff_lim, 900, 900)
        self.left_widget.set_image(psf_image)
        self.right_widget.set_image(psf_diff_lim)

        if isinstance(self.parent.submenu, SubMenu):
            self.parent.submenu.enable_buttons()


class AiryView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        fourier = FourierManager()
        coefficients, size = fourier.test_params()
        rf, psf_diff, psf_image = fourier.find_rf_from_coefs(coefficients, size)

        self.rf_text = QLabel(f"Rapport de Strehl : {int(rf * 1000)//10}%")

        size = psf_image.shape
        self.slice0_abe = slice_image(psf_image, 0, False)
        self.slice45_abe = slice_image(psf_image, size[1] / size[0], False)
        self.slice90_abe = slice_image(psf_image, 0, True)
        self.slice135_abe = slice_image(psf_image, -size[0] / size[1], True)

        self.slice0_dif = slice_image(psf_diff, 0, False)
        self.slice45_dif = slice_image(psf_diff, size[1] / size[0], False)
        self.slice90_dif = slice_image(psf_diff, 0, True)
        self.slice135_dif = slice_image(psf_diff, -size[0] / size[1], True)

        self.main_layout = QVBoxLayout()

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0_abe[0], self.slice0_abe[1], self.slice0_dif[1])
        self.top_right_widget.set_array(self.slice45_abe[0], self.slice45_abe[1], self.slice45_dif[1])
        self.bot_left_widget.set_array(self.slice90_abe[0], self.slice90_abe[1], self.slice90_dif[1])
        self.bot_right_widget.set_array(self.slice135_abe[0], self.slice135_abe[1], self.slice135_dif[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0_abe[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45_abe[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90_abe[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135_abe[2]}°")

        self.layout.addWidget(self.top_left_widget, 0, 0)
        self.layout.addWidget(self.top_right_widget, 0, 1)
        self.layout.addWidget(self.bot_left_widget, 1, 0)
        self.layout.addWidget(self.bot_right_widget, 1, 1)

        self.main_layout.addLayout(self.layout)
        self.rf_text.setStyleSheet(styleH1)
        self.rf_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.rf_text)#, Qt.AlignmentFlag.AlignCenter)
        #self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def get_bounds(self):
        X, _, _ = self.top_left_widget.shorten_bounds(self.slice90_abe[0], self.slice90_abe[1])
        Y, _, _ = self.top_left_widget.shorten_bounds(self.slice0_abe[0], self.slice0_abe[1])
        return len(X), len(Y)


class MTFView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        if not self.linked:
            fourier = FourierManager()
            coefficients, size = fourier.test_params()
            _,psf_diff_lim, psf_image = fourier.find_rf_from_coefs(coefficients, size)
            mtf_image = fourier.MTF_from_PSF(psf_image)
            mtf_diff = fourier.MTF_from_PSF(psf_diff_lim)
        else:
            mtf_image = self.parent.mtf_image.copy()
            mtf_diff = self.parent.mtf_diff.copy()

        size = mtf_image.shape
        self.slice0_abe = slice_image(mtf_image, 0, False)
        self.slice45_abe = slice_image(mtf_image, size[1]/size[0], False)
        self.slice90_abe = slice_image(mtf_image, 0, True)
        self.slice135_abe = slice_image(mtf_image, -size[0]/size[1], True)

        self.slice0_dif = slice_image(mtf_diff, 0, False)
        self.slice45_dif = slice_image(mtf_diff, size[1] / size[0], False)
        self.slice90_dif = slice_image(mtf_diff, 0, True)
        self.slice135_dif = slice_image(mtf_diff, -size[0] / size[1], True)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0_abe[0], self.slice0_abe[1], self.slice0_dif[1])
        self.top_right_widget.set_array(self.slice45_abe[0], self.slice45_abe[1], self.slice45_dif[1])
        self.bot_left_widget.set_array(self.slice90_abe[0], self.slice90_abe[1], self.slice90_dif[1])
        self.bot_right_widget.set_array(self.slice135_abe[0], self.slice135_abe[1], self.slice135_dif[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0_abe[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45_abe[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90_abe[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135_abe[2]}°")

        self.layout.addWidget(self.top_left_widget, 0, 0)
        self.layout.addWidget(self.top_right_widget, 0, 1)
        self.layout.addWidget(self.bot_left_widget, 1, 0)
        self.layout.addWidget(self.bot_right_widget, 1, 1)

        self.setLayout(self.layout)

        if isinstance(self.parent.submenu, SubMenu):
            self.parent.submenu.enable_buttons()


class FocalView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        self.layout = QHBoxLayout()

        self.maximum_slider = 200
        self.minimum_slider = -200
        self.maximum_c3 = 7
        self.minimum_c3 = self.minimum_slider * self.maximum_c3/self.maximum_slider
        self.Nstep = 30
        self.color = (255, 150, 10)

        self.c3_text = QLabel(f"C3 = 0")
        self.c3_text.setFixedWidth(75)

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            self.scan = self.fourier.focal_scan(coefficients, size, self.Nstep, self.minimum_c3, self.maximum_c3)
        else:
            self.fourier = self.parent.fourier
            coefficients, size = self.parent.coefficients.copy(), self.parent.size
            self.scan = self.fourier.focal_scan(coefficients, size, self.Nstep, self.minimum_c3, self.maximum_c3)

        self.slider = QSlider()
        #self.maximum_slider = self.maximum_slider + int(coefficients[3] * self.maximum_slider/self.maximum_c3)
        #self.minimum_slider = self.minimum_slider + int(coefficients[3] * self.maximum_slider/self.maximum_c3)
        self.slider.setMaximum(self.maximum_slider)
        self.slider.setMinimum(self.minimum_slider)
        self.slider.setSliderPosition(0)#int(coefficients[3] * self.maximum_slider/self.maximum_c3))

        self.hslice = self.scan[int(self.Nstep//2), :, :]
        self.vslice = self.scan[:, self.fourier.rpupil, :]
        self.slider.valueChanged.connect(self.slider_update)

        self.hslice_display = PSFDisplayWidget()
        self.hslice = resize_image_ratio(self.hslice, 900, 900)
        self.hslice = self.hslice_display.normalize_image(self.hslice)
        self.hslice_display.set_image(self.hslice)
        self.hslice_display.set_title("coupe horizontale")

        self.vslice_display = PSFDisplayWidget()
        self.vslice = self.vslice_display.shorten_horizontal(self.vslice)
        self.vslice = resize_image(self.vslice, 900, 900)
        self.vslice = self.vslice_display.normalize_image(self.vslice)

        value = self.slider.value()
        ratio = (value - self.minimum_slider) / (self.maximum_slider - self.minimum_slider)
        vslice_copy = self.vslice_display.color_line(self.vslice, ratio, 2, self.color)
        self.vslice_display.set_image(vslice_copy)

        self.vslice_display.set_image(vslice_copy)
        self.vslice_display.set_title("coupe verticale")

        self.layout.addWidget(self.c3_text)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.hslice_display)
        self.layout.addWidget(self.vslice_display)

        self.setLayout(self.layout)

        if isinstance(self.parent.submenu, SubMenu):
            self.parent.submenu.enable_buttons()

    def slider_update(self):
        value = self.slider.value()
        ratio = (self.maximum_slider - value)/(self.maximum_slider - self.minimum_slider)
        index = int(ratio * self.Nstep) - 1
        if index < 0:
            index = 0

        self.hslice = self.scan[index, :, :]
        self.hslice = self.hslice_display.normalize_image(self.hslice)

        self.c3_text.setText(f"C3 = {round(ratio * (self.maximum_c3 - self.minimum_c3) + self.minimum_c3, 3)}")
        self.hslice = resize_image_ratio(self.hslice, 900, 900)
        self.hslice_display.set_image(self.hslice)

        vslice_copy = self.vslice_display.color_line(self.vslice, ratio, 2, self.color)
        self.vslice_display.set_image(vslice_copy)


class CircledEnergyView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        if self.linked:
            self.psf_image = self.parent.psf_image.copy()
            self.psf_diff_lim = self.parent.psf_diff_lim.copy()
        else:
            fourier = FourierManager()
            coefficients, size = fourier.test_params()
            _, self.psf_diff_lim, self.psf_image = fourier.find_rf_from_coefs(coefficients, size)

        self.layout = QHBoxLayout()

        self.display = ChartDisplayWidget(self)
        self.x_axis, self.image_data, self.diff_lim_data = self.calculate_energy()
        self.display.set_array(self.x_axis, self.image_data, self.diff_lim_data)
        self.display.set_title("Energie encerclée")

        self.layout.addWidget(self.display)

        self.setLayout(self.layout)

        if isinstance(self.parent.submenu, SubMenu):
            self.parent.submenu.enable_buttons()

    def calculate_energy(self):
        h,w = self.psf_image.shape
        radius = min(h, w)//2

        diff_lim_data = np.zeros(radius)
        image_data = np.zeros(radius)
        x_axis = np.linspace(0, radius, radius)

        x = np.arange(h) - h // 2
        y = np.arange(w) - w // 2
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)

        psf_image_copy = self.psf_image.copy()
        psf_diff_lim_copy = self.psf_diff_lim.copy()

        for r in range(radius):
            mask = R <= r
            image_data[r] = psf_image_copy[mask].sum()
            diff_lim_data[r] = psf_diff_lim_copy[mask].sum()

        return x_axis, image_data, diff_lim_data


class TreatmentOption1Widget(QWidget):

    checkBoxSignal = pyqtSignal(bool)
    buttonsSignal = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()

        self.circled_energy = CircledEnergyView(self.parent)
        self.modify_coefficients = CoefficientsView(self.parent)

        self.opened = 1

        self.label_progress_bar = QLabel(translate("treatment_progress_bar_label"))
        self.label_progress_bar.setStyleSheet(styleH2)
        #self.label_progress_bar.setStyleSheet(styleH2)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.enhance_coeffs_label = QLabel("treatment_enhance_aberrations_label")
        self.enhance_coeffs_label.setStyleSheet(styleH2)
        self.enhance_coeffs = QCheckBox()
        self.enhance_coeffs.clicked.connect(self.update)

        spacer = QSpacerItem(50, 50)

        self.circled_energy_button = QPushButton(translate("circled_energy"))
        self.circled_energy_button.setStyleSheet(unactived_button)
        self.circled_energy_button.clicked.connect(self.update)
        self.circled_energy_button.setFixedHeight(BUTTON_HEIGHT)

        self.modify_coefficients_button = QPushButton(translate("modify_coefficients"))
        self.modify_coefficients_button.setStyleSheet(unactived_button)
        self.modify_coefficients_button.clicked.connect(self.update)
        self.modify_coefficients_button.setFixedHeight(BUTTON_HEIGHT)

        self.further_actions = QLabel(translate("further_actions"))
        self.further_actions.setStyleSheet(styleH1)

        self.layout.addWidget(self.label_progress_bar)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.enhance_coeffs_label)
        self.layout.addWidget(self.enhance_coeffs)
        self.layout.addItem(spacer)
        self.layout.addWidget(self.further_actions)
        self.layout.addWidget(self.circled_energy_button)
        self.layout.addWidget(self.modify_coefficients_button)

        self.layout.addStretch()

        self.setLayout(self.layout)

    def set_progress_bar_title(self, title):
        self.label_progress_bar.setText(translate(title))

    def set_checkbox_title(self, title):
        self.enhance_coeffs_label.setText(translate(title))

    def update_treatment_progress_bar(self, progress):
        self.progress_bar.setValue(progress)

    def close(self):
        self.modify_coefficients.close()
        self.circled_energy.close()

    def update(self):
        sender = self.sender()
        match sender:
            case self.enhance_coeffs:
                self.checkBoxSignal.emit(self.enhance_coeffs.isChecked())
            case self.circled_energy_button:
                if not self.opened:
                    self.circled_energy = CircledEnergyView(self.parent)
                    self.opened = 1
                self.buttonsSignal.emit("circled_energy")
                self.close()
                self.circled_energy.show()

            case self.modify_coefficients_button:
                self.buttonsSignal.emit("coefficients")
                self.close()
                self.modify_coefficients.show()


class CoefficientsView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        if self.linked:
            self.fourier = self.parent.fourier
            self.coefficients, self.size = self.parent.coefficients.copy(), self.parent.size
            _, _, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
        else:
            self.fourier = FourierManager()
            self.coefficients, self.size = self.fourier.test_params()
            _, _, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)

        self.maximum_slider = 200
        self.minimum_slider = -200
        self.maximum_coeffs = 7
        self.minimum_coeffs = self.minimum_slider * self.maximum_coeffs / self.maximum_slider

        COEFFICIENT_DEPTH = 11  #Nombre de coefficients pris en compte à partir de C4

        self.coefficients[:4] = 0
        self.coefficients[0] = 1

        self.layout = QHBoxLayout()
        self.sliders_layout = QVBoxLayout()
        self.sliders = [QSlider(Qt.Orientation.Horizontal) for i in range(COEFFICIENT_DEPTH + 1)]
        for i,slider in enumerate(self.sliders):
            slider.setMinimum(self.minimum_slider)
            slider.setMaximum(self.maximum_slider)

            slider.setFixedWidth(175)

            coeff_index = i + 4
            coef_value = self.coefficients[coeff_index]
            ratio = (coef_value - self.minimum_coeffs) / (self.maximum_coeffs - self.minimum_coeffs)
            slider_value = int(ratio * (self.maximum_slider - self.minimum_slider) + self.minimum_slider)

            slider.blockSignals(True)
            slider.setValue(slider_value)
            slider.blockSignals(False)
            slider.valueChanged.connect(self.slider_action)
            self.sliders_layout.addWidget(slider)

        self.slider_text_layout = QVBoxLayout()
        self.slider_text = [QLabel(f"C{i+4} = {round(self.coefficients[i+4], 3)}") for i in range(COEFFICIENT_DEPTH + 1)]
        for title in self.slider_text:
            title.setFixedSize(75, 25)
            self.slider_text_layout.addWidget(title)

        self.slider_layout = QHBoxLayout()
        self.slider_layout.addLayout(self.slider_text_layout)
        self.slider_layout.addLayout(self.sliders_layout)

        self.left_layout = QVBoxLayout()
        self.zero_button = QPushButton(translate("set_zero"))
        self.zero_button.setStyleSheet(unactived_button)
        self.zero_button.setFixedHeight(BUTTON_HEIGHT)
        self.left_layout.addLayout(self.slider_layout)
        self.left_layout.addWidget(self.zero_button)

        self.zero_button.clicked.connect(self.zero_action)

        self.psf_image_display = PSFDisplayWidget()
        self.pupil_display = PSFDisplayWidget()

        psf_image = resize_image_ratio(self.psf_image, 900, 900)
        self.psf_image_display.set_image(psf_image)
        self.psf_image_display.setMaximumHeight(900)
        pupil = self.fourier.afficher_pupille(self.coefficients, self.size)
        pupil = resize_image_ratio(pupil, 900, 900)
        self.pupil_display.set_image(pupil)
        self.pupil_display.setMaximumHeight(900)
        self.psf_image_display.set_title("PSF Image")
        self.pupil_display.set_title("Défaut de phase")

        self.layout.addLayout(self.left_layout)
        #self.layout.addLayout(self.slider_text_layout)
        #self.layout.addLayout(self.sliders_layout)
        self.layout.addWidget(self.psf_image_display)
        self.layout.addWidget(self.pupil_display)

        self.setLayout(self.layout)

    def slider_action(self):
        sender = self.sender()
        for i,slider in enumerate(self.sliders):
            if sender == slider:
                value = slider.value()
                ratio = (self.maximum_slider - value) / (self.maximum_slider - self.minimum_slider)
                self.coefficients[i + 4] = ratio * (self.minimum_coeffs - self.maximum_coeffs) - self.minimum_coeffs
                self.slider_text[i].setText(f"C{i+4} = {round(self.coefficients[i+4], 3)}")
                break
        _, _, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
        psf_image = resize_image_ratio(self.psf_image, 900, 900)
        pupil = self.fourier.afficher_pupille(self.coefficients, self.size)
        pupil = resize_image_ratio(pupil, 900, 900)
        self.psf_image_display.set_image(psf_image)
        self.pupil_display.set_image(pupil)

    def zero_action(self):
        for i,slider in enumerate(self.sliders):
            slider.blockSignals(True)
            slider.setValue(0)
            slider.blockSignals(False)
            self.slider_text[i].setText(f"C{i + 4} = 0")
            self.coefficients[i+4] = 0
        _, _, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
        psf_image = resize_image_ratio(self.psf_image, 900, 900)
        pupil = self.fourier.afficher_pupille(self.coefficients, self.size)
        pupil = resize_image_ratio(pupil, 900, 900)
        self.psf_image_display.set_image(psf_image)
        self.pupil_display.set_image(pupil)


class PSFDisplayWidget(QWidget):
    def __init__(self, parent = None, set_bounds = 1):
        super().__init__()
        self.parent = parent

        self.title = QLabel("")
        self.title.setStyleSheet(styleH2)
        self.image_display = ImageDisplayWidget()

        if set_bounds:
            self.image_display.setMinimumSize(400, 400)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.image_display)

        self.setLayout(self.layout)

    def normalize_image(self, image_float):
        if image_float.dtype != np.uint8:
            min_val = image_float.min()
            max_val = image_float.max()
            if max_val > min_val:
                image_norm = (image_float - min_val) / (max_val - min_val)
            else:
                image_norm = np.zeros_like(image_float)

            image_uint8 = (image_norm * 255).astype(np.uint8)
            return image_uint8
        else:
            return image_float

    def set_image(self, image):
        image = self.normalize_image(image)
        self.image_display.set_image_from_array(image)
        self.image_display.fit_images_in_view()

    def set_title(self, title: str):
        self.title.setText(title)

    def shorten_horizontal(self, image, margin: int = 4, lower_bound: float = 1e-05):
        '''This function crops the unnecessary zeroes on the sides of an image'''
        new_image = image.copy()
        size = image.shape[1]
        i = 0
        while max(image[:, i]) < lower_bound and max(image[:, size - i - 1]) < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_image = np.delete(new_image, 0, axis=1)
                new_image = np.delete(new_image, -1, axis=1)
            i += 1
        return new_image

    def shorten_vertical(self, image, margin: int = 4, lower_bound: float = 1e-05):
        '''This function crops the unnecessary zeroes on top and bottom of an image'''
        new_image = image.copy()
        size = image.shape[0]
        i = 0
        while max(image[i, :]) < lower_bound and max(image[size - i - 1, :]) < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_image = np.delete(new_image, 0, axis=0)
                new_image = np.delete(new_image, -1, axis=0)
            i += 1
        return new_image

    def shorten_bounds(self, image, margin: int = 4, lower_bound: float = 1e-05):
        self.shorten_vertical(image, margin, lower_bound)
        self.shorten_horizontal(image, margin, lower_bound)
        return image

    """def resize_image_to(self, image, h, w, keep_proportions = True):
        '''This function can be used to create a new image that is resized to the desired height(h)
        and width(w)'''
        size = image.shape
        y_factor = h/size[0]
        x_factor = w/size[1]
        assert y_factor > 0 and x_factor > 0, "invalid arguments"
        if keep_proportions:
            factor = min(y_factor, x_factor)
            y_factor = factor
            x_factor = factor

        resized_image = np.zeros([int(y_factor*size[0]), int(x_factor*size[1])])

        sample_L_x = 1/x_factor
        sample_L_y = 1/y_factor
        for i in range(int(y_factor*size[0])):
            y_index = sample_L_y * i
            y_index_float = y_index - float(y_index)
            y_next_index = int(y_index + sample_L_y)
            if y_next_index > size[0] - 1:
                y_next_index = size[0] - 1
            for j in range(int(x_factor*size[1])):
                x_index = sample_L_x*j
                x_index_float = x_index - float(x_index)
                x_next_index = int(x_index + sample_L_x)
                if x_next_index > size[1] - 1:
                    x_next_index = size[1] - 1
                topleft = (1 - x_index_float) * (1 - y_index_float) * image[int(y_index), int(x_index)]
                topright = x_index_float * (1 - y_index_float) * image[y_next_index, int(x_index)]
                botleft = (1 - x_index_float) * y_index_float * image[int(y_index), x_next_index]
                botright = x_index_float * y_index_float * image[y_next_index, x_next_index]
                resized_image[i][j] = topleft + topright + botleft + botright

        return resized_image"""

    def toRGB(self, image):
        '''Converts a grayscale image to RGB'''
        height, width, *channels = image.shape
        if not channels or channels[0] == 1:
            image_grayscale = image.astype(np.uint8)
            image = np.stack((image_grayscale,) * 3, axis=-1)
        return image

    def color_line(self, image, ratio, height, color : tuple):
        '''draws a horizontal line from the specified color at a given ratio of the image's height'''
        modified_image = self.toRGB(image.copy())
        h = modified_image.shape[0]

        line_index_min = int(h * ratio) - height
        line_index_min = max(0, min(h - 1, line_index_min))
        line_index_max = int(h * ratio) + height
        line_index_max = max(0, min(h - 1, line_index_max))

        modified_image[line_index_min:line_index_max, :, :] = np.array(color, dtype=np.uint8)
        return modified_image


class ChartDisplayWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        PIXEL_SIZE = 3.5

        self.pixel_size = PIXEL_SIZE

        self.image_display = XYChartWidget()
        self.image_display.setMinimumSize(400, 400)
        self.image_display.set_information(translate('ChartDisplayWidget_label'))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_display)

        self.setLayout(self.layout)
    def set_array(self, X, Y, Z = None):
        self.image_display.set_background("white")
        X, Y, Z = self.shorten_bounds(X, Y, Z)
        if Z is None:
            self.image_display.set_data(X * self.pixel_size * 1e-3, Y, x_label='position(mm)')
        else:
            self.image_display.set_data(X * self.pixel_size * 1e-3, [Y, Z], x_label='position(mm)')
        self.image_display.refresh_chart()

    def set_title(self, title: str):
        self.image_display.set_title(title)

    def shorten_bounds(self, x_array, y_array, second_y=None, margin: int = 4, lower_bound: float = 1e-05):
        '''This function performs an element_wise search in a list and tries to get the external zeroes out to get a
        smoother result

        the variable margin represents the nuber of zeroes that are left out so that the plot doesn't have non-zero
        values at the boundaries
        lower_bound is the threshold under which the values are considered to be zero

        The function is also built to ensure the graph remains centered'''
        two_graphs = second_y is not None
        if not two_graphs:
            second_y = None
        new_array = y_array[:]
        size = y_array.shape[0]
        i = 0
        while y_array[i] < lower_bound and y_array[size - i - 1] < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_array = np.delete(new_array, 0)
                x_array = np.delete(x_array, 0)
                new_array = np.delete(new_array, -1)
                x_array = np.delete(x_array, -1)
                if two_graphs:
                    second_y = np.delete(second_y, 0)
                    second_y = np.delete(second_y, -1)
            i += 1
        return x_array, new_array, second_y


def main():
    app = QApplication(sys.argv)
    window = AiryView()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()