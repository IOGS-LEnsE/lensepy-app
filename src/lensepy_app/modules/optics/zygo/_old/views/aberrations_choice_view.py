# -*- coding: utf-8 -*-
"""*aberrations_choice_view.py* file.

./views/aberrations_choice_view.py contains AnalysesChoiceView class to display options
for choosing Zernike coefficients to correct in aberrations mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.PVRMS_view import PVRMSView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.aberrations_controller import AberrationsController

# Aberrations Choice / Name; Row; Col; List_of_orders; Global (Y-N); type;
str_choice = ['ab_astig_title;0;0;3,5,7;N;astig;',
              'ab_coma_title;2;0;3,5,7;N;coma;',
              'ab_sphere_title;4;0;3,5,7;N;sphere;',
              'ab_trefoil_title;6;0;,5,7;N;trefoil;']


class AberrationsChoiceView(QWidget):
    """Aberrations Choice for selecting aberrations to compensate."""

    aberrations_choice_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        # Data
        self.check_boxes = []
        self.signal_list = []
        self.aberrations_list = []
        # Graphical objects
        self.max_cols = 3
        self.max_rows = 9
        self.layout = QGridLayout()
        for k in range(self.max_cols):
            self.layout.setColumnStretch(k, 1)
        for k in range(self.max_rows):
            self.layout.setRowStretch(k, 1)
        self.setLayout(self.layout)
        self.load_choice()

    def load_choice(self):
        """
        Load choice from a list.
        Each line of the file contains :
        Name; Row; Col; List_of_orders; Global; type;
        """
        for line in str_choice:
            ab_name, ab_row, ab_col, ab_orders, ab_global, ab_type, _ = line.split(';')
            if ab_global == 'Y':
                check = QCheckBox(translate(ab_name))
                check.stateChanged.connect(self.action_checked)
                self.check_boxes.append(check)
                self.signal_list.append(str(ab_type))
                self.layout.addWidget(check, int(ab_row), int(ab_col), 3, 1)
            else:
                label = QLabel(translate(ab_name))
                self.layout.addWidget(label, int(ab_row), int(ab_col), 1, 3)
                orders = ab_orders.split(',')
                col_counter = 0
                for order in orders:
                    if order != '':
                        check_signal = ab_type + order
                        check = QCheckBox(order)
                        check.stateChanged.connect(self.action_checked)
                        self.check_boxes.append(check)
                        self.signal_list.append(check_signal)
                        self.layout.addWidget(check, int(ab_row)+1, col_counter)
                    col_counter += 1
        self.layout.addWidget(QLabel(""), int(ab_row)+2, 0, 1, 3)

    def action_checked(self):
        self.aberrations_list = []
        for i, check in enumerate(self.check_boxes):
            if check.isChecked():
                self.aberrations_list.append(self.signal_list[i])
        self.aberrations_choice_changed.emit('choice_changed')


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
    main_widget = AberrationsChoiceView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test

    sys.exit(app.exec())