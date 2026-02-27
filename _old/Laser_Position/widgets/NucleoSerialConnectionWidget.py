# -*- coding: utf-8 -*-
"""
NucleoSerialConnectionWidget for displaying serial port list (STM Board)

----------------------------------------------------------------------------
Co-Author : Julien VILLEMEJANE
Laboratoire d Enseignement Experimental - Institut d Optique Graduate School
Version : 1.0 - 2023-08-31
"""

# Standard
import sys

# Graphical interface
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QComboBox, QSlider, QLineEdit,
    QVBoxLayout
    )
from PyQt6.QtCore import QTimer, Qt, pyqtSignal

ACTIVE_COLOR = "#45B39D"
INACTIVE_COLOR = "#AF7AC5"

valid_style = "background:" + ACTIVE_COLOR + "; color:white; font-weight:bold;"
not_style = "background:" + INACTIVE_COLOR + "; color:white; font-weight:bold;"
no_style = "background:gray; color:white; font-weight:none;"

#-----------------------------------------------------------------------------------------------

class NucleoSerialConnectionWidget(QWidget):
    """
    Widget used to display a list of available serial port and to connect to a Nucleo Board.
    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    connected = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialisation of our camera widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.serial_link = self.parent.get_nucleo_board() # LaserPID type
        self.layout = QVBoxLayout()

        # Title of the widget
        self.title_label = QLabel("Nucleo Board Connection")
        self.title_label.setStyleSheet("font-size: 16px; text-align: center; color:blue;")
        self.layout.addWidget(self.title_label)

        # Create List of available ports
        self.port_list = self.serial_link.get_serial_ports_list()
        self.port_combo = QComboBox(self)
        font = self.port_combo.font()
        font.setPointSize(18)
        self.port_combo.setFont(font)
        self.ports = [p.device for p in self.port_list]
        if len(self.ports) == 0:
            self.port_combo.addItem('No Board :( ')
        else:
            self.port_combo.addItem('Select...')
            self.port_combo.addItems(self.ports)
        self.layout.addWidget(self.port_combo)
        self.port_combo.currentTextChanged.connect(self.is_connection)

        # Connect button
        self.connect_button = QPushButton('Connect')
        font = self.connect_button.font()
        font.setPointSize(20)
        self.connect_button.setFont(font)
        if len(self.ports) == 0:
            self.connect_button.setEnabled(False)
        else:
            if self.port_combo.currentText() == 'Select...':
                self.connect_button.setEnabled(False)
            else:
                self.connect_button.setEnabled(True)
        self.connect_button.clicked.connect(self.connect_to_serial)
        self.layout.addWidget(self.connect_button)
        self.connect_button.setStyleSheet(no_style)

        # Refresh button
        self.refresh_button = QPushButton('Refresh List')
        font = self.refresh_button.font()
        font.setPointSize(14)
        self.refresh_button.setFont(font)
        self.refresh_button.clicked.connect(self.refresh_list)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)

    def refresh_list(self):
        """
        Refresh the available serial port.

        """
        self.port_list = self.serial_link.get_serial_ports_list()
        self.port_combo.clear()
        self.ports = [p.device for p in self.port_list]
        if len(self.ports) == 0:
            self.port_combo.addItem('No Board :( ')
        else:
            self.port_combo.addItem('Select...')
            self.port_combo.addItems(self.ports)

    def is_connection(self):
        if len(self.ports) == 0:
            self.connect_button.setEnabled(False)
            self.connect_button.setStyleSheet(no_style)
        else:
            if self.port_combo.currentText() == 'Select...':
                self.connect_button.setEnabled(False)
                self.connect_button.setStyleSheet(no_style)
            else:
                self.connect_button.setEnabled(True)
                self.connect_button.setStyleSheet(not_style)

    def connect_to_serial(self):
        """
        Connection to the serial port.

        """
        self.serial_link.set_serial_port(self.port_combo.currentText())
        if self.serial_link.connect_to_hardware():
            if self.serial_link.check_connection():
                self.connect_button.setStyleSheet(valid_style)
                self.connect_button.setEnabled(False)
                self.connect_button.setText('CONNECTED')
                self.refresh_button.setEnabled(False)
                self.port_combo.setEnabled(False)
                self.connected.emit('C')

    def disconnect(self):
        """
        Disconnect the serial port.

        """
        self.serial_link.disconnect()

    def send_data(self, data):
        """
        Send data through the serial port.

        Args:
            data: str
                string to send.
        """
        self.serial_link.send_data(data)


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
        self.nucleo_connect = NucleoSerialConnectionWidget()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.nucleo_connect)
        self.setCentralWidget(self.widget)


# -------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())