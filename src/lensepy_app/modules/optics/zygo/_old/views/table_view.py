# -*- coding: utf-8 -*-
"""*table_view.py* file.

./views/table_view.py contains TableView class to display a table.

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


from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QFont

class TableView(QWidget):
    """Table view class."""

    def __init__(self, rows: int, cols: int, cell_size: int=50, height: int = 25, title: str='') -> None:
        """Default constructor of the class.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(styleH1)
        self.layout.addWidget(self.title_label, stretch=1)
        self.tableGraph = TableGraphicsView(rows=rows, cols=cols, cell_size=cell_size, height=height)
        self.layout.addWidget(self.tableGraph, stretch=6)

    def set_data(self, data: list):
        """
        Update data of the table.
        :param data: data as a list in 2D.
        """
        self.tableGraph.set_data(data)

    def set_rows_colors(self, colors: list[str]):
        """
        Set the color for each row.
        :param colors: List of 'H' or 'N' str for normal or header color for each row.
        """
        self.tableGraph.set_rows_colors(colors)

    def set_cols_colors(self, colors: list[str]):
        """
        Set the color for each col.
        'H' for header color, 'N' nor normal color, 'L' for light color
        :param colors: List for each col.
        """
        self.tableGraph.set_cols_colors(colors)

    def set_cols_size(self, sizes: list[int]):
        """
        Set the size for each col.
        :param sizes: List for each col.
        """
        self.tableGraph.set_cols_size(sizes)


class TableGraphicsView(QGraphicsView):
    """

    """
    def __init__(self, rows: int, cols: int, cell_size: int=50, height: int = 25):
        """

        :param rows:
        :param cols:
        :param cell_size:
        """
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cell_size_list = None
        self.cell_height = height
        self.data = None
        self.header_color = BLUE_IOGS
        self.header_text_color = 'white'
        self.normal_color = 'white'
        self.normal_text_color = 'black'
        self.light_color = 'lightgray'
        self.light_text_color = 'black'
        self.rows_color = None # List of N cols with 'H' for header, 'N' nor normal, 'L' for light
        self.cols_color = None # List of N rows with 'H' for header, 'N' nor normal, 'L' for light
        self._draw_table()

    def _draw_table(self):
        """

        :return:
        """
        self._erase_table()
        for row in range(self.rows):
            for col in range(self.cols):
                color = 'N'
                back_color = self.normal_color
                text_color = self.normal_text_color
                if self.rows_color is not None:
                    if self.rows_color[row] == 'H':
                        color = 'H'
                    elif self.rows_color[row] == 'L':
                        color = 'L'
                if self.cols_color is not None:
                    if self.cols_color[col] == 'H':
                        color = 'H'
                    elif self.cols_color[col] == 'L':
                        color = 'L'
                if color == 'H':
                    back_color = self.header_color
                    text_color = self.header_text_color
                elif color == 'L':
                    back_color = self.light_color
                    text_color = self.light_text_color

                if self.cell_size_list is not None:
                    row_size = self.cell_size_list[col]
                    row_pos = sum(self.cell_size_list[:col])
                else:
                    row_size = self.cell_size
                    row_pos = col * row_size

                rect = QGraphicsRectItem(QRectF(row_pos, row * self.cell_height,
                                                row_size, self.cell_height))
                rect.setBrush(QBrush(QColor(back_color)))
                rect.setPen(QColor(text_color))
                self.scene.addItem(rect)

                if self.data is not None:
                    # Centered text
                    text_item = QGraphicsTextItem(f"{self.data[row][col]}")
                    text_item.setFont(QFont("Arial", 12))
                    text_item.setDefaultTextColor(QColor(text_color))

                    # Text position
                    text_rect = text_item.boundingRect()
                    text_x = row_pos + (row_size - text_rect.width()) / 2
                    text_y = row * self.cell_height + (self.cell_height - text_rect.height()) / 2
                    text_item.setPos(text_x, text_y)

                    self.scene.addItem(text_item)

    def _erase_table(self):
        """Efface tout le tableau"""
        self.scene.clear()

    def set_data(self, data: list):
        """
        Update data of the table.
        :param data: data as a list in 2D.
        """
        self.data = data
        self._draw_table()

    def set_rows_colors(self, colors: list[str]):
        """
        Set the color for each row.
        :param colors: List of 'H' or 'N' str for normal or header color for each row.
        """
        self.rows_color = colors
        self._draw_table()

    def set_cols_colors(self, colors: list[str]):
        """
        Set the color for each col.
        'H' for header color, 'N' nor normal color, 'L' for light color
        :param colors: List for each col.
        """
        self.cols_color = colors
        self._draw_table()

    def set_cols_size(self, sizes: list[int]):
        """
        Set the size for each col.
        :param sizes: List for each col.
        """
        self.cell_size_list = sizes
        self._draw_table()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    def analyses_changed(value):
        print(value)

    app = QApplication(sys.argv)
    main_widget = TableView(5, 5, cell_size=100)
    main_widget.setGeometry(100, 100, 700, 500)
    main_widget.show()

    # Class test
    main_widget.set_cols_size([200, 50, 50, 80, 60])
    main_widget.set_rows_colors(['H','N','L','H','N'])
    main_widget.set_cols_colors(['N','H','N','N','N'])

    sys.exit(app.exec())