# -*- coding: utf-8 -*-
"""*images_display_view.py* file.

./views/images_display_view.py contains ImagesDisplayView and
 ImageToGraphicsScene classes to display images in PyQt6 GUI.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QImage, QPainter


class ImagesDisplayView(QGraphicsView):
    """
    Widget to display an image.
    """

    def __init__(self):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__()
        self.__scene = ImageToGraphicsScene(self)
        self.setScene(self.__scene)

    def set_image(self, image: QImage):
        self.__scene.set_image(image)
        self.update()

    def set_image_from_array(self, np_array: np.array):
        image_disp = np_array.copy().astype(np.uint8)
        height, width, *channels = image_disp.shape
        if channels:
            if channels[0] == 1:
                image_disp = image_disp.squeeze()
                image = QImage(image_disp, width, height, QImage.Format.Format_Grayscale8)
            else:
                image = QImage(image_disp, width, height, 3*width, QImage.Format.Format_RGB888)
        else:
            image = QImage(image_disp, width, height, QImage.Format.Format_Grayscale8)
        self.__scene.set_image(image)
        self.update()

    def fit_images_in_view(self):
        self.fitInView(self.__scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)


class ImageToGraphicsScene(QGraphicsScene):
    def __init__(self, parent: ImagesDisplayView = None):
        super().__init__(parent)
        self.__parent = parent
        self.__image = QImage()

    def set_image(self, image: QImage):
        self.__image = image
        self.update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        try:
            # Display size
            display_width = self.__parent.width()
            display_height = self.__parent.height()
            # Image size
            image_width = self.__image.width()
            image_height = self.__image.height()

            # Return if we don't have an image yet
            if image_width == 0 or image_height == 0:
                return

            if image_width > display_width or image_height > display_height:
                # Calculate aspect ratio of display
                ratio1 = display_width / display_height
                # Calculate aspect ratio of image
                ratio2 = image_width / image_height

                if ratio1 > ratio2:
                    # The height with must fit to the display height.So h remains and w must be scaled down
                    image_width = display_height * ratio2
                    image_height = display_height
                else:
                    # The image with must fit to the display width. So w remains and h must be scaled down
                    image_width = display_width
                    image_height = display_height / ratio2

            image_pos_x = -1.0 * (image_width / 2.0)
            image_pox_y = -1.0 * (image_height / 2.0)

            # Remove digits after point
            image_pos_x = int(image_pos_x)
            image_pox_y = int(image_pox_y)

            rect = QRectF(image_pos_x, image_pox_y, image_width, image_height)

            painter.drawImage(rect, self.__image)
        except Exception as e:
            print(f'draw_background / {e}')


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import time

    app = QApplication(sys.argv)
    main_widget = ImagesDisplayView()
    main_widget.setGeometry(100, 100, 300, 500)
    main_widget.show()

    # Random Image
    width, height = 256, 256
    random_pixels = np.random.randint(0, 256, (height, width), dtype=np.uint8)
    image = QImage(random_pixels, width, height, QImage.Format.Format_Grayscale8)
    main_widget.set_image(image)
    main_widget.set_image_from_array(random_pixels)

    sys.exit(app.exec())
