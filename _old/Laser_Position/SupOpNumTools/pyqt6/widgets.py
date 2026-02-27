# -*- coding: utf-8 -*-
"""Different Widget to use in PyQt6 applications

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/06/12


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python TimeChartWidget.py
"""

import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit
from PyQt6.QtWidgets import QHBoxLayout, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QLabel, QPushButton, QMessageBox, QCheckBox, QSlider
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QRect
from pyqtgraph import PlotWidget, plot, mkPen

styleH1 = "font-size:16px; padding:7px; color:Navy; border-top: 1px solid Navy;"
styleH = "font-size:14px; padding:4px; color:Navy;"
styleV = "font-size:14px; padding:2px; "


"""
Graph1D class
"""
class graph1D(QWidget):
    
    def __init__(self, name=''):
        super().__init__() 
        self.name = name
        ''' '''
        self.y_range_min = -1
        self.y_range_max = 1
        self.x_range_min = 0
        self.x_range_max = 1
        self.length = 1001
        self.legend_bottom = ''
        self.legend = []
        self.pen = []
        self.pen.append(mkPen(color=(80, 128, 80), width=3))
        self.pen.append(mkPen(color=(128, 192, 0), width=6))
        self.pen.append(mkPen(color=(80, 80, 128), width=3))
        self.pen.append(mkPen(color=(0, 128, 192), width=6))
        self.pen.append(mkPen(color=(128, 80, 80), width=3))
        self.pen.append(mkPen(color=(192, 128, 0), width=6))
        self.nb_signal = 1
        ''' Layout '''
        self.plotLayout = QVBoxLayout()
        self.setLayout(self.plotLayout)
        ''' Graph section '''
        self.plot_section = PlotWidget()
        self.plotLayout.addWidget(self.plot_section)
        
        self.plot_section.setBackground('black')
        
        #self.plotSection.setYRange(self.yRangeMin, self.yRangeMax, padding=0)
        self.plot_section.setLabel('bottom', self.legend_bottom)
        self.x_data = np.linspace(self.x_range_min, self.x_range_max, self.length)
        self.y_data = np.sin(self.x_data)
        
        self.refresh_graph()
        
    def set_y_range(self, ymin, ymax):
        self.y_range_min = ymin
        self.y_range_max = ymax
        self.plot_section.set_y_range(self.y_range_min, self.y_range_max, padding=0)
        
    
    def set_data(self, x, y):
        self.x_data = x
        self.y_data = y
        
        try:
            self.nb_signal = x.shape[1]
            pass
        except Exception:
            self.nb_signal = 1
            pass
                
    def refresh_graph(self, log_x=False, log_y=False):
        """ Displaying data """
        self.plot_section.clear()
        self.plot_section.add_legend()
        self.plot_section.showGrid(x = True, y = True, alpha = 1.0)
        # Test the shape of the data to plot different curves
        
        if(self.nb_signal > 1):
            for k in range(self.nb_signal):
                if(self.legend):
                    self.plot_section.plot(self.x_data[:,k], self.y_data[:,k],
                                      pen=self.pen[k], name=self.legend[k])
                else:
                    self.plot_section.plot(self.x_data[:,k], self.y_data[:,k],
                                      pen=self.pen[k])
            self.plot_section.setLogMode(log_x, log_y)
        else:
            self.plot_section.plot(self.x_data, self.y_data, pen=self.pen[1])
            self.plot_section.setLogMode(log_x, log_y)
    
    def set_legend(self, legends):
        self.legend = legends
        

"""
TitleBlock class
"""
class titleBlock(QWidget):
    tBsignal = pyqtSignal(str)
    
    def __init__(self, title='', checkBox=False):
        super().__init__()
        self.title = title
        self.enabled = True
        self.checkBox = checkBox
        ''' Layout Manager '''
        self.layout = QGridLayout()
        ''' Graphical Objects '''
        self.name = QLabel(self.title)
        self.name.setMaximumWidth(300)
        self.name.setStyleSheet(styleH1)
        self.checkB = QCheckBox('EN')
        self.checkB.setStyleSheet(styleV)
        ''' Adding GO into the widget layout '''
        self.layout.addWidget(self.name, 1, 0)  # Position 1,0 / one cell
        if(self.checkBox):
            self.layout.addWidget(self.checkB, 1, 1)
            self.checkB.toggled.connect(self.checkedBox)
        self.setLayout(self.layout)
    
    def setTitle(self, value):
        self.title = value 
        self.name.setText(self.title)
        
    def checkedBox(self):
        self.tBsignal.emit('tB')
    
    def isChecked(self):
        return self.checkB.isChecked()
    
    def setChecked(self, value):
        self.checkB.setCheckState(value)


"""
LabelBlock class
"""
class labelBlock(QWidget):
    lBsignal = pyqtSignal(str)
    
    def __init__(self, name='', checkBox=False):
        super().__init__()
        self.units = ''
        self.realValue = ''
        self.enabled = True
        self.checkBox = checkBox
        ''' Layout Manager '''
        self.layout = QGridLayout()
        ''' Graphical Objects '''
        self.name = QLabel(name)
        self.name.setMaximumWidth(200)
        self.value = QLabel('')
        self.value.setMaximumWidth(300)
        self.name.setStyleSheet(styleH1)
        self.value.setStyleSheet(styleH)
        self.checkB = QCheckBox('EN')
        ''' Adding GO into the widget layout '''
        self.layout.addWidget(self.name, 1, 0)  # Position 1,0 / one cell
        self.layout.addWidget(self.value, 1, 1)  # Position 1,1 / one cell
        if(self.checkBox):
            self.layout.addWidget(self.checkB, 1, 2)
            self.checkB.toggled.connect(self.checkedBox)
        self.setLayout(self.layout)
    
    def setValue(self, value):
        self.realValue = value 
        self.updateDisplay()
    
    def setUnits(self, units):
        self.units = units

    def updateDisplay(self):
        displayValue = self.realValue
        displayUnits = self.units
        if(self.realValue / 1000 >= 1):
            displayValue = self.realValue / 1000
            displayUnits = 'k'+self.units
        if(self.realValue / 1e6 >= 1):
            displayValue = self.realValue / 1e6
            displayUnits = 'M'+self.units
            
        textT = f'{displayValue} {displayUnits}'
        self.value.setText(textT)
        
    def checkedBox(self):
        self.lBsignal.emit('lB')

