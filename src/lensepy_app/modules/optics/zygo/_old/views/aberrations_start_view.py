# -*- coding: utf-8 -*-
"""*aberrations_start_view.py* file.

./views/aberrations_start_view.py contains AberrationsStartView class to display options for analyses mode.

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
from PyQt6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QCheckBox,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.PVRMS_view import PVRMSView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.aberrations_controller import AberrationsController


class AberrationsStartView(QWidget):
    """Images Choice."""

    def __init__(self, controller: "AberrationsController"=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller: "AberrationsController" = controller
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_aberrations_start"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Progression Bar
        self.label_progress_bar = QLabel(translate('label_zernike_progress_bar'))
        self.label_progress_bar.setStyleSheet(styleH2)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_analyses_options)
        self.layout.addWidget(self.label_progress_bar)
        self.layout.addWidget(self.progress_bar)
        self.layout.addStretch()

    def update_progress_bar(self, value: int):
        """
        Update the progression bar value.
        :param value: Value to display.
        """
        self.progress_bar.setValue(value)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    '''
    from controllers.analyses_controller import AnalysesController, ModesManager
    manager = ModesManager()
    controller = AnalysesController()
    '''

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    main_widget = AberrationsStartView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.update_progress_bar(78)

    sys.exit(app.exec())