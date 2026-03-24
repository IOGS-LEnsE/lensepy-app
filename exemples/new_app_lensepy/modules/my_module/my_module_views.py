from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from lensepy import translate
from lensepy.css import *


class MyModuleTopLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel('Top Left')
        layout.addWidget(label)
        self.setLayout(layout)

class MyModuleBotLeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel('Bot Left')
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        self.setLayout(layout)

    def handle_opening(self):
        '''TO DO !'''
        print('Handle opening')