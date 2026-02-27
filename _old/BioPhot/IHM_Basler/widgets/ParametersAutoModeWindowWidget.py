# Libraries to import
import sys
import os
from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QPushButton, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtGui import QIcon

from SupOpNumTools.pyqt6.IncDecWidget import IncDecWidget

# -------------------------------------------------------------------------------------------------------

# Colors
"""
Colors :    Green  : #c5e0b4
            Blue   : #4472c4
            Orange : #c55a11
            Beige  : #fff2cc
            Grey1  : #f2f2f2
            Grey2  : #bfbfbf
"""


# -------------------------------------------------------------------------------------------------------

class Parameters_AutoMode_Window(QWidget):
    """
    Widget used to parameter our AutoMode.

    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    def __init__(self, default_path=None):
        """
        Initialisation of the Widget.
        """
        super().__init__()

        if default_path is None:
            self.path = os.path.expanduser('~')
        else:
            self.path = default_path
        self.setWindowTitle("Automatic Mode Parameters Window")
        self.setWindowIcon(QIcon("IOGSLogo.jpg"))

        # Creating and adding widgets into our layout
        layout = QGridLayout()

        self.directoryLabel = QLabel("Directory")
        self.directoryLabel.setStyleSheet("border-style: none;")

        self.directoryPushButton = QPushButton("Directory")
        self.directoryPushButton.setStyleSheet("background: #c5e0b4; color: black;")

        self.z_init = IncDecWidget('Z Init (um)', values=['0.01', '0.1', '1'], limits=[0, 10])
        self.z_init.set_units('µm')
        self.z_final = IncDecWidget('Z Final (um)', values=['0.01', '0.1', '1'], limits=[0, 10])
        self.z_final.set_units('µm')
        self.z_step = IncDecWidget('Z Step (nm)', values=['1', '10', '100'], limits=[0, 1000])
        self.z_step.set_units('nm')

        self.saveParametersPushButton = QPushButton("Save Parameters")
        self.saveParametersPushButton.setStyleSheet("background: #c5e0b4; color: black;")

        layout.addWidget(self.directoryLabel, 0, 0, 1, 2)  # row = 0, column = 0, rowSpan = 1, columnSpan = 2
        layout.addWidget(self.directoryPushButton, 0, 2, 1, 2)  # row = 0, column = 2, rowSpan = 1, columnSpan = 2
        layout.addWidget(self.z_init, 1, 0, 1, 5)
        layout.addWidget(self.z_final, 2, 0, 1, 5)
        layout.addWidget(self.z_step, 3, 0, 1, 5)
        layout.addWidget(self.saveParametersPushButton, 4, 0, 1, 2)

        self.setLayout(layout)

    def setEnabled(self, enabled):
        """
        Method used to set the style sheet of the widget, if he is enable or disable.

        Args:
            enabled (bool): enable or disable.
        """
        super().setEnabled(enabled)
        if enabled:
            self.setStyleSheet("background-color: #4472c4; border-radius: 10px; border-width: 1px;"
                               "border-color: black; padding: 6px; font: bold 12px; color: white;"
                               "text-align: center; border-style: solid;")
            self.directoryPushButton.setStyleSheet(
                "background: #7fadff; border-style: solid; border-width: 1px; font: bold; color: black")
            self.saveParametersPushButton.setStyleSheet(
                "background: #7fadff; border-style: solid; border-width: 1px; font: bold; color: black")

        else:
            self.setStyleSheet("background-color: #bfbfbf; border-radius: 10px; border-width: 1px;"
                               "border-color: black; padding: 6px; font: bold 12px; color: white;"
                               "text-align: center; border-style: solid;")
            self.directoryPushButton.setStyleSheet(
                "background: white; border-style: solid; border-width: 1px; font: bold; color: black")
            self.saveParametersPushButton.setStyleSheet(
                "background: white; border-style: solid; border-width: 1px; font: bold; color: black")


# -------------------------------------------------------------------------------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Parameters_AutoMode_Window()
    window.show()

    sys.exit(app.exec())
