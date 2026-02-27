# -*- coding: utf-8 -*-
"""Laser Position Control Interface

This GUI drives a 2 dimensionnal scanner and collects
data from a 4 quadrants photodiode to control the position of 
a Laser beam

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
python MainWindow.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from matplotlib import pyplot as plt

from widgets.MainMenu import MainMenu
from widgets.IntroductionWidget import IntroductionWidget
from widgets.PhotodiodeWidget import PhotodiodeWidget
from widgets.EmptyWidget import EmptyWidget
from widgets.ScannerWidget import ScannerWidget
from widgets.CentralPositionWidget import CentralPositionWidget
from widgets.OpenLoopWidget import OpenLoopWidget
from widgets.PIDWidget import PIDWidget
from drivers.LaserPID import LaserPID


# -------------------------------

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
        self.setWindowIcon(QIcon('IOGS-LEnsE-logo.jpg'))
        # Variables
        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.timer_action)
        self.nucleo_board = LaserPID()
        self.camera = None  # TO ADD for embedded USB camera - with opencv
        self.mode = 'O'
        self.step_position = False
        self.step_position_x_min = 0
        self.step_position_x_max = 0
        self.step_position_y_min = 0
        self.step_position_y_max = 0
        # Step response
        self.step_x = None
        self.step_y = None
        self.step_fs = 0
        # Define Window title
        self.setWindowTitle("Laser Position Control")
        self.setWindowIcon(QIcon('_inc/IOGS-LEnsE-logo.jpg'))
        self.setGeometry(50, 50, 1000, 700)

        # Main Layout
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 4)
        self.main_widget.setLayout(self.main_layout)

        # Left Main Menu
        self.main_menu = MainMenu()
        self.main_menu.menu_signal.connect(self.update_mode)
        self.main_layout.addWidget(self.main_menu, 0, 0)

        # Graphical objects
        self.intro_widget = IntroductionWidget(self)
        self.intro_widget.intro_signal.connect(self.update_mode)
        self.main_layout.addWidget(self.intro_widget, 0, 1)
        self.central_widget = EmptyWidget()

        self.setCentralWidget(self.main_widget)
        self.main_timer.setInterval(200)

    def get_nucleo_board(self):
        return self.nucleo_board

    def get_photodiode_value(self):
        """
        Send photodiode position command 'A_!' to the control board.

        After the command is received by the controller, an acknowledgement is sent :
            'A_posX_posY_!'   where posX and posY are the position of the beam on the photodiode

        Returns:
            x, y :float
                x and y position of the photodiode
        """
        return self.nucleo_board.get_phd_xy()

    def set_scanner_position(self, x, y):
        """
        Send moving command 'M_x_y_!' to the control board.

        After the command is received by the controller, an acknowledgement is sent :
            'M_x_y_posX_posY_!'   where posX and posY are the position of the beam on the photodiode

        Args:
            x: float
                position on X-axis to move the scanner
            y: float
                position on Y-axis to move the scanner

        Returns:
            x, y :float
                x and y position of the photodiode
        """
        return self.nucleo_board.set_scan_xy(x, y)

    def timer_action(self):
        if self.mode == 'P':  # Photodiode manual response
            x_phd_value, y_phd_value = self.get_photodiode_value()
            if x_phd_value is not None:
                self.central_widget.set_position(x_phd_value, y_phd_value)
            self.central_widget.refresh_target()
        elif self.mode == 'S' or self.mode == 'E':  
            # Scanner manual control / central position
            scanner_x, scanner_y = self.central_widget.get_scanner_position()
            x_phd_value, y_phd_value = self.set_scanner_position(scanner_x, scanner_y)
            if x_phd_value is not None:
                self.central_widget.set_position(x_phd_value, y_phd_value)
            self.central_widget.refresh_target()
            
        elif self.mode == 'L':
            if self.nucleo_board.is_step_over():
                self.main_timer.stop()
                self.central_widget.set_data_ready(True)
                self.step_x, self.step_y, self.step_fs = self.central_widget.refresh_graph()

        elif self.mode == 'R':
            # Check new values and transfer to PID hardware
            k_x, k_y, i_x, i_y, d_x, d_Y, sampling = self.central_widget.get_PID_parameters()
            self.nucleo_board.set_PID_params(k_x, k_y, i_x, i_y, d_x, d_Y, sampling)

    def update_layout(self, new_widget):
        count = self.main_layout.count()
        if count > 1:
            item = self.main_layout.itemAt(count - 1)
            old_widget = item.widget()
            old_widget.deleteLater()
            self.main_layout.addWidget(new_widget, 0, 1)

    def checked_action(self):
        self.main_menu.update_menu('D')
        self.main_timer.stop()
        if self.nucleo_board.is_data_waiting():
            self.nucleo_board.clear_buffer()
        x1, x2, y1, y2 = self.central_widget.get_limits()
        self.step_position_x_min = x1
        self.step_position_x_max = x2
        self.step_position_y_min = y1
        self.step_position_y_max = y2
        self.step_position = True

    def open_loop_action(self, e):
        if e == 'L_Start': # Start of step response acquisition
            fs, ns = self.central_widget.get_fs_ns()
            self.nucleo_board.clear_buffer()
            if self.nucleo_board.start_open_loop_step(fs, ns):
                self.main_menu.update_menu('M')
                self.main_timer.setInterval(300)
                self.main_timer.start()

    def update_mode(self, e):
        if self.nucleo_board is not None and e != 'C':
            self.nucleo_board.send_stop()
        if e == 'C':
            self.mode = 'C'
            self.main_timer.stop()
            self.main_menu.update_menu('C')
        elif e == 'P':  # photodiode
            self.mode = 'P'
            self.central_widget = PhotodiodeWidget(self.camera)
            self.update_layout(self.central_widget)
            self.main_timer.setInterval(100)
            self.main_timer.start()
        elif e == 'S':  # scanner
            self.mode = 'S'
            self.central_widget = ScannerWidget()
            self.update_layout(self.central_widget)
            self.main_timer.setInterval(100)
            self.main_timer.start()
        elif e == 'E': # central position
            self.mode = 'E'
            self.main_timer.stop()
            self.central_widget = CentralPositionWidget(parent=self, camera=self.camera)
            self.central_widget.checked_limits.connect(self.checked_action)
            self.update_layout(self.central_widget)
            if self.step_position:
                self.central_widget.set_limits(self.step_position_x_min, self.step_position_x_max,
                                               self.step_position_y_min, self.step_position_y_max)
            self.main_timer.setInterval(100)
            self.main_timer.start()
        elif e == 'L': # Step response
            self.mode = 'L'
            self.main_timer.stop()
            self.central_widget = OpenLoopWidget(self)
            self.central_widget.step_response.connect(self.open_loop_action)
            self.update_layout(self.central_widget)
            self.main_timer.setInterval(200)
            if self.step_x is not None and self.step_y is not None:
                self.main_timer.stop()
                self.central_widget.set_data(self.step_x, self.step_y, self.step_fs)
        elif e == 'R': # PID control
            self.mode = 'R'
            self.main_timer.stop()
            self.central_widget = PIDWidget(self)
            self.update_layout(self.central_widget)
            self.main_timer.setInterval(200)
            self.main_timer.start()


# -------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
