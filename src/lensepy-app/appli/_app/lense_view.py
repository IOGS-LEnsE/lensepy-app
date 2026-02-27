from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout


class LEnsEView(QWidget):
    """
    Main window of the application.

    Args:
        QWidget (class): QWidget can contain several graphical objects.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Layout top (gauche + droite)
        top_layout = QHBoxLayout()
        top_layout.addWidget(top_left)
        top_layout.addWidget(top_right)

        # Layout bottom (gauche + droite)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(bot_left)
        bottom_layout.addWidget(bot_right)

        # Layout principal de la partie droite
        self.layout = QVBoxLayout()
        self.layout.addLayout(top_layout, 1)
        self.layout.addLayout(bottom_layout, 1)

        self.lense_label = QLabel('Lense')
