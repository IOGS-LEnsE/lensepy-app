# -*- coding: utf-8 -*-
"""Laser Position Control Interface - Menu

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/15


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python MainMenu.py
"""

# Libraries to import
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

# Global Constants
ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
active_style = "background:orange; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"
title_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

class MainMenu(QWidget):

    menu_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.mode = 'O'

        self.menu_layout = QVBoxLayout()
        self.menu_layout.addStretch()
        
        self.menu_introduction_button = QPushButton('Introduction')
        self.menu_layout.addWidget(self.menu_introduction_button)
        self.menu_introduction_button.setEnabled(False)
        self.menu_introduction_button.setStyleSheet(active_style)
        self.menu_layout.addStretch()
        
        self.menu_photodiode_button = QPushButton('Photodiode')
        self.menu_photodiode_button.setEnabled(False)
        self.menu_photodiode_button.clicked.connect(self.photodiode_action)
        self.menu_layout.addWidget(self.menu_photodiode_button)

        self.menu_scanner_button = QPushButton('Scanner')
        self.menu_layout.addWidget(self.menu_scanner_button)
        self.menu_scanner_button.setEnabled(False)
        self.menu_scanner_button.clicked.connect(self.scanner_action)
        self.menu_scanner_button.setStyleSheet(not_style)
        self.menu_layout.addStretch()

        self.menu_central_position_button = QPushButton('Central Position')
        self.menu_layout.addWidget(self.menu_central_position_button)
        self.menu_central_position_button.setEnabled(False)
        self.menu_central_position_button.clicked.connect(self.central_position_action)
        self.menu_central_position_button.setStyleSheet(not_style)

        self.menu_open_loop_button = QPushButton('Open Loop')
        self.menu_layout.addWidget(self.menu_open_loop_button)
        self.menu_open_loop_button.setEnabled(False)
        self.menu_open_loop_button.clicked.connect(self.open_loop_action)
        self.menu_open_loop_button.setStyleSheet(not_style)    
        self.menu_layout.addStretch()        

        self.menu_PID_button = QPushButton('PID Control')
        self.menu_layout.addWidget(self.menu_PID_button)
        self.menu_PID_button.setEnabled(False)
        self.menu_PID_button.clicked.connect(self.control_action)
        self.menu_PID_button.setStyleSheet(not_style)
        self.menu_layout.addStretch()
        
        self.setLayout(self.menu_layout)
       
    def photodiode_action(self):
        if self.mode != 'O':
            self.mode = 'P'
            self.menu_signal.emit('P')
            self.update_menu('P')

    def scanner_action(self):
        if self.mode != '0':
            self.mode = 'S'
            self.menu_signal.emit('S')
            self.update_menu('S')

    def central_position_action(self):
        if self.mode != '0':
            self.mode = 'E'
            self.menu_signal.emit('E')
            self.update_menu('E')

    def open_loop_action(self):
        if self.mode != '0':
            self.mode = 'L'
            self.menu_signal.emit('L')
            self.update_menu('L')

    def control_action(self):
        if self.mode != '0':
            self.mode = 'R'
            self.menu_signal.emit('R')
            self.update_menu('R')

    def update_menu(self, e):
        if e == 'C': # connected
            self.mode = 'C'
            self.menu_photodiode_button.setEnabled(True)
            self.menu_photodiode_button.setStyleSheet('')
        elif e == 'P': # Photodiode
            self.menu_introduction_button.setEnabled(False)
            self.menu_introduction_button.setStyleSheet(valid_style)
            self.menu_photodiode_button.setEnabled(False)
            self.menu_photodiode_button.setStyleSheet(active_style)
            self.menu_scanner_button.setEnabled(True)
            self.menu_scanner_button.setStyleSheet('')
            self.menu_central_position_button.setEnabled(False)
            self.menu_central_position_button.setStyleSheet(not_style)
        elif e == 'S': # Scanner
            self.menu_photodiode_button.setEnabled(True)
            self.menu_photodiode_button.setStyleSheet(valid_style)
            self.menu_scanner_button.setEnabled(False)
            self.menu_scanner_button.setStyleSheet(active_style)
            self.menu_central_position_button.setEnabled(True)
            self.menu_central_position_button.setStyleSheet('')
            self.menu_open_loop_button.setEnabled(False)
            self.menu_open_loop_button.setStyleSheet(not_style)

        elif e == 'E': # Central position
            self.menu_scanner_button.setEnabled(True)
            self.menu_scanner_button.setStyleSheet(valid_style)
            self.menu_central_position_button.setEnabled(False)
            self.menu_central_position_button.setStyleSheet(active_style)
            self.menu_scanner_button.setEnabled(False)
            self.menu_open_loop_button.setEnabled(False)
            self.menu_open_loop_button.setStyleSheet(not_style)
            self.menu_PID_button.setEnabled(False)
            self.menu_PID_button.setStyleSheet(not_style)
        elif e == 'D': # Central Position Validated
            self.menu_open_loop_button.setEnabled(True)
            self.menu_open_loop_button.setStyleSheet('')
        elif e == 'L':  # Open Loop Step Response
            self.menu_PID_button.setEnabled(True)
            self.menu_PID_button.setStyleSheet('')
            self.menu_open_loop_button.setEnabled(False)
            self.menu_open_loop_button.setStyleSheet(active_style)
            self.menu_central_position_button.setEnabled(True)
            self.menu_central_position_button.setStyleSheet(valid_style)
            self.menu_scanner_button.setEnabled(False)
        elif e == 'M': # Step in progress
            self.menu_scanner_button.setEnabled(False)
        elif e == 'R':
            self.menu_central_position_button.setEnabled(False)
            self.menu_PID_button.setStyleSheet(active_style)
            self.menu_open_loop_button.setEnabled(True)
            self.menu_open_loop_button.setStyleSheet(valid_style)


    def disconnected_board(self):
        self.menu_introduction_button.setStyleSheet(not_style)
        self.menu_introduction_button.setEnabled(True)

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
        self.menu = MainMenu()
        
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.menu)
        self.setCentralWidget(self.widget)


# -------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())