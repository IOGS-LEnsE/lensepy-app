import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from lensepy_app.widgets.objects import make_hline
from lensepy import translate
from lensepy.utils import imread_rgb
from lensepy.css import *


class ImagesOpeningWidget(QWidget):
    """
    Widget to display image opening options.
    """

    image_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('image_opening_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)

    def handle_opening(self):
        sender = self.sender()
        if sender == self.open_button:
            self.open_button.setStyleSheet(actived_button)
            '''
            # Check if for a default directory for images.
            module_path = self.parent.parent.xml_app.get_module_parameter('images', 'imgdir')
            print(module_path)
            module = importlib.import_module(module_path)
            xml_path = os.path.dirname(module.__file__)
            print(f'Path = {test}')
            '''
            im_ok = self.open_image()
            if im_ok:
                self.open_button.setStyleSheet(unactived_button)

    def open_image(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_dir, "Images (*.png *.jpg *.jpeg)")
        if file_path != '':
            image_array, bits_depth = imread_rgb(file_path)
            self.parent.get_variables()['image'] = image_array
            self.parent.get_variables()['bits_depth'] = bits_depth
            self.image_opened.emit('image_opened')
            return True
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return False
