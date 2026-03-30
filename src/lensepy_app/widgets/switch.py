from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from lensepy.css import *


class Switch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self.setFixedSize(60, 30)
        self.animation = QPropertyAnimation(self, b"offset")
        self.animation.setDuration(200)
        self.offset = 2  # Position initiale à 2 pixels du bord gauche

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        bg_color = QColor(150, 150, 150)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 15, 15)
        # Circle
        circle_color = QColor(10, 50, 80) if not self._checked else QColor(255, 150, 10)
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(self.offset, 2, 26, 26)
        painter.setPen(QPen(QColor(20, 20, 20), 1))  # Couleur noire, épaisseur 2 pixels
        painter.drawEllipse(self.offset, 2, 26, 26)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.offset = 32 if self._checked else 2  # 32 = 60 - 26 - 2 (pour symétrie)
        self.animation.setStartValue(self.offset)
        self.animation.setEndValue(32 if self._checked else 2)
        self.animation.start()
        self.toggled.emit(self._checked)
        self.update()

class SwitchWidget(QWidget):
    toggled = pyqtSignal(str)

    def __init__(self, left='', right='', parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addStretch()
        self.label_left = QLabel(left, self)
        self.label_left.setFixedWidth(50)
        self.label_left.setStyleSheet(styleH2)
        layout.addWidget(self.label_left)
        self.switch_button = Switch()
        layout.addWidget(self.switch_button)
        self.label_right = QLabel(right, self)
        self.label_right.setFixedWidth(50)
        self.label_right.setStyleSheet(styleH2)
        layout.addWidget(self.label_right)
        layout.addStretch()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Switch Personnalisé")
        self.setGeometry(100, 100, 300, 200)

        self.switch = SwitchWidget('Test 1', 'Test 2')
        self.switch.toggled.connect(self.on_toggle)

        layout = QVBoxLayout()
        layout.addWidget(self.switch)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_toggle(self, checked):
        print(f"Switch est {'activé' if checked else 'désactivé'}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()