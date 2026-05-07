from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from lensepy import translate

from lensepy.css import *
from lensepy_app.widgets.objects import *
from lensepy_app.widgets import ImageDisplayWidget


class FyzoAnalysisOptionsView(QWidget):

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
        layout.addStretch()

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

        self.fft_masked_button = QPushButton(translate('fft_masked_display_button'))
        self.fft_masked_button.setStyleSheet(unactived_button)
        self.fft_masked_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_masked_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_masked_button)

        self.fft_centered_button = QPushButton(translate('fft_centered_display_button'))
        self.fft_centered_button.setStyleSheet(unactived_button)
        self.fft_centered_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_centered_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_centered_button)

        self.phase_button = QPushButton(translate('phase_display_button'))
        self.phase_button.setStyleSheet(unactived_button)
        self.phase_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.phase_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.phase_button)
        layout.addWidget(make_hline())
        self.surface_button = QPushButton(translate('surface_display_button'))
        self.surface_button.setStyleSheet(unactived_button)
        self.surface_button.setFixedHeight(BUTTON_HEIGHT)
        self.surface_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.surface_button)
        layout.addWidget(make_hline())

        # FFT display
        self.fft_display = ImageDisplayWidget()

        layout.addWidget(self.fft_display)
        self.display_small_fft(value=False)

        layout.addStretch()
        self.setLayout(layout)

    def activate_button(self, value):
        if value == 'surface':
            self.surface_button.setStyleSheet(actived_button)
        # TO COMPLETE

    def display_small_fft(self, image=None, value=True):
        if image is not None:
            self.fft_display.set_image_from_array(image)
        '''
        if value:
            if image is not None:
                self.fft_display.set_image_from_array(image)
            self.fft_display.show()
        else:
            self.fft_display.hide()
        '''

    def _inactivate_buttons(self):
        self.fft_button.setStyleSheet(unactived_button)
        self.interfer_button.setStyleSheet(unactived_button)
        self.fft_masked_button.setStyleSheet(unactived_button)
        self.fft_centered_button.setStyleSheet(unactived_button)
        self.phase_button.setStyleSheet(unactived_button)
        self.surface_button.setStyleSheet(unactived_button)

    def handle_display_changed(self):
        sender = self.sender()
        self._inactivate_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.interfer_button:
            self.display_changed.emit('interfer')
        elif sender == self.fft_button:
            self.display_changed.emit('fft')
        elif sender == self.fft_masked_button:
            self.display_changed.emit('fft_masked')
        elif sender == self.fft_centered_button:
            self.display_changed.emit('fft_centered')
        elif sender == self.phase_button:
            self.display_changed.emit('phase')
        elif sender == self.surface_button:
            self.display_changed.emit('surface')
        else:
            self.display_changed.emit('interfer')

