# -*- coding: utf-8 -*-
"""*widget_combobox* file.

*widget_combobox* file that contains :class::ComboBoxBloc

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSlider, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

# %% Widget
class ComboBoxBloc(QWidget):
    selection_changed = pyqtSignal(str)

    def __init__(self, title: str, list_options: list, default: bool = True) -> None:
        super().__init__(parent=None)

        self.layout = QHBoxLayout()

        self.label = QLabel(translate(title))
        self.label.setStyleSheet(styleH2)

        self.combobox = QComboBox()
        if default:
            self.combobox.addItem(translate('select_option_default'))
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)
        self.combobox.setStyleSheet(styleH3)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.combobox.currentTextChanged.connect(self.emit_selection_changed)

    def emit_selection_changed(self, text):
        self.selection_changed.emit(text)

    def update_options(self, list_options):
        self.combobox.clear()
        self.combobox.addItem(translate('select_option_default'))
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)

    def get_text(self):
        return self.combobox.currentText()

    def get_index(self):
        return self.combobox.currentIndex()


class ButtonSelectionWidget(QWidget):

    clicked = pyqtSignal(str)

    def __init__(self, parent=None, name: str = 'select_button'):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.select_layout = QGridLayout()
        self.setLayout(self.select_layout)
        self.label_select = QLabel(translate(name))
        self.list_options = []
        self.list_buttons = []
        self.selected = -1

    def display_selection(self):
        """Create the widget by inserting graphical elements."""
        self.select_layout.addWidget(self.label_select)
        for i, element in enumerate(self.list_options):
            button = QPushButton(element)
            button.setStyleSheet(styleH2)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.action_clicked)
            self.list_buttons.append(button)
            self.select_layout.addWidget(button, 0, i+1)

    def set_list_options(self, list):
        """Update the list of the options to select."""
        self.list_options = list
        nb = len(self.list_options)
        self.select_layout.setColumnStretch(0, 40)
        for i in range(1, nb+1):
            self.select_layout.setColumnStretch(i, 50//nb)
        self.display_selection()

    def action_clicked(self, event):
        """Action performed when an element is clicked."""
        sender = self.sender()
        for i in range(len(self.list_options)):
            if sender == self.list_buttons[i]:
                self.selected = i
                self.list_buttons[i].setStyleSheet(actived_button)
                self.clicked.emit(f'select_{i}')
            else:
                self.list_buttons[i].setStyleSheet(unactived_button)

    def get_selection(self):
        """Return the selected object value."""
        return self.list_options[self.selected]

    def get_selection_index(self):
        """Return the index of the selected object value."""
        return self.selected

    def activate_index(self, index):
        """Set active an object from its index.
        :param index: Index of the object to activate.
        """
        self.selected = index-1
        self.list_buttons[index-1].setStyleSheet(actived_button)


# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_combo_box_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = ComboBoxBloc(title='Title', list_options=['opt1', 'opt2'])
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
