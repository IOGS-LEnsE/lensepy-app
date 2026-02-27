"""
histogram_widget.py
===================

PyQt6 widget for displaying the histogram of an image (grayscale or RGB)
as bar charts. Allows visualization of the R, G, B channels and luminance
with filtering options and customizable appearance.

Classes
-------
HistogramWidget(QWidget)
    Main widget for displaying an image histogram.

Features
--------
- Graphical display using pyqtgraph
- Supports grayscale and RGB images
- Automatic bit-depth handling (8, 16…)
- Channel selection via checkboxes
- Customizable background color
- Optimized for large images

Usage Example
-------------

.. code-block:: python

    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    widget = HistogramWidget()
    widget.setWindowTitle("Histogram Widget Test")
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image(test_image)
    widget.set_bits_depth(8)
    widget.set_background('w')

    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QCheckBox,
                             QSizePolicy, QLabel)
import pyqtgraph as pg
from lensepy import translate

from lensepy.utils.images import resize_image_ratio

class HistogramSimpleWidget(QWidget):
    """Simple Histogram display from data. Auto zoom."""
    def __init__(self, title="Histogramme", parent=None):
        super().__init__(parent)

        # Layout vertical
        self.layout = QVBoxLayout(self)

        # PlotWidget pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle(title)
        self.plot_widget.showGrid(x=True, y=True)

        self.layout.addWidget(self.plot_widget)

        # Histogramme via un plot step
        self.hist_plot = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(200, 200, 200, 150))
        self.plot_widget.addItem(self.hist_plot)


    def set_title(self, title: str):
        """Changer le titre affiché sur le widget."""
        self.plot_widget.setTitle(title)

    def set_data(self, data, bits_depth=12):
        """Update data for histogram display."""
        # Remove old histogram
        self.plot_widget.removeItem(self.hist_plot)
        # Process zoom
        vmin = np.min(data)
        vmax = np.max(data)
        hist_range = (vmin, vmax)
        nbins = int(vmax - vmin + 1)

        hist, bins = np.histogram(data, bins=nbins, range=hist_range)
        self.hist_plot.setOpts(x=bins[:-1], height=hist, width=1)
        self.plot_widget.addItem(self.hist_plot)

    def set_background(self, color):
        """
        Change la couleur de fond du graphique.
        color : ex. 'k' (noir), 'w' (blanc), '#202020', (r,g,b), (r,g,b,a)
        """
        self.plot_widget.setBackground(color)


class HistogramWidget(QWidget):
    """Histogram of an image."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None
        self.bits_depth = 8
        self.xlabel = 'Intensity'
        self.ylabel = 'Number of pixels'

        # Layout principal
        layout = QVBoxLayout(self)

        # Zone graphique
        self.plot = pg.PlotWidget()
        self.plot.setLabel('bottom', self.xlabel)
        self.plot.setLabel('left', self.ylabel)
        layout.addWidget(self.plot)

        # BarGraphItems for each channel
        self.bar_r = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(255, 0, 0, 150))
        self.bar_g = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 255, 0, 150))
        self.bar_b = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(0, 0, 255, 150))
        self.bar_l = pg.BarGraphItem(x=[0], height=[0], width=1, brush=pg.mkBrush(200, 200, 200, 150))

        self.plot.addItem(self.bar_r)
        self.plot.addItem(self.bar_g)
        self.plot.addItem(self.bar_b)
        self.plot.addItem(self.bar_l)

        # Checkboxes
        box_layout = QHBoxLayout()
        self.chk_r = QCheckBox("R")
        self.chk_g = QCheckBox("G")
        self.chk_b = QCheckBox("B")
        self.chk_l = QCheckBox("Lum.")
        for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
            chk.setChecked(True)
            chk.stateChanged.connect(self.refresh_chart)
            box_layout.addWidget(chk)
        layout.addLayout(box_layout)

    def reinit_checkbox(self, mode: str):
        """
        Update checkbox visibility.
        :param mode:    'RGB' or 'Gray'
        """
        # Detect if RGB or Grayscale
        if mode == 'Gray':
            for chk in [self.chk_r, self.chk_g, self.chk_b]:
                chk.setEnabled(False)
                chk.setChecked(False)
            self.chk_l.setEnabled(False)
            self.chk_l.setChecked(True)
        elif mode == 'RGB':
            for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                chk.setChecked(True)
                chk.setEnabled(True)

    def set_image(self, img: np.ndarray, checked: bool = True, zoom:bool = False):
        """Définit l'image (numpy array, 2D pour gris ou 3D pour RGB)."""
        self.image = img.copy()
        # Detect if RGB or Grayscale
        if img.ndim == 2:
            # Grayscale image
            # Update checkboxes
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b]:
                    chk.setEnabled(False)
                    chk.setChecked(False)
                self.chk_l.setEnabled(False)
                self.chk_l.setChecked(True)
        else:
            # RGB image
            if checked:
                for chk in [self.chk_r, self.chk_g, self.chk_b, self.chk_l]:
                    chk.setChecked(True)
                    chk.setEnabled(True)
        self.refresh_chart(zoom=zoom)

    def set_bits_depth(self, depth: int):
        """Define bits depth in bits (8, 16...)."""
        self.bits_depth = depth
        self.refresh_chart()

    def set_labels(self, xlabel: str, ylabel: str):
        """Define labels of the chart."""
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.plot.setLabel('bottom', self.xlabel)
        self.plot.setLabel('left', self.ylabel)

    def set_background(self, color):
        """
        Change background color.
        color : ex. 'k' (black), 'w' (white), '#202020', (r,g,b), (r,g,b,a)
        """
        self.plot.setBackground(color)

    def refresh_chart(self, zoom: bool=False):
        """
        Process and display histogram.
        :param zoom:    If histogram needs to be zoomed.
        """
        # Empty graphe if no image
        if self.image is None:
            for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
                self.plot.removeItem(bar)
            return

        max_val = 2 ** self.bits_depth - 1
        hist_range = (0, max_val)

        # Remove all the data
        for bar in [self.bar_r, self.bar_g, self.bar_b, self.bar_l]:
            self.plot.removeItem(bar)

        image = self.image
        '''
        # Fast mode
        if self.image.shape[0] * self.image.shape[1] > 1000000:
            image = resize_image_ratio(image, self.image.shape[0]//4,  self.image.shape[1]//4)
        '''
        if image.ndim == 2:
            # Grayscale image
            if self.chk_l.isChecked():
                if zoom:
                    vmin = np.min(image)
                    vmax = np.max(image)
                else:
                    vmin = 0
                    vmax = max_val+1
                hist_range = (vmin, vmax)
                nbins = int(vmax - vmin + 1)

                hist, bins = np.histogram(image, bins=nbins, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist, width=1)
                self.plot.addItem(self.bar_l)

        elif image.ndim == 3 and image.shape[2] >= 3:
            lum = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
            # RGB image
            if zoom:
                r_min, r_max = np.min(image[:,0]), np.max(image[:,0])
                g_min, g_max = np.min(image[:,1]), np.max(image[:,1])
                b_min, b_max = np.min(image[:,2]), np.max(image[:,2])
                l_min, l_max = np.min(lum), np.max(lum)
                vmin = np.min([r_min, g_min, b_min, l_min])
                vmax = np.max([r_max, g_max, b_max, l_max])
            else:
                vmin = 0
                vmax = max_val + 1

            hist_range = (vmin, vmax)
            nbins = int(vmax - vmin + 1)

            if self.chk_r.isChecked():
                hist_r, bins = np.histogram(image[:, :, 0], bins=nbins, range=hist_range)
                self.bar_r.setOpts(x=bins[:-1], height=hist_r, width=1)
                self.plot.addItem(self.bar_r)

            if self.chk_g.isChecked():
                hist_g, bins = np.histogram(image[:, :, 1], bins=nbins, range=hist_range)
                self.bar_g.setOpts(x=bins[:-1], height=hist_g, width=1)
                self.plot.addItem(self.bar_g)

            if self.chk_b.isChecked():
                hist_b, bins = np.histogram(image[:, :, 2], bins=nbins, range=hist_range)
                self.bar_b.setOpts(x=bins[:-1], height=hist_b, width=1)
                self.plot.addItem(self.bar_b)

            if self.chk_l.isChecked():
                hist_l, bins = np.histogram(lum, bins=nbins, range=hist_range)
                self.bar_l.setOpts(x=bins[:-1], height=hist_l, width=1)
                self.plot.addItem(self.bar_l)


class HistoStatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.histo_zoom = False
        self.histo = HistogramWidget()
        self.histo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        widget_zoom = QWidget()
        layout_zoom = QHBoxLayout()
        widget_zoom.setLayout(layout_zoom)
        self.label_stats = QLabel(translate('histo_stats_title'))
        self.label_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_stats.setMaximumHeight(10)
        layout = QVBoxLayout()
        layout.addWidget(self.histo, 5)
        layout.addWidget(widget_zoom, 1)
        layout_zoom.addWidget(self.label_stats)
        self.check_box = QCheckBox(translate('zoom_check_box'))
        layout_zoom.addWidget(self.check_box)
        self.check_box.stateChanged.connect(self.handle_zoom_changed)
        layout_zoom.addWidget(self.label_stats)
        self.setLayout(layout)

    def handle_zoom_changed(self, event):
        """

        """
        self.histo_zoom = self.check_box.isChecked()

    def set_image(self, image):
        mean_image = np.round(np.mean(image), 2)
        stdev_image = np.round(np.std(image), 2)
        str_val = f'Mean = {mean_image} / Stdev = {stdev_image}'
        self.label_stats.setText(str_val)
        self.histo.set_image(image, zoom=self.histo_zoom)

    def set_background(self, color):
        """
        Set the background color of the histogram.
        :param color: Background color.
        """
        self.histo.set_background(color)

    def set_bits_depth(self, bits_depth):
        """
        Set the bits depth of the histogram.
        :param bits_depth: Bits depth.
        """
        self.histo.set_bits_depth(bits_depth)

    def set_labels(self, xlabel: str, ylabel: str):
        """Define labels of the chart."""
        self.histo.set_labels(xlabel, ylabel)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = HistogramWidget()
    widget.setWindowTitle("Histogram Widget Test")

    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image(test_image)
    widget.set_bits_depth(8)
    widget.set_background('w')

    widget.show()
    sys.exit(app.exec())