# -*- coding: utf-8 -*-
"""*laser_control.py* file.

This GUI drives a 2 dimensionnal scanner and collects
data from a 4 quadrants photodiode to control the position of
a Laser beam

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : oct/2024
"""
from lensepy import load_dictionary, translate, dictionary
import sys
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)
from widgets.main_widget import MainWidget, load_menu
from drivers.LaserPID import *


def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)

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
        load_default_dictionary('FR')
        ## GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        # Menu
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        self.central_widget.main_signal.connect(self.main_action)
        ## Main MODE
        self.mode = 'O'

        # Camera (future update)
        # ----------------------
        self.camera = None

        # PID controller (L476RG)
        # -----------------------
        self.nucleo_board = LaserPID()

        # Parameter of the system
        # -----------------------
        self.step_position = False
        self.step_position_x_min = 0
        self.step_position_x_max = 0
        self.step_position_y_min = 0
        self.step_position_y_max = 0

        # Data of the system
        # ------------------


    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        print(f'Main {event}')

    def thread_photodiode_update(self):
        pass

    def resizeEvent(self, event):
        """
        Action performed when the main window is resized.
        :param event: Object that triggered the event.
        """
        self.central_widget.update_size()

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())