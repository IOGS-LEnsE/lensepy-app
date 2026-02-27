# -*- coding: utf-8 -*-
"""*widget_image_histogram* file.

*widget_image_histogram* file that contains :class::ImageHistogramWidget

.. module:: ImageHistogramWidget
   :synopsis: class to display the histogram in PyQt6 of an image (requires pyqtGraph).

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

# Standard Libraries
import numpy as np
import sys

# Third pary imports
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, BarGraphItem
if __name__ == '__main__':
    from widget_histogram import HistogramWidget
else:
    from lensepy.pyqt6.widget_histogram import HistogramWidget
from lensepy.css import *
from lensepy.images.conversion import resize_image_ratio


class ImageHistogramWidget(HistogramWidget):
    """Create a Widget with a histogram.

    Widget used to display a histogram of an image.
    Children of HistogramWidget.
    """

    def __init__(self, name: str = '', info:bool = True) -> None:
        """Initialize the histogram widget.
        """
        super().__init__(name, info)
        self.bit_depth = 8
        self.bins = np.linspace(0, 2**self.bit_depth, 2**self.bit_depth+1)

    def set_bit_depth(self, bit_depth: int = 8):
        """Set the bit depth of a pixel."""
        self.bit_depth = bit_depth
        self.bins = np.linspace(0, 2**self.bit_depth, 2**self.bit_depth+1)

    def set_image(self, image: np.ndarray, fast_mode: bool = False, black_mode:bool = False,
                  log_mode: bool = False, zoom_mode: bool = False, zoom_target: int = 5) -> None:
        """Set an image and the bit depth of a pixel.

        :param data: data to process histogram.
        :param fast_mode: True to accelerate the process (but under sampling).
        :param log_mode: True for log value in Y-axis.
        :param black_mode: True for removing 10 first values of the histogram.
        :param zoom_mode: True to display a zoom of the histogram.
        :param zoom_target: Minimum value to reach to zoom.
        """
        if fast_mode:
            image = resize_image_ratio(image, image.shape[0]//4,  image.shape[1]//4)
        super().set_data(image, self.bins, black_mode=black_mode, log_mode=log_mode,
                         zoom_mode=zoom_mode, zoom_target=zoom_target)
        super().refresh_chart()


class DoubleHistoWidget(QWidget):
    """
    Widget that displays 2 histograms in the quantization mode.
    First histogram is the initial image, second one is the modified image.
    """

    def __init__(self, parent, name_histo_1: str='histo_original_image',
                 name_histo_2: str='histo_quantized_image'):
        """
        Default Constructor.
        :param parent: Parent widget of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.histo1 = ImageHistogramWidget(name_histo_1, info=False)
        self.histo1.set_background('white')
        self.histo2 = ImageHistogramWidget(name_histo_2, info=False)
        self.histo2.set_background('lightgray')
        self.layout.addWidget(self.histo1)
        self.layout.addWidget(self.histo2)

    def set_bit_depth(self, histo2: int, histo1: int = 8):
        """
        Set the bits depth for the two histogram.
        :param histo2: Bit depth of the modified image.
        :param histo1: Bit depth of the original image. Default: 8 bits.
        """
        self.histo1.set_bit_depth(histo1)
        self.histo2.set_bit_depth(histo2)

    def set_images(self, histo1: np.ndarray, histo2: np.ndarray):
        """
        Set the images to calculate histograms.
        :param histo1: Array containing the original image.
        :param histo2: Array containing the modified image.
        """
        self.histo1.set_image(histo1)
        self.histo2.set_image(histo2)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 700, 400)

            self.central_widget = QWidget()
            self.layout = QVBoxLayout()

            self.histo_widget = ImageHistogramWidget('Histogram Test')
            self.histo_widget.set_information('This is a test')
            self.layout.addWidget(self.histo_widget)

            my_image = np.random.randint(0, 4095, (800, 600), dtype=np.uint16)
            #self.histo_widget.set_y_axis_limit(500)
            self.histo_widget.set_background('white')
            self.histo_widget.set_image(my_image)

            self.central_widget.setLayout(self.layout)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
