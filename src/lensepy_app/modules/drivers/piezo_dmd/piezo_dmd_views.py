import sys, time
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton,
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QLabel, QFormLayout, QGroupBox
)

from lensepy import translate
from lensepy.utils import *
from lensepy.widgets import *


class DMDParamsView(QWidget):
    """

    """

    image_set = pyqtSignal(int)
    image_view = pyqtSignal(int)
    image_sent = pyqtSignal(int)

    def __init__(self, parent=None):
        """

        """
        super(DMDParamsView, self).__init__(None)
        self.parent = parent
        layout = QVBoxLayout()

        layout.addWidget(make_hline())
        label = QLabel(translate('dmd_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        layout.addStretch()
        self.image = [None]*3
        self.image_ok = [False]*3
        for k in range(3):
            self.image[k] = ImageOpenWidget(number=k+1)
            layout.addWidget(self.image[k])
            layout.addWidget(make_hline())

        self.camera_button = QPushButton(translate('dmd_camera_view_button'))
        self.camera_button.setStyleSheet(disabled_button)
        self.camera_button.setEnabled(False)
        self.camera_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.camera_button)

        layout.addStretch()

        self.setLayout(layout)

        # Signals
        for k in range(3):
            self.image[k].image_set.connect(self.handle_image_set)
            self.image[k].image_view.connect(self.handle_image_view)
            self.image[k].image_sent.connect(self.handle_image_sent)

    def handle_image_set(self):
        """Action performed when an image is opened."""
        sender = self.sender()
        for k in range(3):
            if sender == self.image[k]:
                self.image_set.emit(k+1)

    def handle_image_view(self):
        """Action performed when an image has to be displayed."""
        sender = self.sender()
        self.set_all_view_inactive()
        self.set_all_send_inactive()
        for k in range(3):
            if sender == self.image[k]:
                self.image_view.emit(k+1)
                self.image[k].set_view_active(True)

    def handle_image_sent(self):
        """Action performed when an image has to be displayed."""
        sender = self.sender()
        self.set_all_view_inactive()
        self.set_all_send_inactive()
        for k in range(3):
            if sender == self.image[k]:
                self.image_sent.emit(k+1)
                self.image[k].set_view_active(True)
                self.image[k].set_send_active(True)

    def set_camera_enabled(self, enabled=True):
        """Set the camera button enabled."""
        self.camera_button.setEnabled(enabled)
        if enabled:
            self.camera_button.setStyleSheet(unactived_button)
        else:
            self.camera_button.setStyleSheet(actived_button)

    def no_image(self):
        """Inactivate send and view button."""
        for k in range(3):
            self.image[k].no_image()

    def set_image_opened(self, number, opened=True):
        """
        Set image opened.
        :param number:  number of the opened image.
        :param opened: whether opened or not.
        """
        self.image_ok[number-1] = opened
        self.set_enabled(number)

    def set_all_view_inactive(self, active=False):
        """Set all the view button inactive."""
        for k in range(3):
            if self.image_ok[k]:
                self.image[k].set_view_active(active)

    def set_all_send_inactive(self, active=False):
        """Set all the send button inactive."""
        for k in range(3):
            if self.image_ok[k]:
                self.image[k].set_send_active(active)

    def set_enabled(self, number):
        """Set enabled buttons."""
        if self.image_ok[number-1]:
            self.image[number-1].set_enabled()

    def set_path_to_image(self, number, path):
        """
        Set image path.
        :param number:  number of the opened image.
        :param path: image path.
        """
        self.image[number-1].set_path(path)


class ImageOpenWidget(QWidget):

    image_set = pyqtSignal()
    image_view = pyqtSignal()
    image_sent = pyqtSignal()

    def __init__(self, parent=None, number=1):
        super().__init__(None)
        self.parent = parent
        self.number = number
        self.path = ''

        layout = QVBoxLayout()
        # Title
        label = QLabel(translate('mire_title')+ f' {self.number}')
        label.setStyleSheet(styleH3)
        layout.addWidget(label)
        # Open / View image
        widget = QWidget()
        h_layout = QHBoxLayout()
        widget.setLayout(h_layout)
        layout.addWidget(widget)
        self.open_button = QPushButton(translate('dmd_open_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        h_layout.addWidget(self.open_button)
        self.view_button = QPushButton(translate('dmd_view_button'))
        self.view_button.setStyleSheet(unactived_button)
        self.view_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        h_layout.addWidget(self.view_button)
        self.send_button = QPushButton(translate('dmd_send_button'))
        self.send_button.setStyleSheet(unactived_button)
        self.send_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        h_layout.addWidget(self.send_button)

        # Label for displaying path of image
        self.image_path = QLabel(translate('image_path'))
        layout.addWidget(self.image_path)
        self.setLayout(layout)

        # Handle
        self.open_button.clicked.connect(self.handle_opening)
        self.view_button.clicked.connect(self.handle_viewing)
        self.send_button.clicked.connect(self.handle_sending)

    def set_view_active(self, active=True):
        if active:
            self.view_button.setStyleSheet(actived_button)
        else:
            self.view_button.setStyleSheet(unactived_button)

    def set_send_active(self, active=True):
        if active:
            self.send_button.setStyleSheet(actived_button)
        else:
            self.send_button.setStyleSheet(unactived_button)

    def no_image(self):
        """Initialize the button as disabled"""
        self.send_button.setStyleSheet(disabled_button)
        self.send_button.setEnabled(False)
        self.view_button.setStyleSheet(disabled_button)
        self.view_button.setEnabled(False)

    def set_enabled(self):
        """Set enabled buttons."""
        self.send_button.setStyleSheet(unactived_button)
        self.send_button.setEnabled(True)
        self.view_button.setStyleSheet(unactived_button)
        self.view_button.setEnabled(True)

    def set_path(self, path):
        """Set image path."""
        self.path = path
        self.image_path.setText(path)

    def handle_opening(self):
        """Action performed when the open button is clicked."""
        self.open_button.setStyleSheet(actived_button)
        self.repaint()
        ## Send signal
        self.image_set.emit()

    def handle_viewing(self):
        """Action performed when the view button is clicked."""
        self.view_button.setStyleSheet(actived_button)
        self.repaint()
        self.image_view.emit()

    def handle_sending(self):
        """Action performed when the view button is clicked."""
        self.send_button.setStyleSheet(actived_button)
        self.repaint()
        self.image_sent.emit()


class PiezoParamsWidget(QWidget):

    board_connected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.boards_list = None

        # Graphical objects
        layout = QVBoxLayout()

        layout.addWidget(make_hline())
        label = QLabel(translate('piezo_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        layout.addStretch()

        self.boards_list_box = QComboBox()
        layout.addWidget(self.boards_list_box)
        self.board_connect_button = QPushButton(translate('piezo_connect'))
        self.board_connect_button.setStyleSheet(disabled_button)
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.board_connect_button)
        self.board_connect_button.clicked.connect(self.handle_piezo_connected)
        layout.addWidget(make_hline())

        self.z_value = SliderBloc(translate('z_slide_value'), 'um', 0, 2)
        layout.addWidget(self.z_value)
        self.setLayout(layout)

    def handle_piezo_connected(self):
        """Action performed when the piezo button is clicked."""
        board_number = self.boards_list_box.currentIndex()
        self.board_connected.emit(board_number)

    def set_boards_list(self, board_list):
        """Set the list of the serial port connected."""
        self.boards_list = board_list
        if len(board_list) != 0:
            self.boards_list_box.addItems(self.boards_list)
            self.board_connect_button.setStyleSheet(unactived_button)
            self.board_connect_button.setEnabled(True)
        self.update()

    def set_connected(self):
        """If a board is connected, disable connexion button."""
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(actived_button)
        self.board_connect_button.setText(translate('piezo_connected'))
        self.boards_list_box.setEnabled(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DMDParamsView()
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

