# -*- coding: utf-8 -*-
"""Increment and Decrement Widget to use in PyQt6 applications

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/09/04


Authors
-------
    Julien VILLEMEJANE

Use
---
    python IncDecWidget.py
"""

import sys
import numpy

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QLineEdit
from PyQt6.QtWidgets import (QGridLayout, QVBoxLayout,
                    QLabel, QPushButton, QMessageBox, QComboBox)
from PyQt6.QtGui import QCursor

from PyQt6.QtCore import Qt, pyqtSignal

styleH1 = "font-size:16px; padding:7px; color:Navy; border-top: 1px solid Navy;"
styleH = "font-size:14px; padding:4px; color:Navy; font-weight:bold;"
styleV = "font-size:12px; padding:2px; "


class IncDecWidget(QWidget):
    """
    IncDecWidget class to create a widget with two buttons to increase and decrease
    a value.
    Children of QWidget
    ---

    Attributes
    ----------

    Methods
    -------

    """

    updated = pyqtSignal(str)

    def __init__(self, name="", percent=False, values=None, limits=None):
        """

        Args:
            name: str
                name of the IncDecWidget - display in a label
            percent: bool
                true if the value is in percent
            values: list of str(float)
                values to display as the gain of the increment
            limits: list of float
                minmum and maximum value of the widget
        """
        super().__init__()

        ''' Global Values '''
        self.ratio_gain = 1.0
        self.real_value = 0.0
        self.enabled = True
        ''' Layout Manager '''
        self.main_layout = QGridLayout()
        ''' Graphical Objects '''
        self.name = QLabel(name)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_value = QLineEdit()
        self.user_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_value.returnPressed.connect(self.new_value_action)
        self.name.setStyleSheet(styleH)
        self.user_value.setStyleSheet(styleH)
        if limits is not None:
            self.limits = limits
        else:
            self.limits = None

        self.units = ''
        self.units_label = QLabel('')
        self.units_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.inc_button = QPushButton('+ '+str(self.ratio_gain))
        self.inc_button.clicked.connect(self.increase_value)
        self.inc_button.setStyleSheet("background:#F3A13C; color:white; font-size:14px; font-weight:bold;")
        self.dec_button = QPushButton('- '+str(self.ratio_gain))
        self.dec_button.clicked.connect(self.decrease_value)
        self.dec_button.setStyleSheet("background:#3EE4FD;font-size:14px; font-weight:bold;")

        self.gain_combo = QComboBox()
        self.values_combo = ['0.001', '0.01', '0.1', '1', '10', '100', '1000']
        if values is None :
            self.gain_combo.addItems(self.values_combo)
        else:
            self.values_combo = values
            self.gain_combo.addItems(self.values_combo)
        self.mean_combo = len(self.values_combo) // 2
        self.gain_combo.setCurrentIndex(self.mean_combo)
        self.gain_combo.currentIndexChanged.connect(self.gain_changed)
        self.gain_changed()

        self.set_zero_button = QPushButton('Set to 0')
        self.set_zero_button.clicked.connect(self.clear_value)
        self.set_zero_button.setStyleSheet("font-size:10px;")

        self.main_layout.setColumnStretch(0, 2) # Dec button
        self.main_layout.setColumnStretch(1, 4) # Name
        self.main_layout.setColumnStretch(2, 1) # Value
        self.main_layout.setColumnStretch(3, 2) # Units

        ''' Adding GO into the widget layout '''
        self.main_layout.addWidget(self.dec_button, 1, 0)
        self.main_layout.addWidget(self.name, 0, 0, 1, 4)  # Position 1,0 / 3 cells
        self.main_layout.addWidget(self.user_value, 1, 1)  # Position 1,1 / 3 cells
        self.main_layout.addWidget(self.units_label, 1, 2)
        self.main_layout.addWidget(self.inc_button, 1, 3)
        self.main_layout.addWidget(self.gain_combo, 2, 3)
        self.main_layout.addWidget(self.set_zero_button, 2, 1, 1, 2)
        self.setLayout(self.main_layout)

        ''' Events '''
        # self.slider.valueChanged.connect(self.slider_changed)
        # self.name.clicked.connect(self.value_changed)
        if self.limits is not None:
            if self.limits[0] <= self.real_value <= self.limits[1]:
                self.set_value(self.real_value)
            else:
                self.real_value = self.limits[0]
                self.set_value(self.real_value)
        else:
            self.set_value(self.real_value)
        self.update_display()

    def gain_changed(self):
        new_gain = self.gain_combo.currentText()
        self.inc_button.setText('+ '+new_gain )
        self.dec_button.setText('- '+new_gain )
        self.ratio_gain = float(new_gain)

    def increase_value(self):
        if self.limits is not None:
            if self.real_value+self.ratio_gain <= self.limits[1]:
                self.real_value += self.ratio_gain
        else:
            self.real_value += self.ratio_gain
        self.update_display()
        self.updated.emit('inc')

    def decrease_value(self):
        if self.limits is not None:
            if self.real_value-self.ratio_gain >= self.limits[0]:
                self.real_value -= self.ratio_gain
        else:
            self.real_value -= self.ratio_gain
        self.update_display()
        self.updated.emit('dec')

    def new_value_action(self):
        value = self.user_value.text()
        if value.isnumeric():
            self.real_value = float(value)
            self.update_display()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name.setText(name)

    def set_enabled(self, value):
        self.enabled = value
        self.inc_button.setEnabled(value)
        self.dec_button.setEnabled(value)
        self.user_value.setEnabled(value)

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
            self.real_value = 0
            self.user_value.setText(str(self.real_value))
        self.update_display()

    def set_units(self, units):
        self.units = units
        self.update_display()

    def update_display(self):
        negative_nb = False
        if self.real_value < 0:
            negative_nb = True
            self.real_value = -self.real_value
        if self.real_value / 1000.0 >= 1:
            display_value = self.real_value / 1000.0
            display_units = 'k' + self.units
        elif self.real_value / 1e6 >= 1:
            display_value = self.real_value / 1e6
            display_units = 'M' + self.units
        else:
            display_value = self.real_value
            display_units = self.units
        self.units_label.setText(f'{display_units}')
        if negative_nb:
            display_value = -display_value
            self.real_value = -self.real_value
        display_value = numpy.round(display_value, 3)
        self.user_value.setText(f'{display_value}')

    def get_real_value(self):
        return self.real_value

    def set_value(self, value):
        self.real_value = value
        self.update_display()

    def set_gain(self, value):
        self.ratio_gain = value
        self.update_display()

    def clear_value(self):
        self.real_value = 0
        self.gain_changed()
        self.update_display()
        self.updated.emit('rst')

    def wheelEvent(self,event):
        if self.enabled:
            mouse_point = QCursor().pos()
            # print(f'Xm={mouse_point.x()} / Ym={mouse_point.y()}')
            numDegrees = event.angleDelta() / 8 / 15
            if numDegrees.y() > 0:
                self.increase_value()
            elif numDegrees.y() < 0:
                self.decrease_value()
    def set_limits(self, limits):
        '''
        Sets the limits of the value of the widget

        Args:
            limits: list of float

        '''
        self.limits = limits

# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XY Chart")
        self.setGeometry(300, 300, 300, 150)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.incdec_widget = IncDecWidget()
        self.incdec_widget.set_units('')
        self.incdec_widget.set_name('X')
        self.layout.addWidget(self.incdec_widget)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    # main.incdec_widget.set_enabled(False)
    main.incdec_widget.set_limits([-2, 6.5])
    main.show()
    sys.exit(app.exec())
