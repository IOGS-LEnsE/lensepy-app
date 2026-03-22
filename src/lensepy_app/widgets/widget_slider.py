# -*- coding: utf-8 -*-
"""*widget_slider* file.

*widget_slider* file that contains :class::WidgetSlider 

.. module:: WidgetSlider
   :synopsis: class to display a slider in PyQt6.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
from lensepy.css import *
from PyQt6.QtWidgets import (
    QMainWindow,
    QGridLayout, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QLabel, QPushButton, QSlider,
    QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt


def is_number(value, min_val=0, max_val=0):
    """Return if the value is a valid number.

    Return true if the value is a number between min and max.

    :param value: Float number to test.
    :type value: float
    :param min_val: Minimum of the interval to test.
    :type min_val: float
    :param max_val: Maximum of the interval to test.
    :type max_val: float
    :return: True if the value is between min and max.
    :rtype: bool

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


# %% Widget
class SliderBloc(QWidget):
    """
    Slider Bloc
    .. classauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
    """

    slider_changed = pyqtSignal(str)

    def __init__(self, name: str, unit: str, min_value: float, max_value: float,
                 integer: bool = False) -> None:
        """

        """
        super().__init__(parent=None)
        self.integer = integer
        self.min_value = min_value
        self.max_value = max_value
        self.value = round(self.min_value + (self.max_value - self.min_value) / 3, 2)
        if self.integer:
            self.ratio = 1
        else:
            self.ratio = 100
        self.unit = unit

        self.layout = QVBoxLayout()

        # First line: name, value and unit
        # --------------------------------
        self.subwidget_texts = QWidget()
        self.sublayout_texts = QHBoxLayout()

        self.label_name = QLabel(name + ':')
        self.label_name.setStyleSheet(styleH2)

        self.lineedit_value = QLineEdit()
        self.lineedit_value.setText(str(self.value))
        self.lineedit_value.editingFinished.connect(self.input_changed)

        self.label_unit = QLabel(unit)
        self.label_unit.setStyleSheet(styleH3)

        self.sublayout_texts.addWidget(self.label_name)
        self.sublayout_texts.addWidget(self.lineedit_value)
        self.sublayout_texts.addWidget(self.label_unit)
        self.sublayout_texts.setContentsMargins(0, 0, 0, 0)

        self.subwidget_texts.setLayout(self.sublayout_texts)

        # Second line: slider and min/max
        # -------------------------------
        self.subwidget_slider = QWidget()
        self.sublayout_slider = QHBoxLayout()

        self.label_min_value = QLabel(str(self.min_value) + ' ' + self.unit)
        self.label_min_value.setStyleSheet(styleH3)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_value * self.ratio))
        self.slider.setMaximum(int(self.max_value * self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)

        self.label_max_value = QLabel(str(self.max_value) + ' ' + self.unit)
        self.label_max_value.setStyleSheet(styleH3)

        self.sublayout_slider.addWidget(self.label_min_value)
        self.sublayout_slider.addWidget(self.slider)
        self.sublayout_slider.addWidget(self.label_max_value)
        self.sublayout_slider.setContentsMargins(0, 0, 0, 0)

        self.subwidget_slider.setLayout(self.sublayout_slider)

        # All combined
        # ------------
        self.layout.addWidget(self.subwidget_texts)
        self.layout.addWidget(self.subwidget_slider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def slider_position_changed(self):
        self.value = self.slider.value() / self.ratio
        self.slider_changed.emit(f'slider')
        self.update_block()

    def input_changed(self):
        self.value = max(self.min_value, min(self.max_value, float(self.lineedit_value.text())))
        self.update_block()

    def update_block(self):
        if self.integer:
            self.value = int(self.value)
        self.lineedit_value.setText(str(self.value))
        self.slider.setValue(int(self.value * self.ratio))

    def get_value(self):
        """Return the value of the block."""
        return self.value

    def set_value(self, value):
        """Set the value of the block."""
        if self.integer:
            self.value = int(value)
        else:
            self.value = value
        self.update_block()

    def set_min_max_slider_values(self, min_value, max_value, value=None):
        """Set the mininmum and the maximum values of the slider.

        """
        self.min_value = min_value
        self.slider.setMinimum(int(self.min_value * self.ratio))
        self.max_value = max_value
        self.slider.setMaximum(int(self.max_value * self.ratio))
        if value is not None:
            self.slider.setValue(int(value * self.ratio))
        self.label_min_value.setText(str(self.min_value) + ' ' + self.unit)
        self.label_max_value.setText(str(self.max_value) + ' ' + self.unit)

    def set_enabled(self, value):
        """Set the widget enabled if value is True."""
        self.slider.setEnabled(value)
        self.lineedit_value.setEnabled(value)


class WidgetSlider(QWidget):
    """Create a Widget with a slider.

    WidgetSlider class to create a widget with a slider and its value.
    Children of QWidget

    .. attribute:: name

        Name to display as the title.

        :type: str

    .. attribute:: ratio_slider

        Use to display non integer on the Slider.

        For example, with a ratio_slider at 10, the slider
        value of 500 corresponds to a real value of 50.0.

        :type: float

    .. attribute:: max_real_value

        Maximum value of the slider.

        :type: float

    .. attribute:: min_real_value

        Minimum value of the slider.

        :type: float

    .. attribute:: real_value

        Value of the slider.

        :type: float

    """

    slider_changed_signal = pyqtSignal(str)

    def __init__(self, name="", percent: bool = False,
                 integer: bool = False, signal_name: str = "") -> None:
        """Default constructor of the class.

        :param name: Name of the slider, defaults to "".
        :type name: str, optional
        :param percent: Specify if the slider is in percent, defaults to False.
        :type percent: bool, optional
        :param integer: Specify if the slider is an integer, defaults to False.
        :type integer: bool, optional
        :param signal_name: Name of the signal, defaults to "".
        :type percent: str, optional

        """
        super().__init__(parent=None)

        # Global values
        self.percent = percent
        self.integer = integer
        self.min_real_value = 0
        self.max_real_value = 100
        self.ratio_slider = 10.0
        self.real_value = 1
        self.enabled = True
        self.name = name
        if signal_name == '':
            self.signal_name = self.name
        else:
            self.signal_name = signal_name
        ''' Layout Manager '''
        self.main_layout = QGridLayout()
        ''' Graphical Objects '''
        self.name_label = QLabel(name)
        self.user_value = QLineEdit()
        self.max_slider_label = QLabel(f'{self.max_real_value}')
        self.min_slider_label = QLabel(f'{self.min_real_value}')
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_real_value * self.ratio_slider))
        self.slider.setMaximum(int(self.max_real_value * self.ratio_slider))
        self.slider.setValue(int(self.real_value * self.ratio_slider))
        self.units = ''
        self.units_label = QLabel('')
        self.update_button = QPushButton('Update')
        self.update_button.setEnabled(True)

        # Adding graphical objects to the main layout
        self.main_layout.addWidget(self.name_label, 0, 0, 1, 3)
        self.main_layout.addWidget(self.user_value, 0, 3)
        self.main_layout.addWidget(self.units_label, 0, 4)
        self.main_layout.addWidget(self.min_slider_label, 1, 0)
        self.main_layout.addWidget(self.slider, 1, 1, 1, 3)
        self.main_layout.addWidget(self.max_slider_label, 1, 4)
        self.main_layout.addWidget(self.update_button, 2, 3, 1, 2)
        self.setLayout(self.main_layout)

        for i in range(self.main_layout.rowCount()):
            self.main_layout.setRowStretch(i, 1)
        for i in range(self.main_layout.columnCount()):
            self.main_layout.setColumnStretch(i, 1)

        self.slider.valueChanged.connect(self.slider_changed)
        self.set_value(self.real_value)
        self.update_button.clicked.connect(self.value_changed)
        self.update_display()
        self.update_GUI()

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        self.name_label.setText(name)

    def set_enabled(self, value):
        self.enabled = value
        self.update_GUI()

    def update_GUI(self):
        self.slider.setEnabled(self.enabled)
        self.user_value.setEnabled(self.enabled)

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

        if self.integer:
            self.real_value = int(self.real_value)
        self.slider.setValue(int(self.real_value * self.ratio_slider))
        self.update_display()
        self.slider_changed_signal.emit('update:' + self.signal_name)

    def slider_changed(self, event):
        self.real_value = self.slider.value() / self.ratio_slider
        if self.integer:
            self.real_value = int(self.real_value)
        self.update_display()
        self.slider_changed_signal.emit('slider:' + self.signal_name)

    def set_min_max_slider(self, min_val: float, max_val: float) -> None:
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
        self.slider.setMinimum(int(self.min_real_value * self.ratio_slider))
        self.min_slider_label.setText(f'{int(self.min_real_value)}')
        self.slider.setMaximum(int(self.max_real_value * self.ratio_slider))
        self.max_slider_label.setText(f'{int(self.max_real_value)}')
        self.slider.setValue(int(self.min_real_value * self.ratio_slider))
        self.update_display()

    def set_units(self, units):
        self.units = units
        self.update_display()

    def update_display(self):
        display_value = self.real_value
        display_units = self.units
        if self.integer is False:
            if self.real_value / 1000 >= 1:
                display_value = display_value / 1000
                display_units = 'k' + self.units
            if self.real_value / 1e6 >= 1:
                display_value = display_value / 1e6
                display_units = 'M' + self.units
        self.user_value.setText(f'{display_value}')
        self.units_label.setText(f'{display_units}')

    def get_real_value(self):
        if self.integer:
            return int(self.slider.value() / self.ratio_slider)
        else:
            return self.slider.value() / self.ratio_slider

    def set_value(self, value):
        self.real_value = value
        self.user_value.setText(str(value))
        self.slider.setValue(int(self.real_value * self.ratio_slider))

    def set_ratio(self, value):
        self.ratio_slider = value
        self.slider.setMinimum(int(self.min_real_value * self.ratio_slider))
        self.slider.setMaximum(int(self.max_real_value * self.ratio_slider))
        self.slider.setValue(int(self.min_real_value * self.ratio_slider))
        self.update_display()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 200, 100)

            self.central_widget = QWidget()
            self.layout = QVBoxLayout()

            self.slider_widget = WidgetSlider()
            self.slider_widget.set_min_max_slider(20, 50)
            self.slider_widget.set_units('Hz')
            self.slider_widget.set_name('Slider to test')
            self.layout.addWidget(self.slider_widget)

            self.central_widget.setLayout(self.layout)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
