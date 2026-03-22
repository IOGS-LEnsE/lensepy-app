# -*- coding: utf-8 -*-
"""*main_menu.py* file.

./views/main_menu.py contains MainMenu class to display the main menu.

--------------------------------------
| Menu |  TOPLEFT     |  TOPRIGHT    |
|      |              |              |
|      |--------------|--------------|
|      |SUB |OPTS|OPTS|  BOTRIGHT    |
|      |MENU| 1  | 2  |              |
--------------------------------------

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal


class MainMenu(QWidget):
    """
    Main central widget of the application.
    """

    menu_changed = pyqtSignal(str)

    def __init__(self, title: str = 'label_title_main_menu'):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        :param title: Title of the menu.
        """
        super().__init__()
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.buttons_list = []
        self.buttons_signal = []
        self.buttons_enabled = []
        self.buttons_options_list = []
        self.options_list = []
        self.actual_button = None

        self.label_title_main_menu = QLabel(translate(title))
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_title_main_menu)

    def display_layout(self):
        """
        Update the layout with all the elements.
        """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                self.layout.addWidget(element)
            else:
                self.layout.addStretch()

    def load_menu(self, file_path: str):
        """
        Load the main menu from a file.
        :param file_path: Filename of the file containing main menu.
        """
        """
        Load parameter from a CSV file.
        """
        if os.path.exists(file_path):
            # Read the txt file, ignoring lines starting with '#'
            data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the txt file
            for element, title, signal, option_list, _ in data:
                if element == 'B':  # button
                    self.add_button(translate(title), signal)
                elif element == 'O':  # options button
                    self.add_button(translate(title), signal, option=True)
                elif element == 'L':  # label title
                    self.add_label_title(translate(title))
                elif element == 'S':  # blank space
                    self.add_space()
                self.buttons_options_list.append(option_list.split(','))
            self.display_layout()
        else:
            print('MENU File error')

    def add_button(self, title: str, signal: str = None, option: bool = False):
        """
        Add a button into the interface.
        :param title: Title of the button.
        :param signal: Signal triggered by the button.
        :param option: True if the button is an option button (smaller height).
        :return:
        """
        button = QPushButton(translate(title))
        button.setStyleSheet(unactived_button)
        if option:
            button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        else:
            button.setFixedHeight(BUTTON_HEIGHT)
        button.clicked.connect(self.menu_is_clicked)
        self.buttons_list.append(button)
        self.buttons_signal.append(signal)
        self.buttons_enabled.append(True)

    def add_label_title(self, title):
        """
        Add a space in the menu.
        :param title: Title of the label.
        """
        label = QLabel(title)
        label.setStyleSheet(styleH1)
        self.buttons_list.append(label)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def add_space(self):
        """
        Add a space in the menu.
        :param title:
        :param signal:
        :return:
        """
        self.buttons_list.append(None)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def update_options(self, options_list):
        """
        Update the options list from the manager, depending on the mode and the connected hardware.
        :param options_list: list of options (nocam, nopiezo, nodata, nomask, noanalysis)
        """
        self.options_list = options_list
        # Erase enabled list for buttons
        for k in range(len(self.buttons_list)):
            self.set_button_enabled(k+1, True)
        # Update enabled buttons
        for option in self.options_list:
            for k in range(len(self.buttons_list)):
                if option in self.buttons_options_list[k]:
                    self.set_button_enabled(k+1, False)

    def get_options_list(self) -> list[str]:
        """
        Return the actual list of options. (nocam, nopiezo, nodata, nomask, noanalysis).
        :return: list of Options.
        """
        return self.options_list

    def inactive_buttons(self):
        """ Switches all buttons to inactive style """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.buttons_enabled[i]:
                    element.setStyleSheet(unactived_button)

    def set_button_enabled(self, button_index: int, value: bool):
        """
        Set a button enabled.
        :param button_index: Index of the button to update.
        :param value: True if the button must be enabled.
        """
        button = self.buttons_list[button_index - 1]
        if button != None:
            self.buttons_enabled[button_index - 1] = value
            self.buttons_list[button_index - 1].setEnabled(value)
            if value:
                self.buttons_list[button_index - 1].setStyleSheet(unactived_button)
            else:
                self.buttons_list[button_index - 1].setStyleSheet(disabled_button)

    def menu_is_clicked(self):
        self.inactive_buttons()
        sender = self.sender()
        self.actual_button = sender
        # Find the good
        for i, element in enumerate(self.buttons_list):
            if sender == element:
                # Change button style
                sender.setStyleSheet(actived_button)
                # Send signal
                self.menu_changed.emit(self.buttons_signal[i])

    def update_menu_display(self):
        """Update the menu."""
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.actual_button == element:
                    element.setStyleSheet(actived_button)
                    element.setEnabled(True)
                elif self.buttons_enabled[i] is True:
                    element.setStyleSheet(unactived_button)
                    element.setEnabled(True)
                else:
                    element.setStyleSheet(disabled_button)
                    element.setEnabled(False)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    def update_menu(event):
        print(event)

    app = QApplication(sys.argv)
    main_widget = MainMenu()
    main_widget.load_menu('../menu/menu.txt')
    options_list = ['nocam', 'nodata','noanalysis']
    main_widget.update_options(options_list)
    main_widget.menu_changed.connect(update_menu)
    main_widget.show()

    sys.exit(app.exec())