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


class Surface2D3DView(QWidget):
    def __init__(self, title, parent=None, colormap='plasma'):
        super().__init__(None)
        self.parent = parent # controller
        self.title = title
        self.general_display_mode, self.general_theme = get_disp_mode(self.parent)
        self.surface = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.left_view = Wavefront2D(translate('unwrapped_2D_surface'),
                                     parent=self.parent, colormap=colormap)
        self.right_view = Wavefront3D(translate('unwrapped_3D_surface'),
                                      parent=self.parent,
                                      disp_cmap=False, colormap=colormap)

        layout.addWidget(self.left_view, 1)
        layout.addWidget(self.right_view, 1)
        self.viewlink = ViewLink(self.left_view, self.right_view)
        self.viewlink.set_enabled(True)

    def set_surface(self, surface, mask=None):
        self.surface = surface
        if mask is not None:
            self.mask = mask
            self.left_view.set_data(surface, mask)
            self.right_view.set_data(surface, mask)
        else:
            self.mask = None
            self.left_view.set_data(surface)
            self.right_view.set_data(surface)


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

    ### REAL DATA
    from lensepy.optics.zygo import DataSet, PhaseModel
    from matplotlib import pyplot as plt
    nb_of_images_per_set = 5
    file_path = '../../../../../../../lensepy-data/optics/zygo/test3.mat'
    data_set = DataSet()
    data_set.load_images_set_from_file(file_path)
    data_set.load_masks_from_file(file_path)

    phase_test = PhaseModel(data_set)

    ## Test class
    phase_test.prepare_data()

    if phase_test.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = phase_test.get_wrapped_phase()
    if phase_test.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = phase_test.get_unwrapped_phase()
    mask = phase_test.get_mask()

    app = QApplication(sys.argv)
    window = Surface2D3DView('Test')
    window.set_surface(unwrapped, mask)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()