# -*- coding: utf-8 -*-
"""*PVRMS_view.py* file.

./views/PVRMS_view.py contains PVRMSView class to display options for different modes.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

MINIMUM_WIDTH = 75


class PVRMSView(QWidget):
    """
    Class to display PV (Peak-to-Valley) and RMS value of a wavefront.
    """

    def __init__(self, vertical: bool = False):
        """
        Default constructor.
        """
        super().__init__()
        styleL = f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
        styleT = f"font-size:14px; padding:5px; font-weight: bold; background-color: white;"

        # PV widget
        self.PV_widget = QWidget()
        self.PV_layout = QHBoxLayout()
        self.PV_widget.setLayout(self.PV_layout)
        self.label_PV = QLabel(translate('label_PV'))
        self.label_PV.setStyleSheet(styleL)
        self.text_PV = QLabel()
        self.text_PV.setStyleSheet(styleT)
        self.text_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.text_PV.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_PV = QLabel()
        self.unit_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.PV_layout.addWidget(self.label_PV)
        self.PV_layout.addWidget(self.text_PV)
        self.PV_layout.addWidget(self.unit_PV)

        # RMS widget
        self.RMS_widget = QWidget()
        self.RMS_layout = QHBoxLayout()
        self.RMS_widget.setLayout(self.RMS_layout)
        self.label_RMS = QLabel(translate('label_RMS'))
        self.label_RMS.setStyleSheet(styleL)
        self.text_RMS = QLabel()
        self.text_RMS.setStyleSheet(styleT)
        self.text_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.text_RMS.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_RMS = QLabel()
        self.unit_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.RMS_layout.addWidget(self.label_RMS)
        self.RMS_layout.addWidget(self.text_RMS)
        self.RMS_layout.addWidget(self.unit_RMS)

        if vertical:
            self.layout = QVBoxLayout()
        else:
            self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.PV_widget)
        if not vertical:
            self.layout.addStretch()
        self.layout.addWidget(self.RMS_widget)
        if not vertical:
            self.layout.addStretch()

    def set_pv(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.text_PV.setText(str(value))
        self.unit_PV.setText(unit)

    def set_rms(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.text_RMS.setText(str(value))
        self.unit_RMS.setText(unit)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.text_PV.setText('')
        self.unit_PV.setText('')
        self.text_RMS.setText('')
        self.unit_RMS.setText('')
