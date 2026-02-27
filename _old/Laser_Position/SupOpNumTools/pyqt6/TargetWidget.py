# -*- coding: utf-8 -*-
"""
Target Widget to display a 2-axis graph

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
    >>> python TargetWidget.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import pyqtSignal

# Colors
darkslategray = QColor(47, 79, 79)
gray = QColor(128, 128, 128)
lightgray = QColor(211, 211, 211)
fuschia = QColor(255, 0, 255)


class TargetWidget(QWidget):
    """
    Graphical object to display photodiode position on a target.

    ...

    Attributes
    ----------
    pos_x : float
        position on X axis of the photodiode
    pos_y : float
        position on Y axis of the photodiode

    Methods
    -------

    """

    def __init__(self, x_min = -10, x_max = 10, y_min = -10, y_max = 10):
        """
        Initialization of the target.
        """
        super().__init__()
        self.pos_x = 0
        self.pos_y = 0
        self.limit_x_max = x_max
        self.limit_x_min = x_min
        self.limit_y_max = y_max
        self.limit_y_min = y_min

    def paintEvent(self, event):
        """

        Args:
            event:

        Returns:

        """
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        center_x = width // 2
        center_y = height // 2
        painter = QPainter(self)
        main_line = QPen(darkslategray)
        main_line.setWidth(5)
        painter.setPen(main_line)
        painter.drawLine(center_x, 5, center_x, height - 5)
        painter.drawLine(5, center_y, width - 5, center_y)
        second_line = QPen(gray)
        second_line.setWidth(1)
        painter.setPen(second_line)
        for ki in range(21):
            if ki != 10:
                painter.drawLine(5 + ki * (width - 10) // 20, 5, 5 + ki * (width - 10) // 20, height - 5)
                painter.drawLine(5, 5 + ki * (height - 10) // 20, width - 5, 5 + ki * (height - 10) // 20)
        photodiode_point = QPen(fuschia)
        photodiode_point.setWidth(3)
        painter.setBrush(QBrush(fuschia))
        painter.setPen(photodiode_point)
        pos_x_real = int(center_x + self.pos_x)
        pos_y_real = int(center_y + self.pos_y)
        painter.drawEllipse(pos_x_real - 10, pos_y_real - 10, 20, 20)
        painter.drawLine(pos_x_real - 20, pos_y_real - 20, pos_x_real + 20, pos_y_real + 20)
        painter.drawLine(pos_x_real + 20, pos_y_real - 20, pos_x_real - 20, pos_y_real + 20)

        # CHANGE RATIO !!

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
        self.pos_x = x*10
        self.pos_y = y*10
        self.update()

    def get_position(self):
        """
        Get the position of the photodiode

        Returns:
            x, y : float - corresponding to x and y axis position
        """
        return self.pos_x, self.pos_y

