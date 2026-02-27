# -*- coding: utf-8 -*-
"""XYChartWidget for displaying data on a 2D chart.

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/02


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python XYChartWidget.py
"""
# PEP257 / PEP8 // OK

# Standard Libraries
import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget


# Local libraries


# -----------------------------------------------------------------------------------------------

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

    def __init__(self):
        """
        Initialisation of the time-dependent chart.

        """
        super().__init__()
        self.title = ''  # Title of the chart
        self.layout = QVBoxLayout()  # Main layout of the QWidget

        # Title label
        self.title_label = QLabel(self.title)
        style = "background-color: darkgray;"
        style += "font-weight:bold;"
        style += "color:white;"
        style += "font-size:20px;"
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.title_label.setStyleSheet(style)

        # Option label
        self.info_label = QLabel('')
        style = "background-color: lightgray;"
        style += "font-size:10px;"
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.info_label.setStyleSheet(style)

        self.plot_chart_widget = PlotWidget()  # pyQtGraph widget
        # Create Numpy array for X and Y data
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])

        # No data at initialization
        self.plot_chart = self.plot_chart_widget.plot([0])
        self.setLayout(self.layout)

    def set_data(self, x_axis, y_axis):
        """
        Set the X and Y axis data to display on the chart.

        Parameters
        ----------
        x_axis : Numpy array
            X-axis value to display.
        y_axis : Numpy array
            Y-axis value to display.

        Returns
        -------
        None.

        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis

    def refresh_chart(self):
        """
        Refresh the data of the chart. 

        Returns
        -------
        None.

        """
        self.plot_chart_widget.removeItem(self.plot_chart)
        self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                      self.plot_y_data)

    def update_infos(self, val=True):
        """
        Update mean and standard deviation data and display.

        Parameters
        ----------
        val : bool
            True to display mean and standard deviation.
            False to display "acquisition in progress".

        Returns
        -------
        None

        """
        if val:
            mean_d = round(np.mean(self.plot_y_data), 2)
            stdev_d = round(np.std(self.plot_y_data), 2)
            self.set_information(f'Mean = {mean_d} / Standard Dev = {stdev_d}')
        else:
            self.set_information('Data Acquisition In Progress')

    def set_title(self, title):
        """
        Set the title of the chart.

        Parameters
        ----------
        title : str
            Title of the chart.

        Returns
        -------
        None.

        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos):
        """
        Set informations in the informations label of the chart.
        (bottom)

        Parameters
        ----------
        infos : str
            Informations to display.

        Returns
        -------
        None.

        """
        self.info_label.setText(infos)

    def set_background(self, css_color):
        """
        Modify the background color of the widget.

        Parameters
        ----------
        css_color : str
            Color in CSS style.

        Returns
        -------
        None.

        """
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the main chart of the widget.

        Returns
        -------
        None

        """
        self.plot_chart_widget.clear()

    def disable_chart(self):
        """
        Erase all the widget of the layout.

        Returns
        -------
        None

        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self):
        """
        Display all the widget of the layout.

        Returns
        -------
        None

        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)


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
        y = np.random.randint(0, 100, 101, dtype=np.int8)

        self.chart_widget.set_background('red')

        self.chart_widget.set_data(x, y)
        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)

# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
