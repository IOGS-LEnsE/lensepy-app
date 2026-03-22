# -*- coding: utf-8 -*-
"""*piezo_options_view.py* file.

./views/piezo_options_view.py contains PiezoOptionsView class to display options for piezo movement.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from lensepy.pyqt6.widget_slider import SliderBloc
from PyQt6.QtWidgets import (
    QWidget, QLabel,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.acquisition_controller import AcquisitionController
    from models.dataset import DataSetModel


class PiezoOptionsView(QWidget):
    """Acquisition Options."""

    voltage_changed = pyqtSignal(str)

    def __init__(self, controller: "AcquisitionController"=None) -> None:
        """Default constructor of the class.
        """
        super().__init__()
        self.controller: "AcquisitionController" = controller
        self.data_set: "DataSetModel" = self.controller.data_set
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Title
        self.label_piezo_title = QLabel(translate("label_piezo_move_title"))
        self.label_piezo_title.setStyleSheet(styleH1)
        self.label_piezo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider to move
        self.voltage_slider = SliderBloc(translate('piezo_voltage_slider'), 'V', 0, 5)
        self.voltage_slider.set_value(1)
        self.voltage_slider.set_enabled(self.data_set.acquisition_mode.is_piezo())
        if self.data_set.acquisition_mode.is_piezo():
            self.data_set.acquisition_mode.piezo.write_dac(1)
        self.voltage_slider.slider_changed.connect(self.action_voltage_changed)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_piezo_title, 0, 0)
        self.layout.addWidget(self.voltage_slider,1, 0)

    def get_voltage(self) -> float:
        """Return the voltage from the slider.
        :return: Voltage as float (in V).
        """
        return float(self.voltage_slider.get_value())

    def action_voltage_changed(self, event):
        """Action performed when the voltage slider changed."""
        self.voltage_changed.emit('voltage')


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from controllers.modes_manager import ModesManager
    from views.main_structure import MainView
    from models.dataset import DataSetModel
    from views.main_menu import MainMenu
    from controllers.acquisition_controller import AcquisitionController

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            widget = MainView()
            menu = MainMenu()
            menu.load_menu('')
            widget.set_main_menu(menu)
            data_set = DataSetModel()
            manager = ModesManager(menu, widget, data_set)

            # Test controller
            self.controller = AcquisitionController(manager)
            manager.mode_controller = self.controller
            main_widget = PiezoOptionsView(self.controller)
            main_widget.voltage_changed.connect(self.settings_changed)
            self.setCentralWidget(main_widget)

        def closeEvent(self, event):
            self.controller.stop_acquisition()

        def settings_changed(self, value):
            print(value)


    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())