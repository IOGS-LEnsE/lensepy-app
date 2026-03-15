import sys
from lensepy import translate
from lensepy.css import *
from matplotlib.lines import Line2D
from numpy.matlib import empty

from lensepy_app.modules.optics.cie1931.cie1931_model import PointCIE

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication,
    QHBoxLayout, QPushButton, QScrollArea,
    QLineEdit, QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QTableWidget, QHeaderView,
    QTableWidgetItem)
import matplotlib

#from lensepy_app.modules.optics.gammutCIE import GammutCIEController

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import colour
import numpy as np
from lensepy_app.modules.optics.cie1931.cie1931_views import CIE1931MatplotlibWidget
from lensepy_app.modules.optics.gamutCIE.gamutCIE_model import TriangleGammut

def complementary_colour(x, y, Y=1.0):
    # xy → XYZ
    XYZ = colour.xy_to_XYZ([x, y]) * Y
    # XYZ → sRGB
    RGB = colour.XYZ_to_sRGB(XYZ)
    RGB = np.clip(RGB, 0, 1)
    return 1 - RGB

class AddGamutDialog(QDialog):
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


class GamutTableWidget(QWidget):
    """Table to manage and display screen gammut (3 CIE points)."""

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
        dialog = AddGamutDialog(self)
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

    def open_add_dialog_with_coords(self, x, y):
        dialog = AddGamutDialog(self)
        dialog.x_spin.setValue(x)
        dialog.y_spin.setValue(y)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, x, y = dialog.get_values()
            self.add_point(name, x, y)
            point = PointCIE(x, y, name)
            self.point_added.emit(point)

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
colors = ["red", "blue", "green", "purple"]
styles = ["-", "--", "-.", ":"]

sRGB_triangle = TriangleGammut('sRGB')
sRGB_triangle.add_point(PointCIE(0.64, 0.33, 'R'))
sRGB_triangle.add_point(PointCIE(0.30, 0.60, 'G'))
sRGB_triangle.add_point(PointCIE(0.15, 0.06, 'B'))

rec_2020_triangle = TriangleGammut('rec2020')
rec_2020_triangle.add_point(PointCIE(0.708, 0.292, 'R'))
rec_2020_triangle.add_point(PointCIE(0.170, 0.797, 'G'))
rec_2020_triangle.add_point(PointCIE(0.131, 0.046, 'B'))

class GamutCIEMatplotlibWidget(CIE1931MatplotlibWidget):

    point_clicked = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.triangles = []
        self.legend_handles = []
        self.update_chart()

    def add_triangle(self, triangle: TriangleGammut):
        """Add a triangle to the table."""
        if triangle.is_complete():
            self.triangles.append(triangle)
            return True
        return False

    def _sRGB_display(self):
        """Display the sRGB triangle."""
        style = '--'
        disp_sRGB_triangle = Polygon(
                sRGB_triangle.get_points(),
                closed=True,
                fill=False,
                edgecolor='black',
                linestyle=style,
                linewidth=1,
                label='sRGB'
            )
        self.ax.add_patch(disp_sRGB_triangle)

        self.legend_handles.append(
            Line2D(
                [0], [0],
                color='black',
                linestyle=style,
                linewidth=1,
                label='sRGB'
            )
        )

    def _rec2020_display(self):
        style = ':'
        disp_rec2020_triangle = Polygon(
                rec_2020_triangle.get_points(),
                closed=True,
                fill=False,
                edgecolor='black',
                linestyle=style,
                linewidth=1,
                label='Rec.2020'
            )
        self.ax.add_patch(disp_rec2020_triangle)
        self.legend_handles.append(
            Line2D(
                [0], [0],
                color='black',
                linestyle=style,
                linewidth=1,
                label='Rec.2020'
            )
        )

    def update_chart(self):
        super().update_chart()
        self.legend_handles.clear()
        self._sRGB_display()
        self._rec2020_display()


        for k, triangle in enumerate(self.triangles):
            points = triangle.get_points()
            name = triangle.name
            color = colors[k % len(colors)]
            style = styles[k % len(styles)]
            disp_triangle = Polygon(
                points,
                closed=True,
                fill=False,
                edgecolor='red',
                linewidth=2,
                label=name
            )

            self.legend_handles.append(
                Line2D(
                    [0], [0],
                    color=color,
                    linestyle=style,
                    linewidth=2,
                    label=name
                )
            )

            self.ax.add_patch(disp_triangle)

        self.ax.legend(handles=self.legend_handles, loc="upper right")

        # redraw
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GammutCIEMatplotlibWidget()

    triangle = TriangleGammut('Ecran 1')

    print(f'Is OK ? {triangle.is_complete()}')
    p1 = PointCIE(0.1, 0.6, 'A')
    triangle.add_point(p1)
    p2 = PointCIE(0.4, 0.5, 'B')
    triangle.add_point(p2)
    p3 = PointCIE(0.2, 0.1, 'C')
    triangle.add_point(p3)
    print(f'Is OK ? {triangle.is_complete()}')

    win.setWindowTitle("Diagramme CIE 1931")
    win.resize(800, 700)
    win.show()

    win.add_triangle(triangle)
    win.update_chart()

    sys.exit(app.exec())
