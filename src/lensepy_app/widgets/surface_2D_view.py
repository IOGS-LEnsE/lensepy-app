# -*- coding: utf-8 -*-
"""*surface_2D_view.py* file.

./views/surface_2D_view.py contains Surface2DView class to display a 2D surface.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import numpy as np
from typing import Tuple
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene,
    QHBoxLayout,
)
from PyQt6.QtGui import QPen, QColor, QFont
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph import ColorMap
from matplotlib import colormaps as cm

pg.setConfigOptions(imageAxisOrder='row-major')

class ColoredAxis(pg.AxisItem):
    def __init__(self, orientation, **kwargs):
        super().__init__(orientation, **kwargs)
        self.font_color = 'red'
        self.font_size = 12

    def tickStrings(self, values, scale, spacing):
        return [f'<span style="color:{self.font_color}; font-size:{self.font_size}pt">{v:g}</span>' for v in values]


class Surface2DView(QWidget):
    """
    Class Surface 2D allowing to display a 2D array in a widget.
    """

    def __init__(self, title: str='', colormap_2D='cividis'):
        """
        Default constructor.
        :param title: Title of the image to display.
        :param colormap_2D: Colormap to use in the 2D display
        """
        super().__init__()
        # Data
        self.array_2D = np.random.rand(20, 20)
        self.title = title
        self.z_axis_label = ''
        self.colormap_2D = colormap_2D
        # Graphic area for image
        self.imv = pg.ImageItem(image=self.array_2D)
        # Création du layout principal
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.plot = pg.PlotWidget()
        self.plot.setBackground('lightgray')
        self.color_bar = None
        layout.addWidget(self.plot)
        self.plot.setTitle(self.title, color="b", size="14pt")

    def set_title(self, title:str):
        self.title = title
        self.plot.setTitle(self.title, color="b", size="14pt")

    def set_array(self, array: np.ndarray):
        """
        Set an array to the surface viewer.
        :param array: Array to display.
        """
        self.array_2D = array
        # Create an ImageItem for the new image
        self.imv = pg.ImageItem(image=self.array_2D)

        # Add the image to the plot
        self.plot.addItem(self.imv)
        self.plot.setAspectLocked(True)
        pen = QPen(QColor('black'))
        pg_cmap = pg.colormap.getFromMatplotlib(self.colormap_2D)
        self.color_bar = self.plot.addColorBar(self.imv, colorMap=pg_cmap, interactive=False, pen=pen)
        self.imv.setColorMap(pg_cmap)
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.hideButtons()
        self.plot.showAxes(True)
        self.plot.invertY(True)

        axis = self.color_bar.axis
        font = QFont("Arial", 14)
        axis.setTickFont(font)


    def set_z_axis_label(self, label: str):
        """
        Set a text to display Z axis values.
        :param label: Text to display.
        :return:
        """
        self.z_axis_label = label
        text_item = pg.TextItem(self.z_axis_label, color="b", anchor=(0, 0))
        text_item.setPos(self.array_2D.shape[1]+70, 10)
        text_item.setRotation(90)
        self.plot.addItem(text_item)

    def set_z_range(self, range_z: Tuple[float]):
        """
        Set the range of the Z-axis, for the colorbar.
        :param range_z: tuple of float, minimum and maximum values of the colorbar.
        """
        self.imv.setLevels(range_z)
        self.color_bar.setLevels(range_z)

    def reset_z_range(self):
        """
        Reset the range of the Z-axis and the colorbar to the value of the image.
        """
        range_z = (np.nanmin(self.array_2D), np.nanmax(self.array_2D))
        self.imv.setLevels(range_z)
        self.color_bar.setLevels(range_z)

    def get_z_range(self) -> Tuple[float]:
        """
        Get the range of the colorbar.
        :return: minimum and maximum values of the colorbar.
        """
        min_val, max_val = self.imv.levels
        return min_val, max_val

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Surface2DView()
    array_2D = np.random.rand(50, 50)
    window.set_array(array_2D)
    window.show()
    sys.exit(app.exec())
