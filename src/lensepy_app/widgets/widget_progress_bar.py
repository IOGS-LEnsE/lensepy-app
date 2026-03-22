# -*- coding: utf-8 -*-
"""*widget_progress_bar* file.

*widget_progress_bar* file that contains ...

.. note:: LEnsE - Institut d'Optique - version 0.4.7

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""
import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from lensepy.css import *


class ProgressBarView(QWidget):

    def __init__(self, title: str = ''):
        """
        Default Constructor.
        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.title = title
        self.label_progress_bar = QLabel(self.title)
        self.label_progress_bar.setStyleSheet(styleH2)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_progress_bar)
        self.layout.addWidget(self.progress_bar)

    def update_progress_bar(self, value: int):
        """
        Update the progress bar value.
        :param value: Value to update to the progress bar.
        """
        self.progress_bar.setValue(value)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main = ProgressBarView('Zernike Coeffs')
    main.update_progress_bar(57)
    main.show()
    sys.exit(app.exec())
