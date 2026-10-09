from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from lensepy import translate
from lensepy.css import *
from lensepy_app.widgets import make_hline


contributors_type = ['main_dev','dev','sciexp']

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


class DefaultBotRightWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent  # Controller
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.layout_left = QVBoxLayout()
        self.layout_right = QVBoxLayout()
        layout.addLayout(self.layout_left, 3)
        if self.parent.get_config('open_gl') is not None:
            layout.addWidget(Surface3DWidget(), 1)

    def init_ui(self):
        # Get list of contributors
        contributors_by_type = self.parent.get_contributors_by_type()
        for c_type in contributors_type:
            contributors = contributors_by_type.get(c_type, [])
            if len(contributors) != 0:
                title_label = QLabel(translate(f'contributors_{c_type}'))
                title_label.setStyleSheet(styleH3)
                self.layout_left.addWidget(title_label)
                for i, info in enumerate(contributors, 1):
                    c_name = f"\t{info['name']} ({info.get('organization', 'N/A')})"
                    contrib = QLabel(c_name)
                    self.layout_left.addWidget(contrib)

        self.layout_left.addStretch()


import pyqtgraph.opengl as gl
import numpy as np

class Surface3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = gl.GLViewWidget()
        layout.addWidget(self.view)
        self.view.opts["distance"] = 18
        self.view.opts["elevation"] = 30
        self.view.opts["azimuth"] = 45

        self.create_scene()

    def create_scene(self):
        n = 150
        x = np.linspace(-6, 6, n)
        y = np.linspace(-6, 6, n)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        Z = np.sin(R)*np.cos(R) / (R + 0.3)
        self.surface = gl.GLSurfacePlotItem( x=x, y=y, z=Z,
                                             shader="shaded", smooth=True, )
        self.surface.scale(1, 1, 3)
        self.view.addItem(self.surface)
