# -*- coding: utf-8 -*-
"""*masks_view.py* file.

./views/masks_view.py contains MasksView class to create masks.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os, time
from lensepy import load_dictionary, translate, dictionary, is_float
from lensepy.css import *
from lensepy_app.widgets import make_hline
from lensepy_app.widgets.widget_editline import LineEditView
from lensepy.images.conversion import resize_image_ratio
from lensepy_app.utils import array_to_qimage
from PyQt6.QtWidgets import (
    QDialog, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QVBoxLayout,
    QApplication,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent, QFont

class InterferControlView(QWidget):
    """Images Choice."""

    analyses_changed = pyqtSignal(str)
    wedge_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller = parent
        self.tilt_on = False
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_analyses_options = QLabel(translate("label_analyses_options"))
        self.label_analyses_options.setStyleSheet(styleH1)
        self.label_analyses_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_analyses_options)

        # Wedge Factor
        self.wedge_edit = LineEditView('wedge', translate('label_wedge_value'), '1')
        self.wedge_edit.text_changed.connect(lambda text: self.wedge_changed.emit(text))

        # PV/RMS displayed (for uncorrected phase)
        self.label_pv_rms_uncorrected = QLabel(translate('label_pv_rms_uncorrected'))
        self.label_pv_rms_uncorrected.setStyleSheet(styleH2)
        self.pv_rms_uncorrected = PVRMSView()

        ## Only when corrected button in analyses is clicked.
        # PV/RMS displayed (for corrected phase)
        self.label_pv_rms_corrected = QLabel(translate('label_pv_rms_corrected'))
        self.label_pv_rms_corrected.setStyleSheet(styleH2)
        self.pv_rms_corrected = PVRMSView()

        # Add graphical elements to the layout.
        self.layout.addWidget(self.wedge_edit)
        self.layout.addWidget(self.label_pv_rms_uncorrected)
        self.layout.addWidget(self.pv_rms_uncorrected)
        self.layout.addWidget(self.label_pv_rms_corrected)
        self.layout.addWidget(self.pv_rms_corrected)
        self.layout.addStretch()

    def set_wegde(self, value):
        """Set the value of the wedge factor."""
        self.wedge_edit.set_value(value)

    def get_wedge(self):
        """Get the value of the wedge factor."""
        result = self.wedge_edit.get_value()
        if is_float(result):
            return float(result)
        return None

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

    def __init__(self, size=''):
        """
        Default constructor.
        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        if size == '':
            style_L = styleL
            style_T = styleT
            MINIMUM_WIDTH = 75
        else:
            style_L = styleL_s
            style_T = styleT_s
            MINIMUM_WIDTH = 40

        self.label_PV = QLabel(translate('label_PV'))
        self.label_PV.setStyleSheet(style_L)
        self.text_PV = QLabel()
        self.text_PV.setStyleSheet(style_T)
        self.text_PV.setMinimumWidth(MINIMUM_WIDTH)
        self.text_PV.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_PV = QLabel()
        self.unit_PV.setMinimumWidth(MINIMUM_WIDTH//2)
        self.label_RMS = QLabel(translate('label_RMS'))
        self.label_RMS.setStyleSheet(style_L)
        self.text_RMS = QLabel()
        self.text_RMS.setStyleSheet(style_T)
        self.text_RMS.setMinimumWidth(MINIMUM_WIDTH)
        self.text_RMS.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_RMS = QLabel()
        self.unit_RMS.setMinimumWidth(MINIMUM_WIDTH//2)
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


class SurfaceChoiceView(QWidget):

    surface_selected = pyqtSignal(str)
    tilt_changed = pyqtSignal(bool)
    view_saved = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        # Graphical objects
        layout = QVBoxLayout()
        self.setLayout(layout)

        ## Title of the widget
        layout.addWidget(make_hline())
        self.label_interfer_options = QLabel(translate("surface_choice_interfer"))
        self.label_interfer_options.setStyleSheet(styleH1)
        self.label_interfer_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_interfer_options)
        layout.addWidget(make_hline())

        self.unwrap_2D_button = QPushButton(translate('2D_unwrap_button'))
        self.unwrap_2D_button.setStyleSheet(unactived_button)
        self.unwrap_2D_button.setFixedHeight(BUTTON_HEIGHT)
        self.unwrap_2D_button.clicked.connect(self.handle_selected)
        layout.addWidget(self.unwrap_2D_button)

        self.unwrap_3D_button = QPushButton(translate('3D_unwrap_button'))
        self.unwrap_3D_button.setStyleSheet(unactived_button)
        self.unwrap_3D_button.setFixedHeight(BUTTON_HEIGHT)
        self.unwrap_3D_button.clicked.connect(self.handle_selected)
        layout.addWidget(self.unwrap_3D_button)
        layout.addStretch()
        self.tilt_check = QCheckBox(translate('tilt_check_box'))
        self.tilt_check.setStyleSheet(styleH3)
        layout.addWidget(self.tilt_check)
        layout.addStretch()

        layout.addWidget(make_hline())
        self.wrap_2D_button = QPushButton(translate('2D_wrap_button'))
        self.wrap_2D_button.setStyleSheet(unactived_button)
        self.wrap_2D_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.wrap_2D_button.clicked.connect(self.handle_selected)
        layout.addWidget(self.wrap_2D_button)

        self.wrap_3D_button = QPushButton(translate('3D_wrap_button'))
        self.wrap_3D_button.setStyleSheet(unactived_button)
        self.wrap_3D_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.wrap_3D_button.clicked.connect(self.handle_selected)
        layout.addWidget(self.wrap_3D_button)
        layout.addWidget(make_hline())
        layout.addStretch()

        self.save_button = QPushButton(translate('save_current_view'))
        self.save_button.setStyleSheet(unactived_button)
        self.save_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_button.clicked.connect(self.handle_saved)
        layout.addWidget(self.save_button)
        layout.addWidget(make_hline())

        layout.addStretch()

        # Signals
        self.tilt_check.clicked.connect(self.handle_tilt_clicked)

    def handle_saved(self):
        file_dialog = QFileDialog()
        # default dir ?
        default_dir = self.parent.get_config('img_dir') or None
        # dialog box
        file_path, _ = file_dialog.getSaveFileName(self, translate('dialog_view_png_image'),
                                                   default_dir, "Images (*.png)")
        if file_path != '':
            self.view_saved.emit(file_path)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Saved")
            dlg.setText("No Image File was saved...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return


    def handle_tilt_clicked(self):
        """Action performed when the tilt checkbox is clicked."""
        self.tilt_changed.emit(self.tilt_check.isChecked())

    def inactivate_buttons(self):
        """Inactivate all the buttons."""
        self.wrap_2D_button.setStyleSheet(unactived_button)
        self.unwrap_2D_button.setStyleSheet(unactived_button)
        self.wrap_3D_button.setStyleSheet(unactived_button)
        self.unwrap_3D_button.setStyleSheet(unactived_button)

    def handle_selected(self):
        """Action performed when 2D unwrapped surface is selected."""
        # Erase all button
        self.inactivate_buttons()
        # Send signal to display selected surface
        sender = self.sender()
        if sender == self.unwrap_2D_button:
            self.unwrap_2D_button.setStyleSheet(actived_button)
            self.surface_selected.emit('2D_unwrap')
        elif sender == self.wrap_2D_button:
            self.wrap_2D_button.setStyleSheet(actived_button)
            self.surface_selected.emit('2D_wrap')
        elif sender == self.unwrap_3D_button:
            self.unwrap_3D_button.setStyleSheet(actived_button)
            self.surface_selected.emit('3D_unwrap')
        elif sender == self.wrap_3D_button:
            self.wrap_3D_button.setStyleSheet(actived_button)
            self.surface_selected.emit('3D_wrap')

    def activate_button(self, value):
        value_split = value.split('_')
        self.inactivate_buttons()
        if value_split[0] == '2D':
            if value_split[1] == 'wrap':
                self.wrap_2D_button.setStyleSheet(actived_button)
            elif value_split[1] == 'unwrap':
                self.unwrap_2D_button.setStyleSheet(actived_button)
        elif value_split[0] == '3D':
            if value_split[1] == 'wrap':
                self.wrap_3D_button.setStyleSheet(actived_button)
            elif value_split[1] == 'unwrap':
                self.unwrap_3D_button.setStyleSheet(actived_button)