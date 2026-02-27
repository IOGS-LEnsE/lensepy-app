# -*- coding: utf-8 -*-
"""*widget_histogram* file.

*widget_histogram* file that contains ...

.. note:: LEnsE - Institut d'Optique - version 0.2.7

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, BarGraphItem, InfiniteLine
from lensepy.css import *


class RGBWidget(QWidget):
    """
    RGC Checkbox widget and display RGB means.
    """
    def __init__(self, parent = None) -> None:
        """Initialize the RGB checkbox widget.
        :param parent: QWidget or QMainWindow parent.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QHBoxLayout() # Main layout of the QWidget

        self.checked_R = True
        self.checked_G = True
        self.checked_B = True

        # Check for RGB images
        self.check_RGB_widget = QWidget()
        self.check_RGB_layout = QHBoxLayout()
        self.check_RGB_widget.setLayout(self.check_RGB_layout)
        self.check_R_box = QCheckBox('R')
        self.label_R_mean_std = QLabel()
        self.label_R_mean_std.setMinimumWidth(100)
        self.check_G_box = QCheckBox('G')
        self.label_G_mean_std = QLabel()
        self.label_G_mean_std.setMinimumWidth(100)
        self.check_B_box = QCheckBox('B')
        self.label_B_mean_std = QLabel()
        self.label_B_mean_std.setMinimumWidth(100)
        self.check_R_box.setChecked(True)
        self.check_G_box.setChecked(True)
        self.check_B_box.setChecked(True)
        self.check_R_box.stateChanged.connect(self.update_check_RGB)
        self.check_G_box.stateChanged.connect(self.update_check_RGB)
        self.check_B_box.stateChanged.connect(self.update_check_RGB)
        self.layout.addWidget(self.check_R_box)
        self.layout.addWidget(self.label_R_mean_std)
        self.layout.addWidget(self.check_G_box)
        self.layout.addWidget(self.label_G_mean_std)
        self.layout.addWidget(self.check_B_box)
        self.layout.addWidget(self.label_B_mean_std)

        self.setLayout(self.layout)

    def update_check_RGB(self):
        """Action performed when a checkbox is clicked."""
        self.checked_R = self.check_R_box.isChecked()
        self.checked_G = self.check_G_box.isChecked()
        self.checked_B = self.check_B_box.isChecked()

    def update_infos(self, mean_R, std_R, mean_G, std_G, mean_B, std_B):
        """Update mean and standard dev of R G B image channels."""
        self.label_R_mean_std.setText(f'{mean_R} / {std_R}')
        self.label_G_mean_std.setText(f'{mean_G} / {std_G}')
        self.label_B_mean_std.setText(f'{mean_B} / {std_B}')

    def is_R_checked(self):
        return self.checked_R

    def is_G_checked(self):
        return self.checked_G

    def is_B_checked(self):
        return self.checked_B


