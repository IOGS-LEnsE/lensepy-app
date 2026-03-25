import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox,
    QGridLayout, QHBoxLayout
)

class MainWindow(QWidget):
    def __init(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()

        self.widget = QWidget()
        self.layout.addWidget(self.widget)