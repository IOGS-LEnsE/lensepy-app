# -*- coding: utf-8 -*-
"""*analyses_options_view.py* file.

./views/analyses_options_view.py contains AnalysesOptionsView class to display options for analyses mode.

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
from lensepy.pyqt6.widget_progress_bar import ProgressBarView
from lensepy.pyqt6.widget_checkbox import CheckBoxView
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.analyses_controller import AnalysesController

MINIMUM_WIDTH = 75


class AnalysesOptionsView(QWidget):
    """Images Choice."""

    analyses_changed = pyqtSignal(str)

    def __init__(self, controller: "AnalysesController"=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller: "AnalysesController" = controller
        self.tilt_on = False
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_analyses_options"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_analyses_options)

        # 2D/3D display
        self.widget_2D_3D = QPushButton(translate('label_2D_3D_choice'))
        self.widget_2D_3D.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.widget_2D_3D.setStyleSheet(unactived_button)
        self.widget_2D_3D.clicked.connect(self.display_changed)
        # 2D/3D display with gain
        self.widget_2D_3D_gain = QPushButton(translate('label_2D_3D_choice_gain'))
        self.widget_2D_3D_gain.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.widget_2D_3D_gain.setStyleSheet(unactived_button)
        self.widget_2D_3D_gain.clicked.connect(self.display_changed)
        # Wedge Factor
        self.wedge_edit = LineEditView('wedge', translate('label_wedge_value'), '1')
        self.wedge_edit.text_changed.connect(self.wedge_changed)

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH2)
        self.pv_rms_uncorrected = PVRMSView()

        ## Only when corrected button in analyses is clicked.
        # PV/RMS displayed (for corrected phase)
        self.label_pv_rms_corrected = QLabel(translate('label_pv_rms_corrected'))
        self.label_pv_rms_corrected.setStyleSheet(styleH2)
        ## Button for TILT
        self.widget_tilt = QPushButton(translate('label_tilt_choice'))
        self.widget_tilt.setStyleSheet(unactived_button)
        self.widget_tilt.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.widget_tilt.clicked.connect(self.tilt_changed)

        self.pv_rms_corrected = PVRMSView()

        # Add graphical elements to the layout.
        self.layout.addWidget(self.wedge_edit)
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addWidget(self.label_pv_rms_corrected)
        self.layout.addWidget(self.widget_tilt)
        self.layout.addWidget(self.pv_rms_corrected)
        self.layout.addStretch()
        self.layout.addWidget(self.widget_2D_3D)
        self.layout.addWidget(self.widget_2D_3D_gain)
        self.layout.addStretch()
        self.show_correction()

    def hide_correction(self):
        """
        Hide the corrected option part of the widget.
        """
        self.widget_tilt.hide()
        self.label_pv_rms_uncorrected.hide()
        self.pv_rms_uncorrected.hide()
        self.label_pv_rms_corrected.hide()
        self.pv_rms_corrected.hide()

    def show_correction(self):
        """
        Show the corrected option part of the widget.
        ## Only when corrected button in analyses is clicked.
        """
        self.widget_tilt.show()
        self.label_pv_rms_uncorrected.show()
        self.pv_rms_uncorrected.show()
        self.label_pv_rms_corrected.show()
        self.pv_rms_corrected.show()

    def set_enable_2D_3D(self, value: bool):
        """
        Set enable the 2D/3D display checkbox.
        :param value: True or False.
        """
        self.widget_2D_3D.setEnabled(value)

    def set_enable_tilt(self, value: bool):
        """
        Set enable the 2D/3D display checkbox.
        :param value: True or False.
        """
        self.widget_tilt.setEnabled(value)

    def is_tilt_checked(self):
        """
        Return if the tilt checkbox is checked.
        :return: True if checked.
        """
        return self.tilt_on

    def display_changed(self, event):
        """
        Action performed when the 2D/3D button is clicked.
        """
        sender = self.sender()
        if sender == self.widget_2D_3D:
            self.analyses_changed.emit('disp_3D,')
        elif sender == self.widget_2D_3D_gain:
            self.analyses_changed.emit('disp_3D_gain,')
        else:
            self.analyses_changed.emit(event)

    def tilt_changed(self):
        """
        Action performed when the 2D/3D checkbox is checked.
        """
        if self.tilt_on:
            self.tilt_on = False
            self.analyses_changed.emit('tilt,off')
            self.widget_tilt.setStyleSheet(unactived_button)
        else:
            self.tilt_on = True
            self.analyses_changed.emit('tilt,on')
            self.widget_tilt.setStyleSheet(actived_button)

    def range_changed(self, event):
        """
        Action performed when the Range checkbox is checked.
        """
        self.analyses_changed.emit(event)

    def wedge_changed(self, event):
        """
        Action performed when the wedge line edit changed.
        """
        self.analyses_changed.emit(event)

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

    def set_pv_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.pv_rms_corrected.set_pv(value, unit)

    def set_rms_corrected(self, value: float, unit: str = '\u03BB'):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.pv_rms_corrected.set_rms(value, unit)

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


class PVRMSView(QWidget):
    """
    Class to display PV (Peak-to-Valley) and RMS value of a wavefront.
    """

    def __init__(self):
        """
        Default constructor.
        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        styleL = f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
        styleT = f"font-size:14px; padding:5px; font-weight: bold; background-color: white;"
        self.label_PV = QLabel(translate('label_PV'))
        self.label_PV.setStyleSheet(styleL)
        self.text_PV = QLabel()
        self.text_PV.setStyleSheet(styleT)
        self.text_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.text_PV.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_PV = QLabel()
        self.unit_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.label_RMS = QLabel(translate('label_RMS'))
        self.label_RMS.setStyleSheet(styleL)
        self.text_RMS = QLabel()
        self.text_RMS.setStyleSheet(styleT)
        self.text_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.text_RMS.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_RMS = QLabel()
        self.unit_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.layout.addWidget(self.label_PV)
        self.layout.addWidget(self.text_PV)
        self.layout.addWidget(self.unit_PV)
        self.layout.addStretch()
        self.layout.addWidget(self.label_RMS)
        self.layout.addWidget(self.text_RMS)
        self.layout.addWidget(self.unit_RMS)
        self.layout.addStretch()

    def set_pv(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the PV value.
        :param value: value of the peak-to-valley.
        :param unit: Unit of the PV value.
        """
        self.text_PV.setText(str(value))
        self.unit_PV.setText(unit)

    def set_rms(self, value: float, unit: str = ''):
        """
        Update the value and the unit of the RMS value.
        :param value: value of the RMS.
        :param unit: Unit of the RMS value.
        """
        self.text_RMS.setText(str(value))
        self.unit_RMS.setText(unit)

    def erase_pv_rms(self):
        """
        Erase PV and RMS values.
        """
        self.text_PV.setText('')
        self.unit_PV.setText('')
        self.text_RMS.setText('')
        self.unit_RMS.setText('')


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
    main_widget = AnalysesOptionsView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.set_enable_2D_3D(True)
    main_widget.set_enable_tilt(True)
    main_widget.set_enable_range(True)
    main_widget.set_pv_uncorrected(20.5, 'mm')
    main_widget.analyses_changed.connect(analyses_changed)
    main_widget.show_correction()

    sys.exit(app.exec())