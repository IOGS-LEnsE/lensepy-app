# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Scanner manual control Widget

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/09/01


Authors
-------
    Julien VILLEMEJANE

Use
---
python ScannerWidget.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, Qt

from SupOpNumTools.pyqt6.TargetWidget import TargetWidget
from widgets.TargetSliderWidget import TargetSliderWidget

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

class ScannerWidget(QWidget):
    """
        Widget used to control 2 axis scanners.
        Children of QWidget - QWidget can be put in another widget and / or window
        ---

        Attributes
        ----------
        layout : QLayout
            layout of the widget
        title_label : QLabel
            label to display informations
        target : PhotodiodeTarget
            widget to display photodiode position in a target
    """
    actuator_signal = pyqtSignal(str)

    def __init__(self, camera=None):
        """

        """
        super().__init__()

        self.camera = camera

        self.layout = QGridLayout()

        # Control Panel
        self.control_widget = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_widget.setLayout(self.control_layout)
        self.title_label = QLabel('Scanner Manual Control')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(title_style)
        self.control_layout.addWidget(self.title_label)

        self.layout.addWidget(self.control_widget, 0, 0)

        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet('background-color:lightgray;')
        self.layout.addWidget(self.camera_widget, 0, 1)

        self.widget_target_scan = TargetSliderWidget()
        self.layout.addWidget(self.widget_target_scan, 1, 0)

        self.widget_target_phd = TargetWidget()
        self.layout.addWidget(self.widget_target_phd, 1, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.setLayout(self.layout)

    def set_position(self, x, y):
        """
        Set the position to display on the target

        Parameters
        ----------
        x : float
            position on x axis
        y : float
            position on y axis

        Returns:
            change the position on the graphical target
        """
        self.widget_target_phd.set_position(x, y)

    def refresh_target(self):
        self.widget_target_phd.update()

    def get_scanner_position(self):
        return self.widget_target_scan.get_x_value(), self.widget_target_scan.get_y_value()

# -------------------------------

# Colors
darkslategray = QColor(47, 79, 79)
gray = QColor(128, 128, 128)
lightgray = QColor(211, 211, 211)
fuschia = QColor(255, 0, 255)


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
        self.intro = ScannerWidget()

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
