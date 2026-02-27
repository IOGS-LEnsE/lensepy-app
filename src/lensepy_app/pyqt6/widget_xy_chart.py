# -*- coding: utf-8 -*-
"""*widget_xy_chart* file.

*widget_xy_chart* file that contains ...

.. note:: LEnsE - Institut d'Optique - version 0.3.4

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import numpy as np
import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSizeF
from pyqtgraph import PlotWidget, mkPen, mkBrush
from lensepy.css import *


class XYChartWidget(QWidget):
    """
    Widget used to display data in a 2D chart - X and Y axis.
    Children of QWidget - QWidget can be put in another widget and / or window
    ---

    Attributes
    ----------
    title : str
        title of the chart
    plot_chart_widget : PlotWidget
        pyQtGraph Widget to display chart
    plot_chart : PlotWidget.plot
        plot object of the pyQtGraph widget
    plot_x_data : Numpy array
        value to display on X axis
    plot_y_data : Numpy array
        value to display on Y axis

    Methods
    -------
    set_data(x_axis, y_axis):
        Set the X and Y axis data to display on the chart.
    refresh_chart():
        Refresh the data of the chart.
    set_title(title):
        Set the title of the chart.
    set_information(infos):
        Set informations in the informations label of the chart.
    set_background(css_color):
        Modify the background color of the widget.
    """

    def __init__(self, parent=None):
        """
        Initialisation of the time-dependent chart.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.title = ''  # Title of the chart
        self.layout = QVBoxLayout()  # Main layout of the QWidget
        self.nb_data = 0

        # Title label
        self.title_label = QLabel(self.title)
        style = "background-color: darkgray;"
        style += "font-weight:bold;"
        style += "color:white;"
        style += "font-size:20px;"
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(style)

        # Option label
        self.info_label = QLabel('')
        style = "background-color: lightgray;"
        style += "font-size:10px;"
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(style)

        self.plot_chart_widget = PlotWidget()  # pyQtGraph widget
        # Create Numpy array for X and Y data
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])
        self.x_label = ''
        self.y_label = ''

        # No data at initialization
        self.pen = [mkPen(color=BLUE_IOGS, style=Qt.PenStyle.SolidLine, width=2.5),
                    mkPen(color=ORANGE_IOGS, style=Qt.PenStyle.DashLine, width=2.5)]
        self.brush = mkBrush(ORANGE_IOGS)
        self.plot_chart = self.plot_chart_widget.plot([0], pen=self.pen[0])

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)
        self.setLayout(self.layout)

    def set_data(self, x_axis, y_axis, x_label: str = '', y_label: str = ''):
        """
        Set the X and Y axis data to display on the chart.
        :param x_axis: X-axis value to display.
        :param y_axis: Y-axis value to display.
        :param x_label: X label to display.
        :param y_label: Y label to display.
        """
        if isinstance(y_axis, list):
            self.nb_data = len(y_axis)
        else:
            self.nb_data = 1
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis
        self.x_label = x_label
        self.y_label = y_label
        self.y_name = ''
        self.x_legend = 0
        self.y_legend = 0

    def set_legend(self, y_legend, x=0, y=0):
        """Add a legend to the graph."""
        self.y_name = y_legend
        self.x_legend = x
        self.y_legend = y

    def set_y_range(self, min_val, max_val):
        """Set Y axis range."""
        self.plot_chart_widget.setYRange(min_val, max_val)

    def refresh_chart(self, last: int = 0):
        """
        Refresh the data of the chart.
        :param last: Number of samples to display (from the end).
        """

        self.plot_chart_widget.clear()
        if self.y_name != '':
            legend = self.plot_chart_widget.addLegend()
            if self.y_legend != 0 or self.x_legend !=0:
                legend.setOffset((self.x_legend, self.y_legend))

        if self.nb_data == 1:
            if last != 0:
                if len(self.plot_x_data) > last:
                    x_plot = self.plot_x_data[-last:]
                    y_plot = self.plot_y_data[-last:]
                else:
                    x_plot = self.plot_x_data
                    y_plot = self.plot_y_data
                if self.plot_x_data.shape[0] > 1:
                    if self.y_name != '':
                        self.plot_chart = self.plot_chart_widget.plot(x_plot, y_plot,
                                                                      pen=self.pen[0],
                                                                      symbol='o',
                                                                      brush=self.brush,
                                                                      name=self.y_name)
                    else:
                        self.plot_chart = self.plot_chart_widget.plot(x_plot, y_plot,
                                                                      pen=self.pen[0],
                                                                      symbol='o',
                                                                      brush=self.brush)
            else:
                if self.plot_x_data.shape[0] > 1:
                    if self.y_name != '':
                        self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                                      self.plot_y_data,
                                                                      pen=self.pen[0],
                                                                      name=self.y_name)
                    else:
                        self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                                      self.plot_y_data,
                                                                      pen=self.pen[0])
            x_axis = self.plot_chart_widget.getPlotItem().getAxis('bottom')
            x_size = len(self.plot_x_data)
            if x_size > 1:
                Te = self.plot_x_data[1] - self.plot_x_data[0]
                xTicks = [x_size / 20 * Te, x_size / 100 * Te]
                x_axis.setTickSpacing(xTicks[0], xTicks[1])
                # set x ticks (major and minor)
                self.plot_chart_widget.showGrid(x=True, y=True)
                styles = {"color": "black", "font-size": "18px"}
                if self.y_label != '':
                    self.plot_chart_widget.setLabel("left", self.y_label, **styles)
                if self.x_label != '':
                    self.plot_chart_widget.setLabel("bottom", self.x_label, **styles)

        else:
            for i in range(self.nb_data):
                if last != 0:
                    if len(self.plot_x_data) > last:
                        x_plot = self.plot_x_data[-last:]
                        y_plot = self.plot_y_data[i]
                        y_plot = y_plot[-last:]
                    else:
                        x_plot = self.plot_x_data
                        y_plot = self.plot_y_data[i]
                    if self.plot_x_data.shape[0] > 1:
                        print(x_plot.shape)
                        print(y_plot.shape)
                        if self.y_name != '':
                            self.plot_chart = self.plot_chart_widget.plot(x_plot, y_plot,
                                                                          pen=self.pen[i],
                                                                          symbol='o',
                                                                          brush=self.brush,
                                                                          name=self.y_name[i])
                        else:
                            self.plot_chart = self.plot_chart_widget.plot(x_plot, y_plot,
                                                                          pen=self.pen[i],
                                                                          symbol='o',
                                                                          brush=self.brush)

                else:
                    if self.plot_x_data.shape[0] > 1:
                        if self.y_name != '':
                            self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                                          self.plot_y_data[i],
                                                                          pen=self.pen[i],
                                                                          name=self.y_name[i])
                        else:
                            self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                                          self.plot_y_data[i],
                                                                          pen=self.pen[i])

            x_axis = self.plot_chart_widget.getPlotItem().getAxis('bottom')
            x_size = len(self.plot_x_data)
            if x_size > 1:
                Te = self.plot_x_data[1] - self.plot_x_data[0]
                xTicks = [x_size / 10 * Te, x_size / 50 * Te]
                x_axis.setTickSpacing(xTicks[0], xTicks[1])
                # set x ticks (major and minor)
                self.plot_chart_widget.showGrid(x=True, y=True)
                styles = {"color": "black", "font-size": "18px"}
                if self.y_label != '':
                    self.plot_chart_widget.setLabel("left", self.y_label, **styles)
                if self.x_label != '':
                    self.plot_chart_widget.setLabel("bottom", self.x_label, **styles)

        if self.y_name != '':
            for sample, label in legend.items:
                text = label.text
                label.setText(f'<span style="color:black; font-size:12pt;">{text}</span>')

    def update_infos(self, value: bool = True):
        """
        Update mean and standard deviation data and display.

        :param value: True to display mean and standard deviation.
            False to display "acquisition in progress".
        """
        if value:
            mean_d = round(np.mean(self.plot_y_data), 2)
            stdev_d = round(np.std(self.plot_y_data), 2)
            self.set_information(f'Mean = {mean_d} / Standard Dev = {stdev_d}')
        else:
            self.set_information('Data Acquisition In Progress')

    def set_title(self, title: str):
        """
        Set the title of the chart.

        :param title: Title of the chart.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str):
        """
        Set informations in the informations label of the chart.
        (bottom)

        :param infos: Informations to display.
        """
        self.info_label.setText(infos)

    def set_background(self, css_color: str):
        """
        Modify the background color of the widget.

        :param css_color: Color in CSS style.
        """
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the main chart of the widget.
        """
        self.plot_chart_widget.clear()

    def display_last(self, number: int = 50):
        """Display the N last points.
        :param number: Number of points to display.
        """
        self.refresh_chart(last=number)


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XY Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = XYChartWidget()
        self.chart_widget.set_title('My Super Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(0, 100, 101)
        y = [np.random.randint(0, 100, 101, dtype=np.int8),
             np.random.randint(0, 20, 101, dtype=np.int8)]

        self.chart_widget.set_background('white')

        self.chart_widget.set_data(x, y)
        y_name = ['Test 1', 'Test 2 - very long long long']
        self.chart_widget.set_legend(y_name, 100, 20)
        self.chart_widget.refresh_chart()
        #self.chart_widget.display_last(50)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
