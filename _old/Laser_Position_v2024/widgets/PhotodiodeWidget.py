# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Photodiode manual vizualisation

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
    >>> python PhotodiodeWidget.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from SupOpNumTools.pyqt6.TargetWidget import TargetWidget
from widgets.CameraUVCWidget import CameraUVCWidget

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

class PhotodiodeWidget(QWidget):
    """
        Widget used to display 4-quadrants photodiode information.
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
    photodiode_signal = pyqtSignal(str)

    def __init__(self, camera=None):
        """

        """
        super().__init__()

        self.camera = camera

        self.layout = QGridLayout()

        # Title
        self.title_label = QLabel('Photodiode Response')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(title_style)
        self.layout.addWidget(self.title_label, 0, 0)

        self.display_widget = QWidget()
        self.display_layout = QVBoxLayout()
        self.x_display = QLabel('X = ')
        self.x_display.setStyleSheet("font-size: 20px; color:blue;")
        self.x_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(self.x_display)
        self.y_display = QLabel('Y = ')
        self.y_display.setStyleSheet("font-size: 20px; color:blue;")
        self.y_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(self.y_display)
        self.display_widget.setLayout(self.display_layout)
        self.layout.addWidget(self.display_widget, 1, 0)

        self.camera_widget = QWidget() # CameraUVCWidget()
        self.camera_widget.setStyleSheet('background-color:lightgray;')
        self.layout.addWidget(self.camera_widget, 0, 1)

        self.target = TargetWidget()
        self.layout.addWidget(self.target, 1, 1)

        self.setLayout(self.layout)
        self.photodiode_signal.emit('P_Start')

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
        self.target.set_position(x, y)

    def get_position(self):
        """
        Get the position of the photodiode

        Returns:
            x, y : float - corresponding to x and y axis position
        """
        return self.target.get_position()

    def refresh_target(self):
        x, y = self.get_position()
        self.x_display.setText('X = '+str(x))
        self.y_display.setText('Y = '+str(y))
        # self.camera_widget.refresh()
        self.target.update()

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
        self.intro = PhotodiodeWidget()

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
