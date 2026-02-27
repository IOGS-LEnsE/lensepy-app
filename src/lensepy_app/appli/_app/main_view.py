from lensepy import translate
from lensepy.css import *
from PyQt6.QtWidgets import (
    QMainWindow, QSizePolicy,
    QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QWidget, QPushButton
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from typing import TYPE_CHECKING

from lensepy.appli._app.app_utils import XMLFileModule

if TYPE_CHECKING:
    from _app.main_manager import MainManager

class MainWindow(QMainWindow):
    """
    Main window of the application.
    """

    menu_changed = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent: MainManager = parent
        self.app_logo: LogoLabel = None
        self.menu_container = QWidget()
        self.menu_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_button_name_list = []
        self.menu_button_list = []
        self.actual_button = None

        self.right_container = QWidget()
        self.right_layout = QGridLayout()
        self.right_container.setLayout(self.right_layout)

        self.top_left_container = QWidget()
        self.top_right_container = QWidget()
        self.bot_left_container = QWidget()
        self.bot_right_container = QWidget()

        self.update_containers()

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.menu_container, 1)  # 1/7
        self.main_layout.addWidget(self.right_container, 6)  # 6/7

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def set_menu_elements(self, elements: list):
        """
        Create graphical elements of the main menu.
        :param elements: List of graphical elements to add.
        """
        self.menu_button_list = []
        for element in elements:
            b_title = translate(f'{element}_menu')
            button = QPushButton(b_title)
            button.clicked.connect(self.handle_main_menu)
            button.setFixedHeight(BUTTON_HEIGHT)
            self.menu_button_name_list.append(f'{element}')
            self.menu_button_list.append(button)
        # Logo
        if self.parent.app_logo != '':
            logo = QPixmap(self.parent.app_logo)
            self.app_logo = LogoLabel(logo)
            w_width = self.parent.main_window.width()
            h_width = self.parent.main_window.height()
            self.app_logo.setMinimumHeight(h_width // 4)
            self.app_logo.setMaximumWidth(w_width // 7)
            self.menu_layout.addWidget(self.app_logo)
        # Title
        if self.parent.app_title != '':
            app_title = QLabel(self.parent.app_title)
            app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            app_title.setStyleSheet(styleH2)
            self.menu_layout.addWidget(app_title)
        self.menu_layout.addStretch()
        self.update_menu()

    def update_menu(self):
        """

        :return:
        """
        for element in self.menu_button_list:
            if element == self.actual_button:
                element.setStyleSheet(actived_button)
                element.setEnabled(True)
            else:
                # CHECK IF REQUIRED VARIABLES ARE NOT NONE then UPDATE Menu
                module_name = self.menu_button_name_list[self.menu_button_list.index(element)]
                if self.check_variables(module_name):
                    element.setStyleSheet(unactived_button)
                    element.setEnabled(True)
                else:
                    # Check if the module has requirements (other module)
                    if self.parent.check_module_requirements(module_name):
                        element.setStyleSheet(unactived_button)
                        element.setEnabled(True)
                    else:
                        element.setStyleSheet(disabled_button)
                        element.setEnabled(False)
            self.menu_layout.addWidget(element)


    def check_variables(self, module) -> bool:
        """Check required variables for the specified module from the module XML file.
        :param module:      Name of the module to check.
        :return:            True if variables were checked.
        """
        var_list = []
        if module in self.parent.req_variables:
            var_module_list = self.parent.req_variables[module]
            if var_module_list is not None:
                var_module_list = self.parent.req_variables[module].split(',')
                for var_m in var_module_list:
                    if self.parent.get_variable(var_m) is None:
                        var_list.append(var_m)
        return len(var_list) == 0

    def handle_main_menu(self):
        """
        Action performed when a button in the menu is clicked.
        """
        self.actual_button = self.sender()
        indice = self.menu_button_list.index(self.actual_button)
        self.menu_changed.emit(self.menu_button_name_list[indice])
        self.update_menu()

    def update_containers(self):
        """Ajoute les widgets aux positions correctes du layout"""
        if self.top_left_container:
            self.right_layout.addWidget(self.top_left_container, 0, 0)
        if self.top_right_container:
            self.right_layout.addWidget(self.top_right_container, 0, 1)
        if self.bot_left_container:
            self.right_layout.addWidget(self.bot_left_container, 1, 0)
        if self.bot_right_container:
            self.right_layout.addWidget(self.bot_right_container, 1, 1)

    def set_mode1(self):
        """Disposition 2x2 (par défaut)"""
        self.right_layout.setColumnStretch(0, 1)
        self.right_layout.setColumnStretch(1, 1)
        self.right_layout.setRowStretch(0, 1)
        self.right_layout.setRowStretch(1, 1)

    def set_mode2(self):
        """Disposition 3/4 - 1/4 sur hauteur et 2/7 - 4/7 sur largeur"""
        self.right_layout.setColumnStretch(0, 2)
        self.right_layout.setColumnStretch(1, 1)
        self.right_layout.setRowStretch(0, 3)
        self.right_layout.setRowStretch(1, 1)

    def set_mode3(self):
        """Disposition 1 - 0 sur hauteur et 2/7 - 4/7 sur largeur"""
        self.right_layout.setColumnStretch(0, 2)
        self.right_layout.setColumnStretch(1, 1)
        self.right_layout.setRowStretch(0, 1)
        self.right_layout.setRowStretch(1, 0)

    def closeEvent(self, event):
        print('End of application')

    def resizeEvent(self, event):
        w_width = self.width()
        h_height = self.height()
        if self.app_logo:
            self.app_logo.setMinimumHeight(h_height // 6)
            self.app_logo.setMaximumWidth(w_width // 7 - 10)
            self.app_logo.update()  # force le repaint
        super().resizeEvent(event)


class LogoLabel(QLabel):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.original_pixmap = pixmap
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        scaled_pixmap = self.original_pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)
        super().resizeEvent(event)