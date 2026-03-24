# -*- coding: utf-8 -*-
"""
.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2026
"""
import sys, os, time
from lensepy import load_dictionary, translate, dictionary, is_float
from lensepy.css import *
from networkx.algorithms.distance_measures import radius

from lensepy_app.widgets.objects import *
from PyQt6.QtWidgets import (
    QDialog, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent, QFont


class AcquisitionView(QWidget):
    """Acquisition View."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__(None)
        self.controller = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.layout.addWidget(make_hline())
        self.label_acquisition = QLabel(translate("label_acquisition"))
        self.label_acquisition.setStyleSheet(styleH2)
        self.label_acquisition.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_acquisition)
        self.layout.addWidget(make_hline())

        self.layout.addStretch()

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


class CameraParamsView(QWidget):
    """Camera Parameters View."""

    exposure_changed = pyqtSignal(float)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__(None)
        self.controller = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.layout.addWidget(make_hline())
        self.label_camera_params= QLabel(translate("label_camera_params"))
        self.label_camera_params.setStyleSheet(styleH2)
        self.label_camera_params.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_camera_params)
        self.layout.addWidget(make_hline())
        self.slider_expo = SliderBloc(translate('slider_exposure'), 'ms', 0, 2000, integer=True)
        self.layout.addWidget(self.slider_expo)
        self.layout.addStretch()

        # Signals
        self.slider_expo.slider_changed.connect(lambda value: self.exposure_changed.emit(value))


class PiezoControlView(QWidget):
    """Piezo Control View."""

    voltage_changed = pyqtSignal(float)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__(None)
        self.controller = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.layout.addWidget(make_hline())
        mini_widget = QWidget()
        mini_layout = QHBoxLayout()
        mini_widget.setLayout(mini_layout)
        self.label_piezo_control = QLabel(translate("label_piezo_control"))
        self.label_piezo_control.setStyleSheet(styleH2)
        self.label_piezo_control.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mini_layout.addWidget(self.label_piezo_control)
        self.circle_ok = CircleWidget(diameter=20)
        mini_layout.addStretch()
        mini_layout.addWidget(self.circle_ok)
        self.layout.addWidget(mini_widget)
        self.layout.addWidget(make_hline())
        self.slider = SliderBloc(translate('slider_piezo'), 'V', 0, 5)
        self.layout.addWidget(self.slider)
        self.layout.addStretch()

        # Signals
        self.slider.slider_changed.connect(lambda value: self.voltage_changed.emit(value))

