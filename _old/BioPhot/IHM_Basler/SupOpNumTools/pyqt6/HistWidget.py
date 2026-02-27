# -*- coding: utf-8 -*-
"""HistWidget for displaying histogram.

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
    >>> python HistWidget.py
"""
# PEP257 / PEP8 // OK

# Standard Libraries
import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, BarGraphItem

# Local libraries



#-----------------------------------------------------------------------------------------------

class HistWidget(QWidget):
    """
    Widget used to display histogram.
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
    plot_hist_data : Numpy array
        data to process as histogram
    plot_hist : Numpy array
        histogram of the data
    plot_bins_data : Numpy array
        bins on X axis of the chart
    
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
    
    def __init__(self):
        """
        Initialisation of the time-dependent chart.

        """
        super().__init__()
        self.title = ''     # Title of the chart
        self.layout = QVBoxLayout()     # Main layout of the QWidget
        
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

        self.plot_chart_widget = PlotWidget()     # pyQtGraph widget
        # Create Numpy array for X and Y data
        self.plot_hist_data = np.array([])
        self.plot_bins_data = np.array([])
        self.plot_hist = np.array([])
        
        # No data at initialization
        self.plot_chart = self.plot_chart_widget.plot([0])
        self.setLayout(self.layout)
        
    def set_data(self, data, bins):
        """
        Set the X and Y axis data to display on the chart.

        Parameters
        ----------
        data : Numpy array
            data to process histogram.
        bins : Numpy array
            bins on X axis of the chart.

        Returns
        -------
        None.

        """
        self.plot_hist_data = data
        self.plot_bins_data = bins
        self.plot_hist, self.plot_bins_data = np.histogram(
            self.plot_hist_data,
            bins=self.plot_bins_data)
        
    def refresh_chart(self):
        """
        Refresh the data of the chart. 

        Returns
        -------
        None.

        """
        # TO CHANGE INTO HISTOGRAM !!
        self.plot_chart_widget.clear()
        bins = self.plot_bins_data[:len(self.plot_hist)]
        barGraph = BarGraphItem(x=bins,
                                height=self.plot_hist,
                                width=1, brush='blue')
        self.plot_chart_widget.addItem(barGraph)

    def update_infos(self, val = True):
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
            mean_d = round(np.mean(self.plot_hist_data), 2)
            stdev_d = round(np.std(self.plot_hist_data), 2)
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
        self.setStyleSheet("background:"+css_color+";")

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
        # Adding graphical elements in the QWidget layout
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
        
        self.chart_widget = HistWidget()
        self.chart_widget.set_title('My Super Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)
        
        x = np.linspace(0,100, 101)
        y = np.random.randint(0, 100, 101, dtype=np.int8)
        
        self.chart_widget.set_background('lightblue')
        
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