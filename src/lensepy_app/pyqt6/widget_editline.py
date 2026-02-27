# -*- coding: utf-8 -*-
"""*widget_editline* file.

*widget_editline* file that contains ...

.. note:: LEnsE - Institut d'Optique - version 0.4.7

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""
import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.css import *


class LineEditView(QWidget):

    text_changed = pyqtSignal(str)

    def __init__(self, signal_name: str, title: str = '', default_value: str = ''):
        """Default Constructor.

        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.title = title
        self.signal_name = signal_name
        self.label = QLabel(self.title)
        self.label.setStyleSheet(styleH3)
        self.text_edit = QLineEdit(default_value)
        self.text_edit.editingFinished.connect(self._changed)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_edit)

    def set_value(self, value: str):
        """Set a new value to the edit line.
        :param value: Value to set.
        """
        self.text_edit.setText(value)

    def _changed(self):
        """
        Action when the text changed.
        """
        sig_value = '' + self.signal_name + ',' + str(self.text_edit.text())
        self.text_changed.emit(sig_value)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main = LineEditView('test')
    main.text_changed.connect(lambda event: print(event))
    main.show()
    sys.exit(app.exec())
