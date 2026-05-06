from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from lensepy import translate

from lensepy.css import *
from lensepy_app.widgets.objects import *
from lensepy_app.widgets import ImageDisplayWidget


class FyzoAnalysisOptionsView(QWidget):

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('fyzo_analysis_parameter_label'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()

        # FFT parameters
        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        #self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)
        layout.addWidget(make_hline())

        # FFT display
        self.fft_display = ImageDisplayWidget()

        layout.addWidget(self.fft_display)
        self.display_small_fft(value=False)

        layout.addStretch()
        self.setLayout(layout)

    def display_small_fft(self, image=None, value=True):
        if value:
            if image is not None:
                self.fft_display.set_image_from_array(image)
            self.fft_display.show()
        else:
            self.fft_display.hide()