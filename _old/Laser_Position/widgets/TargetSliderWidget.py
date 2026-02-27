# -*- coding: utf-8 -*-
"""
Target Widget to display a 2-axis graph with sliders

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
python TargetSliderWidget.py
"""

# Libraries to import
import sys
import numpy

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QPushButton, QLabel, QSlider
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, Qt

from SupOpNumTools.pyqt6.TargetWidget import TargetWidget

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

class TargetSliderWidget(QWidget):
    """
        Widget used to control 2 axis scanners. With 2 sliders.
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
    target_signal = pyqtSignal(str)

    def __init__(self, camera=None):
        """

        """
        super().__init__()

        self.pos_x = 0
        self.pos_y = 0
        self.ratio_slider = 10.0
        self.layout = QGridLayout()
        self.layout.setSpacing(15)

        self.target_slider = TargetWidget()
        self.target_slider.set_position(self.pos_x, self.pos_y)
        self.layout.addWidget(self.target_slider, 0, 2)
        self.layout.setColumnStretch(2, 5)
        self.layout.setRowStretch(0, 5)

        self.target_scan_x_value = QLabel('X = ')
        self.target_scan_x_value.setStyleSheet('font-size:15px; font-weight:bold;')
        self.target_scan_x_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.target_scan_x_value, 2, 2)
        self.target_scan_y_value = QLabel('Y = ')
        self.target_scan_y_value.setStyleSheet('font-size:15px; font-weight:bold;')
        self.target_scan_y_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.target_scan_y_value, 0, 0)
        self.target_slider_x_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.target_slider_x_slider.setMinimum(-100)
        self.target_slider_x_slider.setMaximum(100)
        self.target_slider_x_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.target_slider_x_slider.setTickInterval(10)
        self.target_slider_x_slider.setValue(self.pos_x)
        self.target_slider_x_slider.sliderMoved.connect(self.slider_moved)
        self.layout.addWidget(self.target_slider_x_slider, 1, 2)

        self.target_slider_y_slider = QSlider(Qt.Orientation.Vertical, self)
        self.target_slider_y_slider.setMinimum(-100)
        self.target_slider_y_slider.setMaximum(100)
        self.target_slider_y_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.target_slider_y_slider.setTickInterval(10)
        self.target_slider_y_slider.setValue(self.pos_y)
        self.target_slider_y_slider.sliderMoved.connect(self.slider_moved)
        self.layout.addWidget(self.target_slider_y_slider, 0, 1)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_action)
        self.layout.addWidget(self.reset_button, 2, 0)

        self.setLayout(self.layout)
        self.reset_action()

    def reset_action(self):
        self.pos_x = 0
        self.pos_y = 0
        self.target_slider_x_slider.setValue(self.pos_x)
        self.target_slider_y_slider.setValue(self.pos_y)
        self.refresh_graph()
        self.target_signal.emit('R')
    def slider_moved(self):
        self.pos_x = numpy.round(self.target_slider_x_slider.value()/self.ratio_slider, 1)
        self.pos_y = numpy.round(self.target_slider_y_slider.value()/self.ratio_slider, 1)
        self.refresh_graph()

    def refresh_graph(self):
        self.target_scan_x_value.setText('X = '+str(self.pos_x))
        self.target_scan_y_value.setText('Y = '+str(self.pos_y))
        self.target_slider.set_position(int(self.pos_x), -int(self.pos_y))
        self.refresh_target()

    def refresh_target(self):
        self.target_slider.update()

    def get_x_value(self):
        return self.pos_x

    def get_y_value(self):
        return self.pos_y

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
        self.intro = TargetSliderWidget()

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
