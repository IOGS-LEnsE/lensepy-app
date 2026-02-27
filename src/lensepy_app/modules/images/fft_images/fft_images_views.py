import cv2
import numpy as np
from lensepy import translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import SliderBloc
from lensepy.utils import make_hline
from lensepy.widgets import LabelWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QPushButton
)


class FFTImagesParamsWidget(QWidget):
    """
    Widget to display image infos.
    """
    mask_changed = pyqtSignal(str, float)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        layout = QVBoxLayout()
        self.image = self.parent.parent.variables['image']
        self.radius_max = np.min([self.image.shape[0], self.image.shape[1]]) // 2
        self.mask_choice = None

        label = QLabel(translate('fft_image_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addWidget(make_hline())

        self.radius_value = SliderBloc(translate('radius_fft'), unit='',
                                       min_value=1, max_value=self.radius_max,
                                       integer=True)
        self.radius_value.slider.setValue(10)
        #self.radius_value.slider.setEnabled(False)
        self.radius_value.slider_changed.connect(self.handle_mask_creation)
        layout.addWidget(self.radius_value)

        self.button_circular = QPushButton(translate('button_circular_fft'))
        self.button_circular.setStyleSheet(unactived_button)
        self.button_circular.clicked.connect(self.handle_mask_creation)
        layout.addWidget(self.button_circular)

        self.button_square = QPushButton(translate('button_square_fft'))
        self.button_square.setStyleSheet(unactived_button)
        self.button_square.clicked.connect(self.handle_mask_creation)
        layout.addWidget(self.button_square)

        layout.addWidget(make_hline())

        layout.addStretch()
        self.setLayout(layout)

    def handle_mask_creation(self):
        """"""
        sender = self.sender()
        radius = self.radius_value.get_value()
        if sender == self.button_circular:
            self.mask_choice = 'circular'
            self.mask_changed.emit('circular', radius)
        elif sender == self.button_square:
            self.mask_choice = 'square'
            self.mask_changed.emit('square', radius)
        else:
            self.mask_changed.emit(self.mask_choice, radius)

    def update_infos(self, image: np.ndarray):
        """
        Update information from image.
        :param image:   Displayed image.
        """
        self.image = image
        if self.image is not None:
            self.label_w.set_value(f'{self.image.shape[1]}')
            self.label_h.set_value(f'{self.image.shape[0]}')
            if self.image.ndim == 2:
                self.label_type.set_value(f'GrayScale')
            else:
                self.label_type.set_value(f'RGB')


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from matplotlib import pyplot as plt
    app = QApplication(sys.argv)
    image = cv2.imread('./robot.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    w = FFTImagesParamsWidget()
    w.resize(800, 600)
    w.show()

    # Exemple : image RGB aléatoire


    sys.exit(app.exec())
