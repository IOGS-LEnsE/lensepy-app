# -*- coding: utf-8 -*-
"""*main_structure.py* file.

./views/main_structure.py contains MainView class to display the global application.

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
from lensepy import load_dictionary, translate, dictionary
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QResizeEvent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.title_view import TitleView
from views.sub_menu import SubMenu


MENU_WIDTH = 10
BOT_HEIGHT, TOP_HEIGHT = 45, 50
LEFT_WIDTH, RIGHT_WIDTH = 45, 45
TOP_LEFT_ROW, TOP_LEFT_COL = 1, 1
TOP_RIGHT_ROW, TOP_RIGHT_COL = 1, 2
BOT_LEFT_ROW, BOT_LEFT_COL = 2, 1
BOT_RIGHT_ROW, BOT_RIGHT_COL = 2, 2
SUBMENU_ROW, SUBMENU_COL = 0, 0
OPTIONS1_ROW, OPTIONS1_COL = 0, 1
OPTIONS2_ROW, OPTIONS2_COL = 0, 2

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zygo_lab_app import ZygoApp
    from controllers.acquisition_controller import AcquisitionController


class MainView(QWidget):
    """
    Main central widget of the application.
    """

    main_signal = pyqtSignal(str)

    def __init__(self, main_app: "ZygoApp" = None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__()
        self.main_app: "ZygoApp" = main_app
        # Layout
        self.layout = QGridLayout()

        # Graphical containers
        self.title = TitleView()
        self.main_menu = QWidget()
        self.top_left_widget = QWidget()
        self.top_right_widget = QWidget()
        self.bot_right_widget = QWidget()
        # Submenu and option widgets in the bottom left corner of the GUI
        self.bot_left_widget = QWidget()
        self.bot_left_layout = QGridLayout()
        self.bot_left_widget.setLayout(self.bot_left_layout)
        self.bot_left_layout.setColumnStretch(0, 50)
        self.bot_left_layout.setColumnStretch(1, 50)
        self.bot_left_layout.setColumnStretch(2, 50)
        self.submenu_widget = QWidget()
        self.options1_widget = QWidget()
        self.options2_widget = QWidget()
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)
        self.bot_left_layout.addWidget(self.options1_widget, OPTIONS1_ROW, OPTIONS1_COL)
        self.bot_left_layout.addWidget(self.options2_widget, OPTIONS2_ROW, OPTIONS2_COL)
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

        # Adding elements in the layout
        self.layout.addWidget(self.title, 0, 0, 1, 3)
        self.layout.addWidget(self.main_menu, 1, 0, 2, 1)
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, LEFT_WIDTH)
        self.layout.setColumnStretch(2, RIGHT_WIDTH)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, TOP_HEIGHT)
        self.layout.setRowStretch(2, BOT_HEIGHT)
        self.setLayout(self.layout)

    def clear_all(self):
        """
        Clear all the widgets.
        """
        self._clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self._clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self._clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self._clear_sublayout(OPTIONS2_COL)
        self._clear_sublayout(OPTIONS1_COL)
        self._clear_sublayout(SUBMENU_COL)

    def set_main_menu(self, widget):
        """
        Modify the main_menu.
        :param widget: Widget to include inside the application.
        """
        self._clear_layout(1, 0)
        self.main_menu = widget
        self.layout.addWidget(self.main_menu, 1, 0, 2, 1)

    def set_top_right_widget(self, widget):
        """
        Modify the top right widget.
        :param widget: Widget to include inside the application.
        """
        self._clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self._clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

    def set_bot_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self._clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.bot_right_widget = widget
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def set_right_widget(self, widget):
        """
        Modify the two right widgets by only one widget.
        :param widget: Widget to include inside the application.
        """
        self._clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self._clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL, 2, 1)

    def set_sub_menu_widget(self, widget):
        """
        Modify the sub menu widget.
        :param widget: Widget of the sub menu.
        """
        self._clear_sublayout(SUBMENU_COL)
        self.submenu_widget = widget
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)

    def set_options1_widget(self, widget):
        """
        Modify the options1 widget.
        :param widget: Widget to display on "Options1" area.
        """
        self._clear_sublayout(OPTIONS1_COL)
        self.options1_widget = widget
        self.bot_left_layout.addWidget(self.options1_widget, OPTIONS1_ROW, OPTIONS1_COL)

    def set_options2_widget(self, widget):
        """
        Modify the options2 widget.
        :param widget: Widget to display on "Options2" area.
        """
        self._clear_sublayout(OPTIONS2_COL)
        self.options2_widget = widget
        self.bot_left_layout.addWidget(self.options2_widget, OPTIONS2_ROW, OPTIONS2_COL)

    def set_options_widget(self, widget):
        """
        Modify the two options widget. Display on the two columns.
        :param widget: Widget to display on the two "Options" columns.
        :return:
        """
        self._clear_sublayout(OPTIONS2_COL)
        self._clear_sublayout(OPTIONS1_COL)
        self.options1_widget = widget
        self.bot_left_layout.addWidget(self.options1_widget, OPTIONS1_ROW, OPTIONS1_COL, 1, 2)

    def clear_top_left(self):
        """
        Remove widget from top left area.
        """
        self._clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)

    def clear_top_right(self):
        """
        Remove widget from top right area.
        """
        self._clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def clear_bot_right(self):
        """
        Remove widget from bottom right area.
        """
        self._clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def clear_options(self):
        """
        Remove widgets in options area.
        """
        self._clear_sublayout(OPTIONS1_COL)
        self._clear_sublayout(OPTIONS2_COL)

    def _clear_layout(self, row: int, column: int) -> None:
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
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()
                widget.setParent(None)

    def _clear_sublayout(self, column: int) -> None:
        """
        Remove widgets from a specific position in the layout of the bottom left area.
        :param column: Column index of the layout.
        """
        item = self.bot_left_layout.itemAtPosition(0, column)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                self.bot_left_layout.removeWidget(widget)
                widget.deleteLater()
                widget.setParent(None)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        pass

    def closeEvent(self, event):
        """
        Close event.
        """
        camera = self.main_app.data_set.acquisition_mode.camera
        if self.main_app.data_set.acquisition_mode.is_camera():
            camera.stop_acquisition()
            camera.free_memory()
        controller = self.main_app.mode_manager.mode_controller
        print('End of APP')


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_widget = MainView()
    main_widget.showMaximized()

    widget1 = QWidget()
    widget2 = QWidget()
    widget3 = QWidget()
    widget1.setStyleSheet("background-color: blue;")
    main_widget.set_top_left_widget(widget1)
    widget2.setStyleSheet("background-color: lightgreen;")
    main_widget.set_bot_right_widget(widget2)
    widget3.setStyleSheet("background-color: red;")
    main_widget.set_options1_widget(widget3)

    sys.exit(app.exec())