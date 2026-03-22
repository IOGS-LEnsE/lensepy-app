# -*- coding: utf-8 -*-
"""*bar_graph_view.py* file.

./views/bar_graph_view.py contains BarGraphView class to display a bar graph.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QCheckBox,
    QHBoxLayout, QVBoxLayout
)
import pyqtgraph as pg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.aberrations_controller import AberrationsController


class BarGraphView(QWidget):
    """BarGraph View."""

    def __init__(self) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Pyqtgraph
        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        # Data
        self.x = np.array([1, 2, 3, 4, 5])
        self.y = np.array([3, -2, 5, -4, 2])
        self.colors_x = None

        self.plotWidget.setBackground('white')
        self.setStyleSheet("background:" + BLUE_IOGS + ";")

        # Horizontal Axis
        self.plotWidget.setYRange(min(self.y) - 1, max(self.y) + 1)
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.getAxis('left').setStyle(tickLength=-5)
        # Horizontal Line
        zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('k', width=2))
        self.plotWidget.addItem(zero_line)
        self.x_axis_label = "X Axis"
        self.y_axis_label = "Y Axis"
        # Labels
        self.plotWidget.setLabel('bottom', self.x_axis_label)
        self.plotWidget.setLabel('left', self.y_axis_label)

        self.update_graph()

    def set_labels(self, x_axis: str = None, y_axis: str = None):
        """
        Set the labels of the axis.
        :param x_axis: X-Axis label.
        :param y_axis: Y-Axis label.
        """
        self.x_axis_label = x_axis
        self.y_axis_label = y_axis
        self.plotWidget.setLabel('bottom', self.x_axis_label)
        self.plotWidget.setLabel('left', self.y_axis_label)

    def set_data(self, x, y, color_x = None):
        """
        Set data to the bar graph.
        :param x: X-Axis data.
        :param y: Y-Axis data.
        :param color_x: List of colors of the bar.
        """
        self.x = x
        self.y = y
        self.colors_x = color_x
        self.update_graph()

    def update_graph(self):
        """
        Update graphics display.
        """
        self.plotWidget.clear()
        if self.colors_x is not None:
            brushes = [pg.mkBrush(color) for color in self.colors_x]
            for i in range(len(self.x)):
                bar = pg.BarGraphItem(x=[self.x[i]], height=[self.y[i]], width=0.6, brush=brushes[i])
                self.plotWidget.addItem(bar)
        else:
            bar = pg.BarGraphItem(x=self.x, height=self.y, width=0.6)
            self.plotWidget.addItem(bar)
        self.plotWidget.getPlotItem().enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    '''
    from controllers.analyses_controller import AnalysesController, ModesManager
    manager = ModesManager()
    controller = AnalysesController()
    '''

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    main_widget = BarGraphView()
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    # colors = ['red', 'green', 'blue', 'orange', 'purple']

    sys.exit(app.exec())