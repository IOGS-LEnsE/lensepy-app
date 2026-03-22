# -*- coding: utf-8 -*-
"""*masks_options_view.py* file.

./views/masks_options_view.py contains MasksOptionsView class to display options for masks mode.

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
    QWidget, QLabel, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from utils.dataset_utils import DataSetState, DataSetStateValue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.masks_controller import MasksController

class MasksOptionsView(QWidget):
    """Images Choice."""

    masks_changed = pyqtSignal(str)

    def __init__(self, controller: "MasksController"=None) -> None:
        """Default constructor of the class.
        :param controller: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller: "MasksController" = controller
        #self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_masks_options = QLabel(translate("label_masks_options"))
        self.label_masks_options.setStyleSheet(styleH1)
        self.label_masks_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_masks_options)

        # Table List of masks
        self.masks_list = MasksTableList(self.controller)
        self.layout.addWidget(self.masks_list)

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


class MasksTableList(QTableWidget):

    masks_changed = pyqtSignal()

    def __init__(self, controller: "MasksController", rows=1, cols=5):
        super().__init__(rows, cols)  # Nombre de lignes et colonnes
        # Data of the class
        self.controller: "MasksController" = controller
        self.data_set = self.controller.data_set
        self.select_list = []
        self.invert_list = []
        self.delete_list = []
        # Main options of the table
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.verticalHeader().setVisible(False)     # No line number
        self.setShowGrid(False)
        # Column size
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 100)
        self.setColumnWidth(4, 100)
        # Set the header name of each column
        self.setHorizontalHeaderLabels([translate('masks_list_nb'), translate('masks_list_type'),
                                        translate('masks_list_select'), translate('masks_list_invert')
                                        ,translate('masks_list_delete')])
        # CSS Style for header
        self.setStyleSheet("""
            QHeaderView::section {
                background-color: #0A3250;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 3px;
                border: 2px solid white;
            }            
            QHeaderView::item {
                padding: 0px;
            }
        """)
        # Graphical elements
        self.insertRow(0)    # Insert the first line
        self.setRowHeight(0, 40)
        self._add_text(0, 0, "ALL")
        self._add_text(0, 1, "GLOBAL")
        self._add_select_checkbox(0)
        self._add_invert_checkbox(0)
        self._add_delete_button(0, translate('delete_all'))

        self.init_data()
        self.update_data()
        self.controller.update_submenu('first')

    def update_data(self):
        # Changer la couleur de fond des lignes paires
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    if row == 0:  # Modifier uniquement la 1ère ligne
                        item.setBackground(QColor(ORANGE_IOGS))  # Orange
                        item.setForeground(QColor(BLUE_IOGS))  # Texte noir
                    elif row % 2 == 0:  # Lignes paires en gris clair
                        item.setBackground(QColor(230, 230, 230))
                    else:  # Lignes impaires en blanc
                        item.setBackground(QColor(255, 255, 255))

    def update_display(self):
        """
        Update masks list display.
        """
        self.delete_data()
        self.init_data()
        self.update_data()
        '''
        if self.data_set.masks_sets.get_masks_number()+1 >= self.rowCount():
            self.add_new_row(self.data_set.masks_sets.get_masks_number())
            self.setRowHeight(self.data_set.masks_sets.get_masks_number(), 40)
        '''

    def init_data(self):
        """
        Initialize graphical lines of the table.
        """
        if self.data_set.masks_sets.get_masks_number() == 0:
            self.data_set.set_masks_state(False)
        for mask_index in range(self.data_set.masks_sets.get_masks_number()):
            self.add_new_row(mask_index+1)
            self.setRowHeight(mask_index+1, 40)

    def delete_data(self):
        """
        Remove graphical lines of the table.
        :return:
        """
        if len(self.select_list) > 1:
            for mask_index in range(len(self.delete_list)-1):
                self.removeRow(1)
                self.delete_list.pop()
                self.select_list.pop()
                self.invert_list.pop()

    def add_new_row(self, index: int):
        row_position = self.rowCount()  # Get the actual number of lines
        self.insertRow(row_position)    # Insert a new line
        # Add data
        self._add_text(index, 0, str(index), False)
        type = self.data_set.masks_sets.get_type(index)
        self._add_text(index, 1, type, False)
        self._add_select_checkbox(index, self.data_set.masks_sets.is_mask_selected(index))
        self._add_invert_checkbox(index, self.data_set.masks_sets.is_mask_inverted(index))
        self._add_delete_button(index, translate('delete_mask'))

    def select_mask(self, event):
        sender = self.sender()
        for i, select_check in enumerate(self.select_list):
            if sender == select_check:
                if i != 0:
                    # Select (or not a mask)
                    self.data_set.masks_sets.select_mask(i, sender.isChecked())
                    # If the sender is not checked, uncheck global mask
                    if sender.isChecked() is False:
                        self.select_list[0].setChecked(False)
                else:   # Select all the masks
                    if sender.isChecked():
                        for k in range(self.data_set.masks_sets.get_masks_number()):
                            self.data_set.masks_sets.select_mask(k, True)
                        self.delete_data()
                        self.init_data()
        self.masks_changed.emit()

    def invert_mask(self, event):
        sender = self.sender()
        for i, select_check in enumerate(self.invert_list):
            if sender == select_check:
                if i == 0:
                    self.data_set.masks_sets.invert_global_mask(sender.isChecked())
                else:
                    self.data_set.masks_sets.invert_mask(i-1, sender.isChecked())
        self.masks_changed.emit()

    def delete_mask(self, event):
        sender = self.sender()
        for i, delete_button in enumerate(self.delete_list):
            if sender == delete_button:
                if i != 0:
                    if self.data_set.masks_sets.get_masks_number() >= 1:
                        self.data_set.masks_sets.del_mask(i)
                        self.delete_data()
                    self.data_set.set_cropped_state(False)
                    self.data_set.set_analyzed_state(False)
                    self.data_set.set_wrapped_state(False)
                    self.data_set.set_unwrapped_state(False)

                else:
                    self.data_set.masks_sets.reset_masks()
                    self.delete_data()
                self.init_data()
        self.masks_changed.emit()

    def _add_text(self, row: int, col: int, text: str, bold: bool=True):
        """
        Add a text in a cell.
        :param row: Row where to add the text.
        :param col: Column where to add the text.
        :param text: Text to write in the cell.
        :param bold: If true, text is bold.
        """
        item = QTableWidgetItem(text)
        if bold:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, col, item)

    def _add_select_checkbox(self, row: int, selected: bool=True):
        """
        Add a checkbox for selecting a mask in a cell.
        :param row: Row where to add the checkbox.
        :param selected: True if the mask is selected.
        """
        checkbox = QCheckBox()
        item = QWidget()
        layout = QHBoxLayout(item)
        checkbox.stateChanged.connect(self.select_mask)
        checkbox.setChecked(selected)
        self.select_list.append(checkbox)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCellWidget(row, 2, item)

    def _add_invert_checkbox(self, row: int, inverted: bool=False):
        """
        Add a checkbox for inverting a mask in a cell.
        :param row: Row where to add the checkbox.
        :param inverted: True if the mask is inverted.
        """
        checkbox = QCheckBox()
        item = QWidget()
        layout = QHBoxLayout(item)
        checkbox.stateChanged.connect(self.invert_mask)
        checkbox.setChecked(inverted)
        self.invert_list.append(checkbox)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCellWidget(row, 3, item)

    def _add_delete_button(self, row: int, text: str):
        """
        Add a button for deleting a mask in a cell.
        :param row: Row where to add the button.
        :param text: Text to display in the button.
        """
        button = QPushButton(text)
        item = QWidget()
        layout = QHBoxLayout(item)
        button.clicked.connect(self.delete_mask)
        self.delete_list.append(button)
        layout.addWidget(button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCellWidget(row, 4, item)


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_structure import MainView
    from models.dataset import DataSetModel
    from views.main_menu import MainMenu
    from controllers.masks_controller import MasksController

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    data_set = DataSetModel()
    m_app.data_set = data_set
    m_app.main_widget = MainView()
    m_app.main_menu = MainMenu()
    m_app.main_menu.load_menu('')
    manager = ModesManager(m_app)

    # Update data
    manager.data_set.load_images_set_from_file("../_data/test4.mat")
    manager.data_set.load_mask_from_file("../_data/test4.mat")
    controller = MasksController(manager)

    main_widget = MasksOptionsView(controller)
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test

    sys.exit(app.exec())