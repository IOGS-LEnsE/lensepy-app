from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from lensepy import translate

from lensepy.css import *
from lensepy_app.widgets.objects import *
from lensepy_app.widgets import ImageDisplayWidget


class FyzoFFTOptionsView(QWidget):

    display_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('fyzo_analysis_parameter_label'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # different display
        self.interfer_button = QPushButton(translate('interfer_display_button'))
        self.interfer_button.setStyleSheet(unactived_button)
        self.interfer_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.interfer_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.interfer_button)

        self.fft_button = QPushButton(translate('fft_display_button'))
        self.fft_button.setStyleSheet(unactived_button)
        self.fft_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_button)

        self.fft_circled_button = QPushButton(translate('fft_circled_display_button'))
        self.fft_circled_button.setStyleSheet(unactived_button)
        self.fft_circled_button.setFixedHeight(BUTTON_HEIGHT)
        self.fft_circled_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_circled_button)

        layout.addStretch()
        self.setLayout(layout)


    def _inactivate_buttons(self):
        self.fft_button.setStyleSheet(unactived_button)
        self.interfer_button.setStyleSheet(unactived_button)
        self.fft_circled_button.setStyleSheet(unactived_button)

    def activate_mode(self, mode, value=True):
        self._inactivate_buttons()
        if mode == 'fft_circled':
            self.fft_circled_button.setStyleSheet(actived_button)
        elif mode == 'interfer':
            self.interfer_button.setStyleSheet(actived_button)
        elif mode == 'fft':
            self.fft_button.setStyleSheet(actived_button)

    def handle_display_changed(self):
        sender = self.sender()
        self._inactivate_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.interfer_button:
            self.display_changed.emit('interfer')
        elif sender == self.fft_button:
            self.display_changed.emit('fft')
        elif sender == self.fft_circled_button:
            self.display_changed.emit('fft_circled')
        else:
            self.display_changed.emit('fft_circled')

