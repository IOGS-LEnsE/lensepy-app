# -*- coding: utf-8 -*-
"""*sub_menu.py* file.

./views/sub_menu.py contains SubMenu class to display the main menu.

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
    QVBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal


class SubMenu(QWidget):
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

    def inactive_buttons(self):
        """ Switches all buttons to inactive style """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.buttons_enabled[i]:
                    element.setStyleSheet(unactived_button)

    def disable_buttons(self):
        '''Disables all buttons on the panel'''
        for i, element in enumerate(self.buttons_list):
            self.buttons_enabled[i] = False
            if element is not None:
                self.buttons_list[i].setEnabled(False)
                self.buttons_list[i].setStyleSheet(disabled_button)
        QApplication.processEvents()

    def enable_buttons(self):
        '''Enables all buttons on the panel'''
        for i, element in enumerate(self.buttons_list):
            self.buttons_enabled[i] = True
            if element is not None:
                self.buttons_list[i].setEnabled(True)
                self.buttons_list[i].setStyleSheet(unactived_button)
        QApplication.processEvents()

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

    '''
    def set_enabled(self, index: int, value: bool = True):
        """
        Set enabled a button.
        :param index:
        :param value:
        """
        menu = self.parent.get_list_menu('off_menu')
        if isinstance(index, list):
            for i in index:
                if i not in menu:
                    self.buttons_enabled[i - 1] = value
                else:
                    self.buttons_enabled[i - 1] = False
        else:
            if index not in menu:
                self.buttons_enabled[index - 1] = value
            else:
                self.buttons_enabled[index - 1] = False
        self.update_menu_display()
    '''

    def set_activated(self, index: int):
        """
        Set activated a button.
        :param index:
        """
        self.inactive_buttons()
        if isinstance(index, list):
            for i in index:
                self.buttons_list[i - 1].setStyleSheet(actived_button)
        else:
            self.buttons_list[index - 1].setStyleSheet(actived_button)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    def update_menu(event):
        print(event)

    app = QApplication(sys.argv)
    main_widget = SubMenu()
    main_widget.load_menu('../menu/images_menu.txt')
    main_widget.menu_changed.connect(update_menu)
    main_widget.show()

    sys.exit(app.exec())