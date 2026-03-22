# -*- coding: utf-8 -*-
"""*simple_acquisition_view.py* file.

./views/simple_acquisition_view.py contains SimpleAcquisitionView class to display options
for simple acquisition.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from lensepy.pyqt6.widget_slider import SliderBloc
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QProgressBar,
    QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.acquisition_controller import AcquisitionController
    from models.dataset import DataSetModel


class SimpleAcquisitionView(QWidget):
    """Acquisition Options."""

    voltage_changed = pyqtSignal(str)
    acquisition_end = pyqtSignal(str)

    def __init__(self, controller: "AcquisitionController"=None) -> None:
        """Default constructor of the class.
        """
        super().__init__()
        self.controller: "AcquisitionController" = controller
        self.data_set: "DataSetModel" = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        self.label_simple_acq_title = QLabel(translate("label_simple_acq_title"))
        self.label_simple_acq_title.setStyleSheet(styleH1)
        self.label_simple_acq_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Start acquisition - delete mask
        self.start_acq_button = QPushButton(translate('start_acq_button'))
        self.start_acq_button.setStyleSheet(unactived_button)
        self.start_acq_button.setFixedHeight(BUTTON_HEIGHT)
        self.start_acq_button.clicked.connect(self.start_acquisition)
        # Start acquisition - keep mask
        self.start_acq_keep_button = QPushButton(translate('start_acq_keep_button'))
        self.start_acq_keep_button.setStyleSheet(unactived_button)
        self.start_acq_keep_button.setFixedHeight(BUTTON_HEIGHT)
        self.start_acq_keep_button.clicked.connect(self.start_acquisition)

        # Progression Bar
        self.label_progress_bar = QLabel(translate('label_progress_acq_bar'))
        self.label_progress_bar.setStyleSheet(styleH2)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_simple_acq_title)
        self.layout.addWidget(self.start_acq_button)
        self.layout.addWidget(self.start_acq_keep_button)
        self.layout.addStretch()
        self.layout.addWidget(self.label_progress_bar)
        self.layout.addWidget(self.progress_bar)
        self.layout.addStretch()

    def start_acquisition(self, event):
        """
        Start acquisition of one set of images.
        """
        sender = self.sender()
        volt_list = [0.80, 1.62, 2.43, 3.24, 4.05]
        self.data_set.acquisition_mode.set_voltages(volt_list)
        if sender == self.start_acq_keep_button:
            self.data_set.reset_data(keep_mask=True)
        else:
            self.data_set.reset_data()
        if self.data_set.acquisition_mode.is_possible():
            self.data_set.acquisition_mode.start()
            thread = threading.Thread(target=self.update_progress_bar)
            time.sleep(0.01)
            thread.start()

    def update_progress_bar(self):
        """
        Update the progress bar value.
        """
        progress_value = self.data_set.acquisition_mode.get_progress()
        if progress_value < 100:
            self.progress_bar.setValue(progress_value)
            thread = threading.Thread(target=self.update_progress_bar)
            time.sleep(0.01)
            thread.start()
        else:
            self.progress_bar.setValue(100)
            time.sleep(0.01)
            self.acquisition_end.emit('acq_end')

    def update_view(self):
        if self.data_set.has_mask():
            self.start_acq_keep_button.setEnabled(True)
            self.start_acq_keep_button.setStyleSheet(unactived_button)
        else:
            self.start_acq_keep_button.setEnabled(False)
            self.start_acq_keep_button.setStyleSheet(disabled_button)



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
            main_widget = SimpleAcquisitionView(self.controller)
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