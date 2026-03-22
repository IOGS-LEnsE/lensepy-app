# -*- coding: utf-8 -*-
"""*help_controller.py* file.

./controllers/help_controller.py contains HelpController class to manage "help" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout,
    QMessageBox, QFileDialog, QDialog
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager


class HelpController:
    """
    Help mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager: "ModesManager" = manager
        self.main_widget: MainView = self.manager.main_widget
        # Graphical elements
        self.top_left_widget = QWidget()        # Display ?
        self.top_right_widget = QWidget()       # Display ?
        self.bot_right_widget = QWidget()       # HTML Help on images
        # Submenu
        self.submenu = SubMenu('submenu_help')
        self.submenu.load_menu('menu/help_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        # Option 2

        #Init view
        self.init_view()
        print('HelpController / Help Mode')

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Update menu
        self.update_submenu_view("")

    def update_submenu_view(self, submode):
        """

        :param submode:
        :return:
        """
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, False)
        self.submenu.set_button_enabled(1, True)
        ## Update menu
        match submode:
            case 'open_images':
                self.submenu.set_activated(1)
            case 'display_images':
                self.submenu.set_activated(2)

    def update_submenu(self, event):
        """

        :param event:
        :return:
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        #print(event)

