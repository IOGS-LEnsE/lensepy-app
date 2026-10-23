__all__ = ["ImagesOpeningWidget", "ImagesInfosWidget"]

from PyQt6.QtCore import pyqtSignal, Qt
from lensepy import translate
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QWidget, QLabel, QVBoxLayout
)
from lensepy.utils import *
from lensepy_app import *
from lensepy_app.appli import *
from lensepy_app.widgets.objects import *

import numpy as np


class ImagesOpeningWidget(ModuleWidget):
    """
    Widget to display image opening options.
    """

    image_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('image_opening_dialog'))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.setFixedHeight(BUTTON_HEIGHT[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)

    def handle_opening(self):
        sender = self.sender()
        if sender == self.open_button:
            self.open_button.setStyleSheet(ACTIVATED_BUTTON[self.global_theme][self.global_mode])
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
                self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])

    def open_image(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_dir, "Images (*.png *.jpg *.jpeg)")
        if file_path != '':
            image_array, bits_depth = imread_rgb(file_path)
            self.controller.set_variables('image', image_array)
            self.controller.set_variables('bits_depth', bits_depth)
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


class ImagesInfosWidget(ModuleWidget):
    """
    Widget to display image infos.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()

        self.image = None

        label = QLabel(translate('image_infos_title'))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addWidget(make_hline())

        self.label_w = LabelWidget(translate("image_infos_label_w"), '',
                                   'pixels', parent=self.controller)
        layout.addWidget(self.label_w)
        self.label_h = LabelWidget(translate("image_infos_label_h"), '',
                                   'pixels', parent=self.controller)
        layout.addWidget(self.label_h)

        layout.addWidget(make_hline())

        self.label_type = LabelWidget(translate("image_infos_label_type"), '',
                                      '', parent=self.controller)
        layout.addWidget(self.label_type)

        layout.addStretch()
        self.setLayout(layout)
        self.hide()

    def update_infos(self, image: np.ndarray):
        """
        Update information from image.
        :param image:   Displayed image.
        """
        self.image = image
        if self.image is not None:
            self.show()
            self.label_w.set_value(f'{self.image.shape[1]}')
            self.label_h.set_value(f'{self.image.shape[0]}')
            if self.image.ndim == 2:
                self.label_type.set_value(f'GrayScale')
            else:
                self.label_type.set_value(f'RGB')
        else:
            self.hide()

