# -*- coding: utf-8 -*-
"""Slidez Widget to use in PyQt6 applications

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/05


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python SliderBlock.py
"""

import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit
from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QLabel, QPushButton, QMessageBox, QCheckBox, QSlider
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QRect
from pyqtgraph import PlotWidget, plot, mkPen

styleH1 = "font-size:16px; padding:7px; color:Navy; border-top: 1px solid Navy;"
styleH = "font-size:14px; padding:4px; color:Navy;"
styleV = "font-size:14px; padding:2px; "


def is_number(value, min_val=0, max_val=0):
    """
    Returns true if the value is a number between min and max.

    Parameters
    ----------
    value : float
        Number to test.
    min_val : float
        Minimum of the interval to test.
    max_val : float
        Maximum of the interval to test.

    Returns
    -------
    True if number is between min and max.
    """
    min_ok = False
    max_ok = False
    value2 = str(value).replace('.', '', 1)
    value2 = value2.replace('e', '', 1)
    value2 = value2.replace('-', '', 1)
    if value2.isdigit():
        value = float(value)
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        if (min_val != '') and (int(value) >= min_val):
            min_ok = True
        if (max_val != '') and (int(value) <= max_val):
            max_ok = True
        if min_ok != max_ok:
            return False
        else:
            return True
    else:
        return False


class SliderBlock(QWidget, QObject):
    """
    SliderBlock class to create a widget with a slider and its value.
    Children of QWidget
    ---

    Attributes
    ----------
    ratio_slider : float
        Use to display non integer on the Slider.
        For example, with a ratio_slider at 10, the slider
        value of 500 corresponds to a real value of 50.0.
        Default to 10.
    max_real_value : float
        Maximum value of the slider.
    min_real_value : float
        Minimum value of the slider.
    real_value : float
        Value of the slider.
    Methods
    -------

    """

    slider_changed_signal = pyqtSignal(str)

    def __init__(self, name="", percent=False):
        super(SliderBlock, self).__init__()

        ''' Global Values '''
        self.min_real_value = 0
        self.max_real_value = 100
        self.ratio_slider = 10.0
        self.real_value = 1
        self.enabled = True
        ''' Layout Manager '''
        self.main_layout = QGridLayout()
        ''' Graphical Objects '''
        self.name = QPushButton(name)
        self.user_value = QLineEdit()
        self.name.setStyleSheet(styleH)
        self.user_value.setStyleSheet(styleH)
        self.max_slider_label = QLabel(f'{self.max_real_value}')
        self.max_slider_label.setStyleSheet(styleV)
        self.min_slider_label = QLabel(f'{self.min_real_value}')
        self.min_slider_label.setStyleSheet(styleV)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_real_value*self.ratio_slider))
        self.slider.setMaximum(int(self.max_real_value*self.ratio_slider))
        self.slider.setValue(int(self.real_value*self.ratio_slider))
        ''' '''
        self.units = ''
        self.units_label = QLabel('')

        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 3)
        self.main_layout.setColumnStretch(2, 1)

        ''' Adding GO into the widget layout '''
        self.main_layout.addWidget(self.name, 0, 0, 1, 3)  # Position 1,0 / 3 cells
        self.main_layout.addWidget(self.user_value, 1, 0, 1, 2)  # Position 1,1 / 3 cells
        self.main_layout.addWidget(self.units_label, 1, 2)
        self.main_layout.addWidget(self.min_slider_label, 2, 0)  # Position 2,0 / one cell
        self.main_layout.addWidget(self.slider, 2, 1)  # Position 2,1 / one cell
        self.main_layout.addWidget(self.max_slider_label, 2, 2)  # Position 2,0 / one cell
        self.setLayout(self.main_layout)

        ''' Events '''
        self.slider.valueChanged.connect(self.slider_changed)
        self.name.clicked.connect(self.value_changed)
        self.set_value(self.real_value)
        self.update_display()
        self.update_GUI()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name.setText(name)

    def set_enabled(self, value):
        self.enabled = value
        self.update_GUI()

    def update_GUI(self):
        self.slider.setEnabled(self.enabled)
        self.user_value.setEnabled(self.enabled)
        self.name.setEnabled(self.enabled)

    def value_changed(self, event):
        value = self.user_value.text()
        value2 = value.replace('.', '', 1)
        value2 = value2.replace('e', '', 1)
        value2 = value2.replace('-', '', 1)
        if value2.isdigit():
            self.real_value = float(value)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"Not a number")
            msg.setWindowTitle("Not a Number Value")
            msg.exec()
            self.real_value = self.min_real_value
            self.user_value.setText(str(self.real_value))
        # Test if value is between min and max
        if not is_number(self.real_value, self.min_real_value, self.max_real_value):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('This number is not in the good range')
            msg.setWindowTitle("Outside Range")
            msg.exec()
            self.real_value = self.min_real_value
            self.user_value.setText(str(self.real_value))
            self.real_value = self.min_real_value
        self.slider.setValue(int(self.real_value*self.ratio_slider))
        self.update_display()
        self.slider_changed_signal.emit('slider_changed')

    def slider_changed(self, event):
        self.real_value = self.slider.value() / self.ratio_slider
        self.update_display()
        self.slider_changed_signal.emit(self.name.text())

    def set_min_max_slider(self, min_val, max_val):
        """
        Set the minimum and maximum values of the slider.

        Parameters
        ----------
        min_val : float
            Minimum value of the slider.
        max_val : float
            Maximum value of the slider.

        """
        self.min_real_value = min_val
        self.max_real_value = max_val
        self.slider.setMinimum(int(self.min_real_value*self.ratio_slider))
        self.min_slider_label.setText(f'{int(self.min_real_value)}')
        self.slider.setMaximum(int(self.max_real_value*self.ratio_slider))
        self.max_slider_label.setText(f'{int(self.max_real_value)}')
        self.slider.setValue(int(self.min_real_value*self.ratio_slider))
        self.update_display()

    def set_units(self, units):
        self.units = units
        self.update_display()

    def update_display(self):
        display_value = self.real_value
        display_units = self.units
        if self.real_value / 1000 >= 1:
            display_value = display_value / 1000
            display_units = 'k' + self.units
        if self.real_value / 1e6 >= 1:
            display_value = display_value / 1e6
            display_units = 'M' + self.units
        self.user_value.setText(f'{display_value}')
        self.units_label.setText(f'{display_units}')

    def get_real_value(self):
        return self.slider.value()/self.ratio_slider

    def set_value(self, value):
        self.real_value = value
        self.user_value.setText(str(value))
        self.slider.setValue(int(self.real_value*self.ratio_slider))

    def set_ratio(self, value):
        self.ratio_slider = value
        self.slider.setMinimum(int(self.min_real_value * self.ratio_slider))
        self.slider.setMaximum(int(self.max_real_value * self.ratio_slider))
        self.slider.setValue(int(self.min_real_value * self.ratio_slider))
        self.update_display()


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XY Chart")
        self.setGeometry(300, 300, 300, 150)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.slider_widget = SliderBlock()
        self.slider_widget.set_min_max_slider(20, 50)
        self.slider_widget.set_units('Hz')
        self.slider_widget.set_name('Slider to test')
        self.layout.addWidget(self.slider_widget)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
