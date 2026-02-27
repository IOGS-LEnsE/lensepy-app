from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from lensepy.css import *
from lensepy.utils import make_hline


class DefaultTopLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.layout = QVBoxLayout()
        label = QLabel('Top Left')
        self.layout.addWidget(label)
        self.setLayout(self.layout)

    def _delete_items(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._delete_items()

    def display(self, config):
        """
        Display title of the application and main information
        :param config:  list of information (stored in the config list of the main_app)
        """
        self._delete_items()    # Delete all the objects in the main layout
        self.layout.addWidget(make_hline())
        label = QLabel(config['name'])
        label.setStyleSheet(styleH1)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        self.layout.addWidget(make_hline())
        label = QLabel(config['description'])
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)
        self.layout.addStretch()
        label = QLabel(f'Developped by {config["organization"]} in {config["year"]}')
        label.setStyleSheet(styleH3)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label)

        self.layout.addStretch()

class DefaultBotLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        layout = QVBoxLayout()
        label = QLabel('Bot Left')
        layout.addWidget(label)
        self.setLayout(layout)