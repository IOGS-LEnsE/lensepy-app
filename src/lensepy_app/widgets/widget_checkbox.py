# -*- coding: utf-8 -*-
"""*widget_checkbox* file.

*widget_checkbox* file that contains ...

.. note:: LEnsE - Institut d'Optique - version 0.4.7

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.css import *


class CheckBoxView(QWidget):

    check_changed = pyqtSignal(str)

    def __init__(self, signal_name: str, title: str = ''):
        """Default Constructor.

        """
        super().__init__()
        self.title = title
        self.signal_name = signal_name
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.checkbox_choice = QCheckBox()
        sig_value = ''+self.signal_name+','+str(self.checkbox_choice.isChecked())
        self.checkbox_choice.stateChanged.connect(self._changed)
        self.label_choice = QLabel(self.title)
        self.label_choice.setStyleSheet(styleH3)
        self.layout.addWidget(self.checkbox_choice)
        self.layout.addWidget(self.label_choice)
        self.layout.addStretch()
        self.checkbox_choice.setEnabled(False)
        self.checkbox_choice.setChecked(False)

    def _changed(self, event):
        """
        Action when state of the checkbox changed.
        """
        sig_value = '' + self.signal_name + ',' + str(self.checkbox_choice.isChecked())
        self.check_changed.emit(sig_value)

    def set_enabled(self, value: bool = True):
        """Set enabled the checkbox.
        :param value: True or False. Default True.
        """
        self.checkbox_choice.setEnabled(value)

    def set_checked(self, value: bool = False):
        """Set checked the checkbox.
        :param value: True or False. Default True.
        """
        self.checkbox_choice.setChecked(value)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main = CheckBoxView('Test', 'Test 2')
    main.check_changed.connect(lambda event: print(event))
    main.show()
    sys.exit(app.exec())
