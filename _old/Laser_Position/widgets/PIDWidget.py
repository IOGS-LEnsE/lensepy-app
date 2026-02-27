# -*- coding: utf-8 -*-
"""Laser Position Control Interface

PID Page

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/10


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python PIDWidget.py
"""

import sys
import time

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget,  QVBoxLayout, QGridLayout
from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox
from PyQt6.QtCore import pyqtSignal, Qt

from widgets.NucleoSerialConnectionWidget import NucleoSerialConnectionWidget
from SupOpNumTools.pyqt6.IncDecWidget import IncDecWidget

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

"""
"""
class PIDWidget(QWidget):

    pid_signal = pyqtSignal(str)

    def __init__(self, parent=None, camera=None):
        """

        """
        super().__init__()
        self.parent = parent

        self.layout = QGridLayout()

        # Camera if exists
        self.camera = camera
        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet('background-color:lightgray;')
        self.layout.addWidget(self.camera_widget, 0, 1)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.layout.addWidget(self.left_widget, 0, 0)
        # Title label
        self.title_label = QLabel('PID Real-Time Control')
        self.title_label.setStyleSheet(title_style)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.addWidget(self.title_label)

        # X = Y and sampling freq
        self.x_equal_y_check = QCheckBox('|X| = |Y|')
        self.x_equal_y_check.clicked.connect(self.x_equal_y_action)
        self.left_layout.addWidget(self.x_equal_y_check)

        self.sampling_freq_label = QLabel('Sampling Frequency (Hz)')
        self.sampling_freq_combo = QComboBox()
        self.sampling_freq_values = ['10000', '3000', '1000', '300', '100']
        self.sampling_freq_combo.addItems(self.sampling_freq_values)
        self.left_layout.addWidget(self.sampling_freq_label)
        self.left_layout.addWidget(self.sampling_freq_combo)
        self.left_layout.addStretch()

        self.title_x_label = QLabel('X Channel')
        self.title_x_label.setStyleSheet("font-size: 14px; color:indigo;")
        self.title_x_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_x_label, 1, 0)
        self.title_y_label = QLabel('Y Channel')
        self.title_y_label.setStyleSheet("font-size: 14px; color:indigo;")
        self.title_y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_y_label, 1, 1)

        self.P_X_inc_dec = IncDecWidget('Proportional Gain', limits=[0, 100])
        self.P_X_inc_dec.updated.connect(self.updated_action)
        self.layout.addWidget(self.P_X_inc_dec, 2, 0)
        self.I_X_inc_dec = IncDecWidget('Integral Factor', limits=[0, 100])
        self.I_X_inc_dec.updated.connect(self.updated_action)
        self.layout.addWidget(self.I_X_inc_dec, 3, 0)
        self.D_X_inc_dec = IncDecWidget('Derivative Factor', limits=[0, 100])
        self.D_X_inc_dec.updated.connect(self.updated_action)
        self.layout.addWidget(self.D_X_inc_dec, 4, 0)

        self.P_Y_inc_dec = IncDecWidget('Proportional Gain', limits=[0, 100])
        self.layout.addWidget(self.P_Y_inc_dec, 2, 1)
        self.I_Y_inc_dec = IncDecWidget('Integral Factor', limits=[0, 100])
        self.layout.addWidget(self.I_Y_inc_dec, 3, 1)
        self.D_Y_inc_dec = IncDecWidget('Derivative Factor', limits=[0, 100])
        self.layout.addWidget(self.D_Y_inc_dec, 4, 1)

        self.x_inverse_check = QCheckBox('Invert X')
        self.layout.addWidget(self.x_inverse_check, 5, 0)
        self.y_inverse_check = QCheckBox('Invert Y')
        self.layout.addWidget(self.y_inverse_check, 5, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 6)
        for k in range(1, 6):
            self.layout.setRowStretch(k, 1)
        self.setLayout(self.layout)

    def updated_action(self):
        if self.x_equal_y_check.checkState() == Qt.CheckState.Checked:
            self.P_Y_inc_dec.set_value(self.P_X_inc_dec.get_real_value())
            self.I_Y_inc_dec.set_value(self.I_X_inc_dec.get_real_value())
            self.D_Y_inc_dec.set_value(self.D_X_inc_dec.get_real_value())
            time.sleep(0.1)

    def x_equal_y_action(self):
        if self.x_equal_y_check.checkState() == Qt.CheckState.Checked:
            self.P_Y_inc_dec.setEnabled(False)
            self.I_Y_inc_dec.setEnabled(False)
            self.D_Y_inc_dec.setEnabled(False)
        else:
            self.P_Y_inc_dec.setEnabled(True)
            self.I_Y_inc_dec.setEnabled(True)
            self.D_Y_inc_dec.setEnabled(True)
        self.updated_action()

    def get_PID_parameters(self):
        k_x = self.P_X_inc_dec.get_real_value()
        k_y = self.P_Y_inc_dec.get_real_value()
        i_x = self.I_X_inc_dec.get_real_value()
        i_y = self.I_Y_inc_dec.get_real_value()
        d_x = self.D_X_inc_dec.get_real_value()
        d_y = self.D_Y_inc_dec.get_real_value()
        if self.x_inverse_check.checkState() == Qt.CheckState.Checked:
            k_x = -k_x
            i_x = -i_x
            d_x = -d_x
        if self.y_inverse_check.checkState() == Qt.CheckState.Checked:
            k_y = -k_y
            i_y = -i_y
            d_y = -d_y
        sampling = int(self.sampling_freq_combo.currentText())
        return k_x, k_y, i_x, i_y, d_x, d_y, sampling

# -------------------------------

class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """
    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()
        self.intro = PIDWidget()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.intro)
        self.setCentralWidget(self.widget)


# -------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())