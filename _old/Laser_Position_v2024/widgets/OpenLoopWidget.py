# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Open Loop Step response control Widget

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
    >>> python OpenLoopWidget.py
"""

# Libraries to import
import sys
import numpy

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QPushButton, QLabel, QComboBox
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, Qt

from SupOpNumTools.pyqt6.XYChartWidget import XYChartWidget

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

class OpenLoopWidget(QWidget):
    """
        Widget used to start and display step response of the system.
        Children of QWidget - QWidget can be put in another widget and / or window
        ---

        Attributes
        ----------
        layout : QLayout
            layout of the widget
        title_label : QLabel
            label to display informations
    """
    step_response = pyqtSignal(str)

    def __init__(self, parent=None, camera=None):
        """

        """
        super().__init__()

        self.parent = parent
        self.data_ready = False
        self.x_data = None
        self.y_data = None
        self.s_data = None

        self.layout = QGridLayout()

        # Control Panel
        self.control_widget = QWidget()
        self.control_layout = QGridLayout()
        self.control_widget.setLayout(self.control_layout)
        self.title_label = QLabel('Open Loop Step Response')
        self.title_label.setStyleSheet(title_style)
        self.control_layout.addWidget(self.title_label, 0, 0, 1, 2)

        self.samples_label = QLabel('Number of samples')
        self.control_layout.addWidget(self.samples_label, 1, 1)
        self.samples_combo = QComboBox()
        self.samples_values = ['100', '200', '500']
        self.samples_combo.addItems(self.samples_values)
        self.control_layout.addWidget(self.samples_label, 1, 0)
        self.control_layout.addWidget(self.samples_combo, 1, 1)

        self.sampling_label = QLabel('Sampling Freq (Hz)')
        self.control_layout.addWidget(self.sampling_label, 1, 1)
        self.sampling_combo = QComboBox()
        self.sampling_values = ['10000', '5000', '1000', '500']
        self.sampling_combo.addItems(self.sampling_values)
        self.control_layout.addWidget(self.sampling_label, 2, 0)
        self.control_layout.addWidget(self.sampling_combo, 2, 1)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_action)
        self.control_layout.addWidget(self.start_button, 3, 0)
        self.data_ready_label = QLabel('NO DATA')
        self.data_ready_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_ready_label.setStyleSheet(not_style)
        self.control_layout.addWidget(self.data_ready_label, 3, 1)

        self.layout.addWidget(self.control_widget, 0, 0)

        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet('background-color:lightgray;')
        self.layout.addWidget(self.camera_widget, 0, 1)

        # Graphe
        self.graph_widget = XYChartWidget()
        self.graph_widget.set_title('Step Response')
        self.graph_widget.set_information('This is a test')
        self.graph_widget.set_background('white')
        self.layout.addWidget(self.graph_widget, 1, 0, 1, 2)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)
        self.setLayout(self.layout)

    def start_action(self):
        self.step_response.emit('L_Start')
        self.data_ready_label.setText('IN PROGRESS')
        self.data_ready_label.setStyleSheet('background:orange;color:white;')

    def refresh_graph(self):
        nuc_board = self.parent.get_nucleo_board()
        self.x_data, self.y_data, self.s_data = nuc_board.get_open_loop_data()
        print(f'SHAPE X_DATA = {self.x_data.shape}')
        t_data = numpy.linspace(0, len(self.x_data)-1, len(self.x_data))
        self.graph_widget.set_data(t_data, self.x_data)
        self.graph_widget.enable_chart()
        self.graph_widget.refresh_chart()

    def set_data_ready(self, value):
        self.data_ready = value
        if value:
            self.data_ready_label.setText('DATA OK')
            self.data_ready_label.setStyleSheet(valid_style)
        else:
            self.data_ready_label.setText('NO DATA')
            self.data_ready_label.setStyleSheet(not_style)

    def get_fs_ns(self):
        nb_samples = int(self.samples_combo.currentText())
        sampling_f = int(self.sampling_combo.currentText())
        return sampling_f, nb_samples

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
        self.intro = OpenLoopWidget()

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
