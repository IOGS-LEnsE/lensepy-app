# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Empty Page

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
    >>> python EmptyWidget.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWidgets import QLabel


class EmptyWidget(QWidget):
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
    """

    def __init__(self, title=''):
        """

        """
        super().__init__()
        self.title = title

        self.layout = QVBoxLayout()
        self.title_label = QLabel('Empty Widget '+title)
        self.layout.addWidget(self.title_label)

        self.setLayout(self.layout)


# --------------------------------

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
        self.intro = EmptyWidget()

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
