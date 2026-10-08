# -*- coding: utf-8 -*-
"""
.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys
from lensepy import translate
from lensepy.css import *
from lensepy_app.widgets import Wavefront2D, Wavefront3D, ViewLink
from lensepy_app.widgets.objects import *
from lensepy_app.widgets.objects import *
from lensepy_app.appli._app.main_view import get_disp_mode
from PyQt6.QtWidgets import (
    QDialog, QLabel, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QVBoxLayout, QGridLayout,
    QApplication,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QSlider
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent, QFont


class Surface2D3DView(QWidget):
    def __init__(self, title, parent=None, colormap='plasma'):
        super().__init__(None)
        self.parent = parent # controller
        self.title = title
        self.general_display_mode = get_disp_mode(self.parent)
        self.surface = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.left_view = Wavefront2D(
            translate('unwrapped_2D_surface'), colormap=colormap)
        self.right_view = Wavefront3D(translate('unwrapped_3D_surface'))

        layout.addWidget(self.left_view, 1)
        layout.addWidget(self.right_view, 1)
        self.viewlink = ViewLink(self.left_view, self.right_view)
        self.viewlink.set_enabled(True)

    def set_surface(self, surface):
        self.surface = surface
        self.left_view.set_data(surface)
        self.right_view.set_data(surface)
        '''
        w2d.set_data(W, masque, X, Y)
        w3d.set_data(W, masque, X, Y)
        '''





def main():
    import numpy as np
    SIZE = 500
    # Grille spatiale
    x = np.linspace(-5, 5, SIZE)
    y = np.linspace(-5, 5, SIZE)
    X, Y = np.meshgrid(x, y)

    # Distance radiale
    R = np.sqrt(X ** 2 + Y ** 2)

    # Paramètres du front d'onde
    lambda_ = 4  # longueur d'onde
    k = 2 * np.pi / lambda_

    # Surface représentant le front d'onde
    Z = np.sin(k * R)

    app = QApplication(sys.argv)
    window = Surface2D3DView()
    window.set_surface(Z)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()