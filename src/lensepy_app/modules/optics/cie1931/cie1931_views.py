import sys
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.modules.optics.cie1931.cie1931_model import PointCIE

from lensepy import translate
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication,
    QHBoxLayout, QPushButton, QScrollArea,
    QLineEdit, QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QTableWidget, QHeaderView,
    QTableWidgetItem)
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import colour
import numpy as np

def complementary_colour(x, y, Y=1.0):
    # xy → XYZ
    XYZ = colour.xy_to_XYZ([x, y]) * Y
    # XYZ → sRGB
    RGB = colour.XYZ_to_sRGB(XYZ)
    RGB = np.clip(RGB, 0, 1)
    return 1 - RGB

class AddPointDialog(QDialog):
    """Dialog box to enter a new point (name, x, y)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un point")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du point")

        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(0, 1)
        self.x_spin.setSingleStep(0.1)
        self.x_spin.setDecimals(2)

        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(0, 1)
        self.y_spin.setSingleStep(0.1)
        self.y_spin.setDecimals(2)

        layout.addRow(translate("name_cie_point_add"), self.name_edit)
        layout.addRow(translate("x_cie_point_add"), self.x_spin)
        layout.addRow(translate("y_cie_point_add"), self.y_spin)

        # Buttons OK / Annuler
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def validate_and_accept(self):
        """Validation of the coordinates."""
        name = self.name_edit.text().strip()
        x = self.x_spin.value()
        y = self.y_spin.value()
        # Name checking
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du point ne peut pas être vide.")
            return
        # x,y range checking
        if x > 1.0 or y > 1.0 or x < 0.0 or y < 0.0:
            QMessageBox.warning(self, "Erreur", "Les coordonnées doivent être comprises entre -1000 et 1000.")
            return
        self.accept()

    def get_values(self):
        return self.name_edit.text().strip(), self.x_spin.value(), self.y_spin.value()


class CoordinateTableWidget(QWidget):
    """Table to manage and display CIE x,y points."""

    point_added = pyqtSignal(PointCIE)
    point_deleted = pyqtSignal(PointCIE)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        # Table (4 cols : name, x, y, del)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([translate("name_cie_point"), "x", "y", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(3, 50)    # Delete button column
        #self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # CSS Style for header
        self.table.setStyleSheet("""
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
            }
        """)

        main_layout.addWidget(self.table)

        # --- Boutons globaux ---
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(translate('add_cie_point'))
        self.clear_button = QPushButton(translate('delete_all_cie_points'))

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Connexions
        self.add_button.clicked.connect(self.open_add_dialog)
        self.clear_button.clicked.connect(self.clear_all)

    # --- Logique principale ---
    def open_add_dialog(self):
        """Ouvre la boîte de dialogue pour ajouter un point."""
        dialog = AddPointDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, x, y = dialog.get_values()
            self.add_point(name, x, y)
            point = PointCIE(x, y, name)
            self.point_added.emit(point)

    def add_point(self, name, x, y):
        """Add a validated point in the table."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        for col, value in enumerate([name, f"{x:.3f}", f"{y:.3f}"]):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row_position, col, item)

        # Delete button
        btn = QPushButton(translate('delete_point'))
        btn.clicked.connect(lambda _, r=row_position: self.remove_row(r))
        self.table.setCellWidget(row_position, 3, btn)

    def remove_row(self, row_index):
        """Delete one point (row)."""
        name = self.table.item(row_index, 0).text()
        x = float(self.table.item(row_index, 1).text())
        y = float(self.table.item(row_index, 2).text())
        self.table.removeRow(row_index)
        self._refresh_delete_buttons()
        point = PointCIE(x, y, name)
        self.point_deleted.emit(point)

    def clear_all(self):
        """Clear all the points."""
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            x = float(self.table.item(row, 1).text())
            y = float(self.table.item(row, 2).text())
            point = PointCIE(x, y, name)
            self.point_deleted.emit(point)
        self.table.setRowCount(0)

    def _refresh_delete_buttons(self):
        """Réassocie les callbacks après suppression."""
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 3)
            if isinstance(widget, QPushButton):
                widget.clicked.disconnect()
                widget.clicked.connect(lambda _, r=row: self.remove_row(r))

    def get_all_data(self):
        """Get the list of points (dict)."""
        data = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            x = float(self.table.item(row, 1).text())
            y = float(self.table.item(row, 2).text())
            data.append({"name": name, "x": x, "y": y})
        return data

marker_list = ['x', '+', 'p', '8', '1']

class CIE1931MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points_list = {}
        # Initialisation du graphique une seule fois
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.update_chart()

    def update_list(self, p_list: dict):
        """Update the list of points."""
        self.points_list = p_list
        self.update_chart()

    def update_chart(self):
        # Efface le contenu précédent
        self.ax.clear()

        # Redessine le diagramme
        colour.plotting.plot_chromaticity_diagram_CIE1931(
            show=False, axes=self.ax,
            show_diagram_colours=True,
            show_spectral_locus=True,
            show_colourspace_diagram=False
        )

        # Ajoute les nouveaux points
        self.ax.plot(0.33, 0.33, 'kD', label="D65")
        marker_nb = 0
        for key in self.points_list:
            x, y = self.points_list[key].get_coords()
            name = self.points_list[key].get_name()
            # To display in a complementary color
            RGB = complementary_colour(x, y)
            self.ax.plot(x, y, marker=marker_list[marker_nb%len(marker_list)],
                         color=RGB, label=name, linestyle='None')
            marker_nb += 1

        # Réglages et redraw
        self.ax.legend(loc="upper right")
        self.ax.set_xlim(-0.1, 0.8)
        self.ax.set_ylim(-0.1, 0.9)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CIE1931MatplotlibWidget()
    win.setWindowTitle("Diagramme CIE 1931")
    win.resize(800, 700)
    win.show()
    sys.exit(app.exec())
