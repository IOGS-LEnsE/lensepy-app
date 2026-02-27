# -*- coding: utf-8 -*-
"""TimeChartWidget for displaying time-dependent data on a 2D chart.

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
    >>> python TimeChartWidget.py
"""
# PEP257 / PEP8 // OK

# Standard Libraries
import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

# Local libraries
from SupOpNumTools.pyqt6.XYChartWidget import XYChartWidget



#-----------------------------------------------------------------------------------------------

class TimeChartWidget(XYChartWidget):
    """
    Widget used to display a time-dependent data in a 2D chart.
    Children of XYChartWidget 
    ---
    
    Attributes
    ----------
    max_points: int
        maximum of points to display. Default : 100.
    
    Methods
    -------
    info(additional=""):
        Prints the person's name and age.
    """
    
    def __init__(self):
        """
        Initialisation of the time-dependent chart.

        """
        super().__init__()
        self.max_points = 100
        
    def refresh_chart(self):
        """
        Refresh the chart with specific time limits.

        Returns
        -------
        None

        """
        # Test if maxpoints ?
        super().refresh_chart()

# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("XY Chart")
        self.setGeometry(100, 100, 800, 600)
        
        self.centralWid = QWidget()
        self.layout = QVBoxLayout()
        
        
        self.chart_widget = TimeChartWidget()
        self.chart_widget.set_title('My Super Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)
        
        x = np.linspace(0,100, 101)
        y = np.random.randint(0, 100, 101, dtype=np.int8)
        
        self.chart_widget.set_background('white')
        
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