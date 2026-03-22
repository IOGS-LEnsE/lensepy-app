# -*- coding: utf-8 -*-
"""*aberrations_options_view.py* file.

./views/aberrations_options_view.py contains AnalysesOptionsView class to display options
for aberrations mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6.widget_editline import LineEditView
from lensepy.pyqt6.widget_checkbox import CheckBoxView
from PyQt6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.PVRMS_view import PVRMSView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.aberrations_controller import AberrationsController


class AberrationsOptionsView(QWidget):
    """Images Choice."""

    aberrations_changed = pyqtSignal(str)

    def __init__(self, controller: "AberrationsController"=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller: "AberrationsController" = controller
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_aberrations_options"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_analyses_options)

        # Wedge factor
        self.wedge_edit = LineEditView('wedge', translate('label_wedge_value'), '1')
        self.wedge_edit.text_changed.connect(self.wedge_changed)
        self.layout.addWidget(self.wedge_edit)
        self.layout.addStretch()

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_ab_corrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH2)
        self.pv_rms_uncorrected = PVRMSView(vertical=True)
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addStretch()

        # Display corrected coefficients
        self.widget_correct = CheckBoxView('correct_disp', translate('label_correct_disp_choice'))
        self.widget_correct.set_enabled(True)
        self.widget_correct.check_changed.connect(self.disp_changed)
        self.layout.addWidget(self.widget_correct)
        self.widget_correct_first = CheckBoxView('correct_first',
                                                 translate('label_correct_first_choice'))
        self.widget_correct_first.set_enabled(True)
        self.widget_correct_first.check_changed.connect(self.disp_changed)
        self.layout.addWidget(self.widget_correct_first)
        self.layout.addStretch()
        # Defocus correction
        self.widget_correct_defoc = CheckBoxView('defocus_correct',
                                                 translate('label_correct_defocus_choice'))
        self.widget_correct_defoc.set_enabled(True)
        self.widget_correct_defoc.check_changed.connect(self.disp_changed)
        self.layout.addWidget(self.widget_correct_defoc)
        self.layout.addStretch()

        # lambda or nm display
        self.widget_lambda = QWidget()
        self.widget_layout = QHBoxLayout()
        self.widget_lambda.setLayout(self.widget_layout)
        self.lambda_edit = LineEditView('wavelength',
                                        translate('label_lambda_value'), '632.8')
        self.lambda_edit.text_changed.connect(self.lambda_changed)
        self.widget_layout.addWidget(self.lambda_edit)

        self.lambda_check = CheckBoxView('wavelength_check', translate('label_lambda_check'))
        self.lambda_check.check_changed.connect(self.lambda_changed)
        self.lambda_check.set_enabled(True)
        self.widget_layout.addWidget(self.lambda_check)

        self.layout.addWidget(self.widget_lambda)
        self.widget_layout.addStretch()

    def set_pv_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_uncorrected.set_pv(value, unit)

    def set_rms_uncorrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_uncorrected.set_rms(value, unit)

    def set_wedge(self, value: float):
        """
        Set the value of the wedge factor.
        :param value: Value of the wedge factor.
        """
        self.wedge_edit.text_edit.setText(str(value))

    def _clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.pv_rms_uncorrected.erase_pv_rms()
        self.pv_rms_corrected.erase_pv_rms()

    def wedge_changed(self, event):
        """
        Action to perform when the wedge factor changed.
        """
        self.aberrations_changed.emit(event)

    def disp_changed(self, event):
        """
        Action to perform when the checkbox for corrected coefficients displaying changed.
        """
        self.aberrations_changed.emit(event)

    def lambda_changed(self, event):
        """
        Action to perform when the value of lambda changed.
        """
        self.aberrations_changed.emit(event)

    def get_checkboxes(self):
        """
        Return the values of the checkbox in Zernike mode
        :return:
        """
        disp_correct = self.widget_correct.checkbox_choice.isChecked()
        disp_first = self.widget_correct_first.checkbox_choice.isChecked()
        return disp_correct, disp_first

    def set_checkboxes(self, correct: bool = False, first: bool = False, um_check: bool = False):
        """
        Set the values of the checkbox in Zernike mode
        """
        self.widget_correct.checkbox_choice.setChecked(correct)
        self.widget_correct_first.checkbox_choice.setChecked(first)
        self.lambda_check.checkbox_choice.setChecked(um_check)

    def is_lambda_checked(self) -> bool:
        """
        Return if the lambda or meters option is checked.
        :return: True if in um unit.
        """
        return self.lambda_check.checkbox_choice.isChecked()

    def get_lambda(self) -> float:
        """
        Return the value of the wavelength.
        :return: value of the wavelength.
        """
        return self.lambda_edit.text_edit.text()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    main_widget = AberrationsOptionsView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.set_pv_uncorrected(20.5, 'mm')

    sys.exit(app.exec())