class HistogramWidget(QWidget):
    """Create a Widget with a histogram.

    Widget used to display histogram.
    Children of QWidget - QWidget can be put in another widget and / or window

    plot_chart_widget : PlotWidget
        pyQtGraph Widget to display chart
    plot_chart : PlotWidget.plot
        plot object of the pyQtGraph widget
    plot_hist_data : Numpy array
        data to process as histogram
    plot_hist : Numpy array
        histogram of the data
    plot_bins_data : Numpy array
        bins on X axis of the chart
    line_color : CSS color
        color of the line in the graph - default #0A3250

    Methods
    -------
    set_data(data, bins=[]):
        Set the data to process before displaying on the chart, and
        optionally bins of the histogram.
    refresh_chart():
        Refresh the data of the chart.
    set_title(title):
        Set the title of the chart.
    set_information(infos):
        Set informations in the informations label of the chart.
    set_background(css_color):
        Modify the background color of the widget.
    """

    def __init__(self, name: str = '', info: bool = True) -> None:
        """Initialize the histogram widget.
        :param name: Displayed name of the histogram.
        :param info: if True, display information under the histogram.
        """
        super().__init__()
        self.name = name  # Name of the chart
        self.info = info
        self.layout = QVBoxLayout()  # Main layout of the QWidget

        # Title label
        self.title_label = QLabel(self.name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # Option label
        self.info_label = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        self.plot_chart_widget = PlotWidget()  # pyQtGraph widget
        # Create Numpy array for X and Y data
        self.plot_hist_data = np.array([])
        self.plot_bins_data = np.array([])
        self.plot_hist = np.array([])
        self.y_axis_label = ''
        self.x_axis_label = ''

        # No data at initialization
        self.plot_chart = self.plot_chart_widget.plot([0])
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        if self.info:
            self.layout.addWidget(self.info_label)

        self.check_RGB_widget = RGBWidget(self)
        self.layout.addWidget(self.check_RGB_widget)
        self.setLayout(self.layout)

        # Color of line in the graph
        self.line_color = '#0A3250'

        # Height of the y axis
        self.y_axis_height = 0

    def set_data(self, data: np.ndarray, bins: np.ndarray, log_mode: bool = False,
                 black_mode: bool = False, zoom_mode: bool = False,
                 zoom_target: int = 5) -> None:
        """Set the data and the bins to process the histogram.

        :param data: data to process histogram.
        :param bins: bins on X axis of the histogram. Must increase monotonically.
        :param log_mode: True for log value in Y-axis.
        :param black_mode: True for removing 10 first values of the histogram.
        :param zoom_mode: True to display a zoom of the histogram.
        :param zoom_target: Minimum value to reach to zoom.
        """
        self.plot_hist_data = data
        self.plot_bins_data = bins
        if len(data.shape) <= 2:
            self.set_RGB_mode(False)
            self.plot_hist, self.plot_bins_data = np.histogram(
                self.plot_hist_data,
                bins=self.plot_bins_data)
            if log_mode:
                self.plot_hist = np.log10(self.plot_hist + 1)
            if black_mode:
                self.plot_hist = self.plot_hist[10:]
                self.plot_bins_data = self.plot_bins_data[10:]
            if zoom_mode:
                # Find min index
                min_index = np.argmax(self.plot_hist > zoom_target) - 10
                if min_index < 0:
                    min_index = 0
                # Find max index
                max_index = len(self.plot_hist) - 1 - np.argmax(np.flip(self.plot_hist) > zoom_target) + 10
                if max_index > len(bins):
                    max_index = len(bins)
                self.plot_hist = self.plot_hist[min_index:max_index]
                self.plot_bins_data = self.plot_bins_data[min_index:max_index]
        else:
            self.set_RGB_mode(True)
            plot_hist_R, self.plot_bins_data = np.histogram(
                self.plot_hist_data[:, :, 0],
                bins=self.plot_bins_data)
            plot_hist_G, self.plot_bins_data = np.histogram(
                self.plot_hist_data[:, :, 1],
                bins=self.plot_bins_data)
            plot_hist_B, self.plot_bins_data = np.histogram(
                self.plot_hist_data[:, :, 2],
                bins=self.plot_bins_data)
            self.plot_hist = np.column_stack((plot_hist_R, plot_hist_G, plot_hist_B))

    def set_RGB_mode(self, value: bool):
        """Set RGB mode.
        """
        if value:
            self.check_RGB_widget.show()
        else:
            self.check_RGB_widget.hide()

    def set_axis_labels(self, x_axis_label: str = '', y_axis_label: str = ''):
        """Set the label of the axis of the histogramme."""
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label

    def refresh_chart(self) -> None:
        """Refresh the data of the chart.
        """
        self.plot_chart_widget.clear()
        bins = self.plot_bins_data[:len(self.plot_hist)]

        if len(self.plot_hist.shape) == 1:
            self.check_RGB_widget.hide()
            bar_graph = BarGraphItem(x=bins,
                                     height=self.plot_hist,
                                     width=1, brush=self.line_color)
            if self.y_axis_height != 0:
                self.plot_chart_widget.setYRange(0, self.y_axis_height)
            self.plot_chart_widget.showGrid(x=True, y=True)
            styles = {"color": "black", "font-size": "18px"}
            if self.y_axis_label != '':
                self.plot_chart_widget.setLabel("left", self.y_axis_label, **styles)
            if self.x_axis_label != '':
                self.plot_chart_widget.setLabel("bottom", self.x_axis_label, **styles)
            self.plot_chart_widget.addItem(bar_graph)
        else:
            self.check_RGB_widget.show()
            if self.y_axis_height != 0:
                self.plot_chart_widget.setYRange(0, self.y_axis_height)
            self.plot_chart_widget.showGrid(x=True, y=True)
            styles = {"color": "black", "font-size": "18px"}
            if self.y_axis_label != '':
                self.plot_chart_widget.setLabel("left", self.y_axis_label, **styles)
            if self.x_axis_label != '':
                self.plot_chart_widget.setLabel("bottom", self.x_axis_label, **styles)
            if self.check_RGB_widget.is_R_checked():
                bar_graph_R = BarGraphItem(x=bins,
                                           height=self.plot_hist[:, 0],
                                           width=1, brush='red')
                self.plot_chart_widget.addItem(bar_graph_R)
            if self.check_RGB_widget.is_G_checked():
                bar_graph_G = BarGraphItem(x=bins,
                                           height=self.plot_hist[:, 1],
                                           width=1, brush='green')
                self.plot_chart_widget.addItem(bar_graph_G)
            if self.check_RGB_widget.is_B_checked():
                bar_graph_B = BarGraphItem(x=bins,
                                           height=self.plot_hist[:, 2],
                                           width=1, brush='blue')
                self.plot_chart_widget.addItem(bar_graph_B)
            mean_R = np.round(np.mean(self.plot_hist_data[:, :, 0]), 2)
            std_R = np.round(np.std(self.plot_hist_data[:,:,0]), 2)
            mean_G = np.round(np.mean(self.plot_hist_data[:, :, 1]), 2)
            std_G = np.round(np.std(self.plot_hist_data[:,:,1]), 2)
            mean_B = np.round(np.mean(self.plot_hist_data[:, :, 2]), 2)
            std_B = np.round(np.std(self.plot_hist_data[:,:,2]), 2)
            self.check_RGB_widget.update_infos(mean_R, std_R, mean_G, std_G, mean_B, std_B)

    def update_info(self, val: bool = True) -> None:
        """Update mean and standard deviation data and display.

        :param val: True to display mean and standard deviation.
                    False to display "acquisition in progress".
        :type val: bool

        """
        if val:
            mean_d = round(np.mean(self.plot_hist_data), 2)
            stdev_d = round(np.std(self.plot_hist_data), 2)
            self.set_information(f'Mean = {mean_d} / Standard Dev = {stdev_d}')
        else:
            self.set_information('Data Acquisition In Progress')

    def set_name(self, name: str) -> None:
        """Set the name of the chart.

        :param name: Name of the chart
        :type name: str

        """
        self.name = name
        self.title_label.setText(self.name)

    def set_information(self, info: str) -> None:
        """Set information in the information label of the chart.
        (bottom)

        :param info: Information to display.
        :type info: str

        """
        self.info_label.setText(info)

    def set_background(self, css_color):
        """Set the background color of the widget.

        :parap css_color: Color in CSS style.
        :type css_color: str

        """
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def set_y_axis_limit(self, value):
        """Set the y axis limit."""
        self.y_axis_height = value

    def clear_graph(self):
        """Clear the main chart of the widget.
        """
        self.plot_chart_widget.clear()

    def set_v_line(self, position: int, color: str = 'r'):
        """
        Display a vertical line at a specific position.
        :param position: X position of the line.
        :param color: Color of the line ('r', 'b'...). Default red (r).
        """
        v_line = InfiniteLine(pos=position, angle=90, pen=color)
        self.plot_chart_widget.addItem(v_line)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 700, 400)

            self.central_widget = QWidget()
            self.layout = QVBoxLayout()

            self.histo_widget = HistogramWidget('Histogram Test')
            self.histo_widget.set_information('This is a test')
            self.layout.addWidget(self.histo_widget)

            bins = np.linspace(0, 100, 101)
            data = np.random.randint(0, 100, 1001, dtype=np.int8)
            self.histo_widget.set_background('white')
            self.histo_widget.set_data(data, bins)
            self.histo_widget.refresh_chart()
            self.histo_widget.enable_chart()

            self.central_widget.setLayout(self.layout)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
