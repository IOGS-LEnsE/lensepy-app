import sys

from PyQt6.QtCore import Qt
from lensepy.css import *
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QVBoxLayout,
    QLabel, QPushButton
)


class My_Application(QApplication):

    def __init__(self, app_name=None, standalone=False, argv=None):
        if argv is None:
            argv = sys.argv
        super().__init__(argv)

        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("My App")

        title = QLabel('LEnsEpy-APP')
        title.setStyleSheet(styleH1)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button = QPushButton("Click me")
        button.clicked.connect(self.button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.main_window.setCentralWidget(container)
        self.main_window.show()

    def button_clicked(self):
        print("Button was clicked!")

if __name__ == "__main__":
    select_app = My_Application(sys.argv)
    select_app.exec()
