# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Scanner manual control Widget for central positionning

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
python CentralPositionWidget.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit
)
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

class CentralPositionWidget(QWidget):
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
    checked_limits = pyqtSignal(str)

    def __init__(self, parent=None, camera=None):
        """

        """
        super().__init__()

        self.camera = camera
        self.parent = parent
        self.x_limit_min_set = False
        self.x_limit_max_set = False
        self.y_limit_min_set = False
        self.y_limit_max_set = False
        self.x_limit_min = 0
        self.x_limit_max = 0
        self.y_limit_min = 0
        self.y_limit_max = 0

        self.layout = QGridLayout()

        # Control Panel
        self.control_widget = QWidget()
        self.control_layout = QGridLayout()
        self.control_widget.setLayout(self.control_layout)
        self.title_label = QLabel('Extrema Points for Open Loop Step Response')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(title_style)
        self.control_layout.addWidget(self.title_label, 0, 0, 1, 2)

        self.x_limit_min_button = QPushButton('Xmin = ')
        self.x_limit_min_button.clicked.connect(self.x_limit_min_action)
        self.x_limit_min_label = QLineEdit(self)
        self.x_limit_min_label.editingFinished.connect(self.action_editing_finished)
        self.x_limit_min_label.setStyleSheet('background:orange; color:black;')
        self.control_layout.addWidget(self.x_limit_min_button, 1, 0)
        self.control_layout.addWidget(self.x_limit_min_label, 1, 1)

        self.x_limit_max_button = QPushButton('Xmax = ')
        self.x_limit_max_button.clicked.connect(self.x_limit_max_action)
        self.x_limit_max_label = QLineEdit('')
        self.x_limit_max_label.setStyleSheet('background:orange; color:black;')
        self.control_layout.addWidget(self.x_limit_max_button, 2, 0)
        self.control_layout.addWidget(self.x_limit_max_label, 2, 1)

        self.y_limit_min_button = QPushButton('Ymin = ')
        self.y_limit_min_button.clicked.connect(self.y_limit_min_action)
        self.y_limit_min_label = QLineEdit('')
        self.y_limit_min_label.setStyleSheet('background:orange; color:black;')
        self.control_layout.addWidget(self.y_limit_min_button, 3, 0)
        self.control_layout.addWidget(self.y_limit_min_label, 3, 1)

        self.y_limit_max_button = QPushButton('Ymax = ')
        self.y_limit_max_button.clicked.connect(self.y_limit_max_action)
        self.y_limit_max_label = QLineEdit('')
        self.y_limit_max_label.setStyleSheet('background:orange; color:black;')
        self.control_layout.addWidget(self.y_limit_max_button, 4, 0)
        self.control_layout.addWidget(self.y_limit_max_label, 4, 1)

        self.checked_label = QLabel('NOT VALID')
        self.checked_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checked_label.setStyleSheet('background:orange;')
        self.control_layout.addWidget(self.checked_label, 5, 0, 1, 2)

        self.set_default_button = QPushButton('Set default values')
        self.set_default_button.clicked.connect(self.set_default_action)
        self.control_layout.addWidget(self.set_default_button, 6, 0, 1, 2)

        self.layout.addWidget(self.control_widget, 0, 0)

        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet('background-color:lightgray;')
        self.layout.addWidget(self.camera_widget, 0, 1)

        self.widget_target_scan = TargetSliderWidget()
        self.widget_target_scan.target_signal.connect(self.target_scan_action)
        self.layout.addWidget(self.widget_target_scan, 1, 0)

        self.widget_target_phd = TargetWidget()
        self.layout.addWidget(self.widget_target_phd, 1, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.setLayout(self.layout)

    def action_editing_finished(self):
        """Action performed when editing is finished."""
        sender = self.sender()
        if sender == self.x_limit_min_label:
            x_min = self.x_limit_min_label.text()
            print(f'X MIN = {x_min}')

    def set_default_action(self):
        """
        """
        self.x_limit_min = -0.2
        self.x_limit_min_label.setText(str(self.x_limit_min))
        self.x_limit_min_label.setStyleSheet('')
        self.x_limit_min_label.setStyleSheet('font-weight:bold;')
        self.x_limit_min_set = True

        self.x_limit_max = 0.2
        self.x_limit_max_label.setText(str(self.x_limit_max))
        self.x_limit_max_label.setStyleSheet('')
        self.x_limit_max_label.setStyleSheet('font-weight:bold;')
        self.x_limit_max_set = True

        self.y_limit_min = -0.2
        self.y_limit_min_label.setText(str(self.y_limit_min))
        self.y_limit_min_label.setStyleSheet('')
        self.y_limit_min_label.setStyleSheet('font-weight:bold;')
        self.y_limit_min_set = True

        self.y_limit_max = 0.2
        self.y_limit_max_label.setText(str(self.y_limit_max))
        self.y_limit_max_label.setStyleSheet('')
        self.y_limit_max_label.setStyleSheet('font-weight:bold;')
        self.y_limit_max_set = True
        self.check_limits()

    def update_action(self):
        nuc_board = self.parent.get_nucleo_board()
        nuc_board.set_open_loop_steps(self.x_limit_min, self.y_limit_min, self.x_limit_max, self.y_limit_max)
        self.checked_limits.emit('CheckLimits')

    def target_scan_action(self, e):
        if e == 'R': # Reset
            print('target_ reset')

    def check_limits(self):
        limits = (self.y_limit_min_set and self.y_limit_max_set
                  and self.x_limit_min_set and self.x_limit_max_set)
        if limits:
            if self.y_limit_min > self.y_limit_max: # Swap
                self.y_limit_min, self.y_limit_max = self.y_limit_max, self.y_limit_min
                self.y_limit_min_label.setText(str(self.y_limit_min))
                self.y_limit_max_label.setText(str(self.y_limit_max))
            if self.x_limit_min > self.x_limit_max: # Swap
                self.x_limit_min, self.x_limit_max = self.x_limit_max, self.x_limit_min
                self.x_limit_min_label.setText(str(self.x_limit_min))
                self.x_limit_max_label.setText(str(self.x_limit_max))
            self.checked_label.setText('VALID')
            self.update_action()
            self.checked_label.setStyleSheet('background:'+ ACTIVE_COLOR+';font-weight:bold;')

    def x_limit_min_action(self):
        x, y = self.get_scanner_position()
        self.x_limit_min_set = True
        self.x_limit_min_label.setText(str(x))
        self.x_limit_min_label.setStyleSheet('')
        self.x_limit_min_label.setStyleSheet('font-weight:bold;')
        self.x_limit_min = x
        self.check_limits()

    def x_limit_max_action(self):
        x, y = self.get_scanner_position()
        self.x_limit_max_set = True
        self.x_limit_max_label.setText(str(x))
        self.x_limit_max_label.setStyleSheet('')
        self.x_limit_max_label.setStyleSheet('font-weight:bold;')
        self.x_limit_max = x
        self.check_limits()

    def y_limit_min_action(self):
        x, y = self.get_scanner_position()
        self.y_limit_min_set = True
        self.y_limit_min_label.setText(str(y))
        self.y_limit_min_label.setStyleSheet('')
        self.y_limit_min_label.setStyleSheet('font-weight:bold;')
        self.y_limit_min = y
        self.check_limits()

    def y_limit_max_action(self):
        x, y = self.get_scanner_position()
        self.y_limit_max_set = True
        self.y_limit_max_label.setText(str(y))
        self.y_limit_max_label.setStyleSheet('')
        self.y_limit_max_label.setStyleSheet('font-weight:bold;')
        x, y = self.get_scanner_position()
        self.y_limit_max = y
        self.check_limits()

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

    def get_limits(self):
        return self.x_limit_min, self.x_limit_max, self.y_limit_min, self.y_limit_max

    def set_limits(self, x1, x2, y1, y2):
        self.x_limit_min = x1
        self.x_limit_min_set = True
        self.x_limit_min_label.setText(str(x1))
        self.x_limit_min_label.setStyleSheet('')
        self.x_limit_min_label.setStyleSheet('font-weight:bold;')
        self.x_limit_max = x2
        self.x_limit_max_set = True
        self.x_limit_max_label.setText(str(x2))
        self.x_limit_max_label.setStyleSheet('')
        self.x_limit_max_label.setStyleSheet('font-weight:bold;')
        self.y_limit_min = y1
        self.y_limit_min_set = True
        self.y_limit_min_label.setText(str(y1))
        self.y_limit_min_label.setStyleSheet('')
        self.y_limit_min_label.setStyleSheet('font-weight:bold;')
        self.y_limit_max = y2
        self.y_limit_max_set = True
        self.y_limit_max_label.setText(str(y2))
        self.y_limit_max_label.setStyleSheet('')
        self.y_limit_max_label.setStyleSheet('font-weight:bold;')
        self.check_limits()

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
        self.intro = CentralePositionWidget()

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
