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


class CircleWidget(QWidget):
    def __init__(self, color=QColor("red"), diameter=100):
        """Create a widget that displays a circle."""
        super().__init__()
        self.color = color
        self.diameter = diameter
        self.setMinimumSize(diameter, diameter)

    def paintEvent(self, event):
        """Draw the circle in the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Color
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        # Process circle coordinates
        w = self.width()
        h = self.height()
        x = (w - self.diameter) / 2
        y = (h - self.diameter) / 2
        # Draw the circle
        circle_rect = QRectF(int(x), int(y), self.diameter, self.diameter)
        painter.drawEllipse(circle_rect)


class RGBLedControlWidget(QWidget):
    """
    Widget to display image opening options.
    """

    rgb_changed = pyqtSignal()
    arduino_connected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()
        # Graphical Elements
        layout.addWidget(make_hline())

        label = QLabel(translate('led_control_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Connection to Arduino
        layout.addWidget(make_hline())
        label_boards = QLabel(translate('led_control_boards'))
        label_boards.setStyleSheet(styleH3)
        label_boards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_boards)
        self.boards_list = QComboBox()
        layout.addWidget(self.boards_list)
        self.board_connect_button = QPushButton(translate('arduino_connect'))
        self.board_connect_button.setStyleSheet(unactived_button)
        self.board_connect_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.board_connect_button)
        self.board_connect_button.clicked.connect(self.handle_arduino_connected)

        layout.addWidget(make_hline())

        label_rgb = QLabel(translate('R_G_B_values'))
        label_rgb.setStyleSheet(styleH3)
        label_rgb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_rgb)

        # Sliders for RGB
        rgb_widget = QWidget()
        rgb_layout = QHBoxLayout()
        rgb_layout.addWidget(make_hline())
        ## Red
        r_widget = QWidget()
        r_layout = QVBoxLayout()
        r_widget.setLayout(r_layout)
        r_circle = CircleWidget(color=QColor(255, 0, 0), diameter=30)
        r_layout.addWidget(r_circle)
        self.r_color = SliderBlocVertical('R', '', 0, 255, integer=True)
        r_layout.addWidget(self.r_color)
        ## Green
        g_widget = QWidget()
        g_layout = QVBoxLayout()
        g_widget.setLayout(g_layout)
        g_circle = CircleWidget(color=QColor(0, 150, 0), diameter=30)
        g_layout.addWidget(g_circle)
        self.g_color = SliderBlocVertical('G', '', 0, 255, integer=True)
        g_layout.addWidget(self.g_color)
        ## Blue
        b_widget = QWidget()
        b_layout = QVBoxLayout()
        b_widget.setLayout(b_layout)
        b_circle = CircleWidget(color=QColor(0, 0, 255), diameter=30)
        b_layout.addWidget(b_circle)
        self.b_color = SliderBlocVertical('B', '', 0, 255, integer=True)
        b_layout.addWidget(self.b_color)

        ## White 1
        w1_widget = QWidget()
        w1_layout = QVBoxLayout()
        w1_widget.setLayout(w1_layout)
        w1_circle = CircleWidget(color=QColor(120, 200, 150), diameter=30)
        w1_layout.addWidget(w1_circle)
        self.w1_color = SliderBlocVertical('W1', '', 0, 255, integer=True)
        w1_layout.addWidget(self.w1_color)
        ## White 2
        w2_widget = QWidget()
        w2_layout = QVBoxLayout()
        w2_widget.setLayout(w2_layout)
        w2_circle = CircleWidget(color=QColor(120, 200, 20), diameter=30)
        w2_layout.addWidget(w2_circle)
        self.w2_color = SliderBlocVertical('W2', '', 0, 255, integer=True)
        w2_layout.addWidget(self.w2_color)

        self.r_color.set_enabled(False)
        self.g_color.set_enabled(False)
        self.b_color.set_enabled(False)
        self.w1_color.set_enabled(False)
        self.w2_color.set_enabled(False)
        rgb_layout.addWidget(r_widget)
        rgb_layout.addWidget(g_widget)
        rgb_layout.addWidget(b_widget)
        rgb_layout.addWidget(make_vline())
        rgb_layout.addWidget(w1_widget)
        rgb_layout.addWidget(w2_widget)
        layout.addLayout(rgb_layout)
        # Erase all
        self.erase_button = QPushButton(translate('erase_button'))
        self.erase_button.setStyleSheet(disabled_button)
        self.erase_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.erase_button.clicked.connect(self.handle_erase_all)
        layout.addWidget(self.erase_button)
        self.erase_button.setEnabled(False)

        layout.addStretch()
        self.setLayout(layout)
        # Init boards and lists
        self.boards = self.parent.wrapper.find_arduino_ports()
        if self.boards:
            self.boards_list.addItems(self.boards)
        else:
            self.board_connect_button.setEnabled(False)
            self.board_connect_button.setText(translate('no_boards'))
            self.board_connect_button.setStyleSheet(disabled_button)

        # Signals
        self.r_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.g_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.b_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.w1_color.slider_changed.connect(lambda: self.rgb_changed.emit())
        self.w2_color.slider_changed.connect(lambda: self.rgb_changed.emit())

    def get_rgb(self):
        """Return the current RGB colors."""
        r = int(self.r_color.get_value())
        g = int(self.g_color.get_value())
        b = int(self.b_color.get_value())
        return (r, g, b)

    def get_w12(self):
        """Return the current W1 and W2 colors."""
        w1 = int(self.w1_color.get_value())
        w2 = int(self.w2_color.get_value())
        return (w1, w2)

    def handle_arduino_connected(self):
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(disabled_button)
        self.erase_button.setStyleSheet(unactived_button)
        self.r_color.set_enabled(True)
        self.g_color.set_enabled(True)
        self.b_color.set_enabled(True)
        self.w1_color.set_enabled(True)
        self.w2_color.set_enabled(True)
        self.erase_button.setEnabled(True)
        com = self.boards_list.currentText()
        self.arduino_connected.emit(com)

    def handle_erase_all(self):
        self.erase_button.setStyleSheet(actived_button)
        self.repaint()
        self.r_color.set_value(0)
        self.g_color.set_value(0)
        self.b_color.set_value(0)
        self.w1_color.set_value(0)
        self.w2_color.set_value(0)
        self.rgb_changed.emit()
        time.sleep(0.3)
        self.erase_button.setStyleSheet(unactived_button)
        self.repaint()


class MatrixWidget(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(make_hline())
        label = QLabel(translate('rgb_matrix_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        # 3x3 Matrix
        self.matrix = QTableWidget(3, 3)
        self.matrix.setHorizontalHeaderLabels(["R", "G", "B"])
        self.matrix.setVerticalHeaderLabels(["X", "Y", "Z"])
        self.matrix.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix.itemChanged.connect(self.on_matrix_changed)
        self.matrix.clearSelection()

        # CSS Style for header
        self.matrix.setStyleSheet("""
            QHeaderView::section {
                background-color: #0A3250;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 3px;
                border: 2px solid white;
            }            
            QHeaderView::item {
                padding: 0px;
                color: #0A3250;
                text-align: center;
            }
        """)

        matrix_layout = QHBoxLayout()
        matrix_layout.addStretch()  # espace à gauche
        matrix_layout.addWidget(self.matrix)  # la matrice au centre
        matrix_layout.addStretch()  # espace à droite
        layout.addLayout(matrix_layout)

        # --- Zone 2 : cachée au début ---
        self.extra_group = QGroupBox("Données supplémentaires")
        self.extra_layout = QFormLayout()

        self.valeur_max = QLineEdit()
        self.valeur_max.textChanged.connect(self.check_inputs)

        self.x_edit = QLineEdit()
        self.y_edit = QLineEdit()
        self.z_edit = QLineEdit()
        for edit in (self.x_edit, self.y_edit, self.z_edit):
            edit.textChanged.connect(self.check_inputs)

        self.calc_btn = QPushButton(translate("process_rgb_matrix"))
        self.calc_btn.setEnabled(False)
        self.calc_btn.clicked.connect(self.process_rgb)

        self.result_label = QLabel("R, G, B : - , - , -")

        self.extra_layout.addRow("Valeur max :", self.valeur_max)

        xyz_layout = QHBoxLayout()
        xyz_layout.addWidget(QLabel("x:"))
        xyz_layout.addWidget(self.x_edit)
        xyz_layout.addWidget(QLabel("Y:"))
        xyz_layout.addWidget(self.y_edit)
        xyz_layout.addWidget(QLabel("Z:"))
        xyz_layout.addWidget(self.z_edit)
        self.extra_layout.addRow("Coordonnées :", xyz_layout)

        self.extra_layout.addRow(self.calc_btn)
        self.extra_layout.addRow(self.result_label)
        self.extra_group.setLayout(self.extra_layout)
        self.extra_group.setEnabled(False)

        layout.addWidget(self.extra_group)
        layout.addStretch()

    def on_matrix_changed(self, item: QTableWidgetItem):
        """Met à jour la couleur et vérifie si tout est rempli."""
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        text = item.text().strip()
        if text:
            item.setBackground(QColor("#c4f0c2"))  # vert pâle
        else:
            item.setBackground(QColor("white"))

        if self.is_matrix_filled():
            self.extra_group.setEnabled(True)
        self.matrix.clearSelection()

    def is_matrix_filled(self):
        """Vérifie si toutes les cases sont remplies."""
        for row in range(3):
            for col in range(3):
                item = self.matrix.item(row, col)
                if not item or not item.text().strip():
                    return False
        return True

    def check_inputs(self):
        """Active le bouton calcul si tout est rempli."""
        if (
            self.valeur_max.text().strip()
            and self.x_edit.text().strip()
            and self.y_edit.text().strip()
            and self.z_edit.text().strip()
        ):
            self.calc_btn.setEnabled(True)
        else:
            self.calc_btn.setEnabled(False)

    def process_rgb(self):
        """Exemple de calcul arbitraire de RGB."""
        try:
            vmax = float(self.valeur_max.text())
            x = float(self.x_edit.text())
            y = float(self.y_edit.text())
            z = float(self.z_edit.text())

            x_red = float(self.matrix.item(0, 0).text())
            x_green = float(self.matrix.item(0, 1).text())
            x_blue = float(self.matrix.item(0, 2).text())
            y_red = float(self.matrix.item(1, 0).text())
            y_green = float(self.matrix.item(1, 1).text())
            y_blue = float(self.matrix.item(1, 2).text())
            z_red = float(self.matrix.item(2, 0).text())
            z_green = float(self.matrix.item(2, 1).text())
            z_blue = float(self.matrix.item(2, 2).text())
            mat_led = np.array([[x_red, x_green, x_blue],[y_red, y_green, y_blue],
                                [z_red, z_green, z_blue]])
            mat_led_inv = np.linalg.inv(mat_led)

        except ValueError:
            self.result_label.setText("Erreur : valeurs non numériques")
            return

        # Exemple simple : normalisation
        [r, g, b] = np.dot(mat_led_inv, np.array([x, y, z]))

        self.result_label.setText(f"R, G, B : {r}, {g}, {b}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MatrixWidget()
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

