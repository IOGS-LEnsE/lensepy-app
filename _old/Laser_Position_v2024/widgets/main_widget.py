# -*- coding: utf-8 -*-
"""*main_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *

BOT_HEIGHT, TOP_HEIGHT = 45, 50
LEFT_WIDTH, RIGHT_WIDTH = 45, 45
TOP_LEFT_ROW, TOP_LEFT_COL = 1, 1
TOP_RIGHT_ROW, TOP_RIGHT_COL = 1, 2
BOT_LEFT_ROW, BOT_LEFT_COL = 2, 1
BOT_RIGHT_ROW, BOT_RIGHT_COL = 2, 2
SUBMENU_ROW, SUBMENU_COL = 0, 0
OPTIONS_ROW, OPTIONS_COL = 0, 1

# Other functions
def load_menu(file_path: str, menu):
    """
    Load parameter from a CSV file.
    """
    print(file_path)
    if os.path.exists(file_path):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for element, title, signal, _ in data:
            if element == 'B':     # button
                menu.add_button(translate(title), signal)
            elif element == 'O':   # options button
                menu.add_button(translate(title), signal, option=True)
            elif element == 'L':   # label title
                menu.add_label_title(translate(title))
            elif element == 'S':   # blank space
                menu.add_space()
        menu.display_layout()
    else:
        print('MENU File error')

# %% Widgets
class MenuWidget(QWidget):
    """
    Main menu of the application
    """

    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None, title: str='label_title_main_menu', sub: bool=False):
        """
        Default Constructor.
        :param parent:
        :param title:
        :param sub:
        """
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.submenu = sub
        self.setLayout(self.layout)
        self.buttons_list = []
        self.buttons_signal = []
        self.buttons_enabled = []

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

    def add_button(self, title: str, signal: str=None, option: bool=False):
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
        self.buttons_enabled[button_index-1] = value
        self.buttons_list[button_index-1].setEnabled(value)
        if value:
            self.buttons_list[button_index-1].setStyleSheet(unactived_button)
        else:
            self.buttons_list[button_index-1].setStyleSheet(disabled_button)

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

    def menu_is_clicked(self):
        self.inactive_buttons()
        sender = self.sender()

        for i, element in enumerate(self.buttons_list):
            if sender == element:
                if self.submenu is False:
                # Update Sub Menu
                    self.parent.submenu_widget = MenuWidget(self.parent,
                                                            title=f'sub_menu_{self.buttons_signal[i]}',
                                                            sub=True)
                    self.parent.submenu_widget.menu_clicked.connect(self.submenu_is_clicked)
                    file_name = f'./config/{self.buttons_signal[i]}_menu.txt'
                    load_menu(file_name, self.parent.submenu_widget)
                    self.parent.set_sub_menu_widget(self.parent.submenu_widget)
                    self.parent.submenu_widget.display_layout()
                # Change button style
                sender.setStyleSheet(actived_button)
                # Send signal
                self.menu_clicked.emit(self.buttons_signal[i])

    def submenu_is_clicked(self, event):
        self.menu_clicked.emit(event)

class TitleWidget(QWidget):
    """
    Widget containing the title of the application and the LEnsE logo.
    """
    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the title widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.label_title = QLabel(translate('label_title'))
        self.label_title.setStyleSheet(styleH1)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_subtitle = QLabel(translate('label_subtitle'))
        self.label_subtitle.setStyleSheet(styleH3)
        self.label_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lense_logo = QLabel('Logo')
        self.lense_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QPixmap("./assets/IOGS-LEnsE-logo_small.jpg")
        # logo = logo_.scaled(imageSize.width()//4, imageSize.height()//4, Qt.AspectRatioMode.KeepAspectRatio)
        self.lense_logo.setPixmap(logo)

        self.layout.addWidget(self.label_title, 0, 0)
        self.layout.addWidget(self.label_subtitle, 1, 0)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 5)
        self.layout.addWidget(self.lense_logo, 0, 1, 2, 1)

        self.setLayout(self.layout)

class MainWidget(QWidget):
    """
    Main central widget of the application.
    """

    main_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        try:
            # GUI Structure
            self.layout = QGridLayout()
            self.title_label = TitleWidget(self)
            self.main_menu = MenuWidget(self)
            self.top_left_widget = QWidget()
            self.top_right_widget = QWidget()
            self.bot_right_widget = QWidget()
            # Submenu and option widgets in the bottom left corner of the GUI
            self.bot_left_widget = QWidget()
            self.bot_left_layout = QGridLayout()
            self.bot_left_widget.setLayout(self.bot_left_layout)
            self.bot_left_layout.setColumnStretch(0, 50)
            self.bot_left_layout.setColumnStretch(1, 50)
            self.submenu_widget = QWidget()
            self.options_widget = QWidget()
            self.layout.addWidget(self.title_label, 0, 0, 1, 3)
            self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)
            self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)
            self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

            self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)
            self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
            self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

            self.main_menu.menu_clicked.connect(self.menu_action)

            # Adding elements in the layout
            self.layout.addWidget(self.main_menu, 1, 0, 2, 1)
            self.layout.setColumnStretch(0, 10)
            self.layout.setColumnStretch(1, 45)
            self.layout.setColumnStretch(2, 45)
            self.layout.setRowStretch(0, 5)
            self.layout.setRowStretch(1, 50)
            self.layout.setRowStretch(2, 45)
            self.setLayout(self.layout)
        except Exception as e:
            print(e)

    def clear_layout(self, row: int, column: int) -> None:
        """
        Remove widgets from a specific position in the layout.
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

    def clear_sublayout(self, column: int) -> None:
        """
        Remove widgets from a specific position in the layout of the bottom left area.
        :param column: Column index of the layout.
        """
        item = self.bot_left_layout.itemAtPosition(0, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def update_size(self, aoi: bool = False):
        """
        Update the size of the main widget.
        """
        pass

    def set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

    def set_top_right_widget(self, widget):
        """
        Modify the top right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def set_bot_left_widget(self, widget):
        """
        Modify the bottom left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_LEFT_ROW, BOT_LEFT_COL)
        self.bot_left_widget = widget
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

    def set_bot_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.bot_right_widget = widget
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def set_sub_menu_widget(self, widget):
        """
        Modify the sub menu widget.
        :param widget: Widget of the sub menu.
        """
        self.clear_sublayout(SUBMENU_COL)
        self.submenu_widget = widget
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)

    def set_options_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(OPTIONS_COL)
        self.options_widget = widget
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)

    def menu_action(self, event):
        """
        Action performed when a button of the main menu is clicked.
        Only GUI actions are performed in this section.
        :param event: Event that triggered the action.
        """
        self.main_signal.emit(event)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = MainWidget(self)
            self.setCentralWidget(self.central_widget)

        def create_gui(self):
            widget1 = QWidget()
            widget1.setStyleSheet('background-color: red;')
            self.central_widget.set_top_left_widget(widget1)
            widget2 = QWidget()
            widget2.setStyleSheet('background-color: blue;')
            self.central_widget.set_top_right_widget(widget2)
            widget3 = QWidget()
            widget3.setStyleSheet('background-color: green;')
            self.central_widget.set_sub_menu_widget(widget3)
            widget4 = QWidget()
            widget4.setStyleSheet('background-color: yellow;')
            self.central_widget.set_bot_right_widget(widget4)

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
    main.create_gui()
    main.show()
    sys.exit(app.exec())
