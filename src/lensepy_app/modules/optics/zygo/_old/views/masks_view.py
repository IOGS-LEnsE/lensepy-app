# -*- coding: utf-8 -*-
"""*masks_view.py* file.

./views/masks_view.py contains MasksView class to create masks.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os, time
import numpy as np
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from lensepy.images.conversion import resize_image_ratio, array_to_qimage
from PyQt6.QtWidgets import (
    QDialog, QLabel,
    QVBoxLayout,
    QApplication
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QKeyEvent, QMouseEvent, QResizeEvent


WIDTH_MARGIN = 30
HEIGHT_MARGIN = 80


class MasksView(QDialog):
    """
    A dialog for selecting a mask on an image.

    This dialog allows the user to define a region on an image. Points are selected
    by clicking on the image, and a mask is generated based on these points.

    See Also
    --------
    CircularMask, RectangularMask, PolygonalMask

    Example
    -------
    image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    dialog = CircularMaskSelection(image)
    dialog.exec()
    """

    def __init__(self, pixel: np.ndarray, mask_type: str, help_text: str = 'Help') -> None:
        """
        Initializes the MasksView dialog.
        :param pixel: The image on which the mask will be drawn.
        :param help_text: Text displayed to help the user.
        """
        super().__init__()
        # Data of the class
        self.image = np.array(pixel.copy(), dtype='uint8')
        self.type = mask_type
        # Initialize layout and image attributes
        self.layout = QVBoxLayout()

        # Create a QLabel to display help
        self.help = QLabel(help_text)
        self.help.setStyleSheet(styleH2)
        self.help.setFixedHeight(50)
        # Create a QLabel to display the image
        self.label = QLabel()

        # Add the label to the layout
        self.layout.addWidget(self.help, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        # Convert image to QImage and QPixmap for display and adjust to maximum size of the screen
        if self.image.shape[1] > self.width() or self.image.shape[0] > self.height():
            new_h = self.height()-HEIGHT_MARGIN
            new_w = self.width()-WIDTH_MARGIN
            image_to_display = resize_image_ratio(self.image, new_h, new_w)
        else:
            image_to_display = self.image
        self.qimage = array_to_qimage(image_to_display)
        self.pixmap = QPixmap.fromImage(self.qimage)
        self.label.setPixmap(self.pixmap)

        self.ratio = self.image.shape[1] / image_to_display.shape[1]

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        self.setWindowState(Qt.WindowState.WindowMaximized)
        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_circle

    def resizeEvent(self, a0: QResizeEvent) -> None:
        # Convert image to QImage and QPixmap for display and adjust to maximum size of the screen
        if self.image.shape[1] > self.width() or self.image.shape[0] > self.height():
            new_h = self.height()-HEIGHT_MARGIN
            new_w = self.width()-WIDTH_MARGIN
            image_to_display = resize_image_ratio(self.image, new_h, new_w)
        else:
            image_to_display = self.image
        self.qimage = array_to_qimage(image_to_display)
        self.pixmap = QPixmap.fromImage(self.qimage)
        self.label.setPixmap(self.pixmap)
        self.ratio = self.image.shape[1] / image_to_display.shape[1]
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.
        :param event:
        :return: The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.accept()

    def get_points_circle(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the circle.
        :param event: The mouse event.
        """
        # Enable drawing points and limit to three points
        self.can_draw = True
        # Get the position of the mouse click
        pos = event.pos()
        # Testing mask type
        if self.can_draw:
            match self.type:
                case 'circular':
                    if len(self.points) < 3:
                        # Add the point to the list of polygon points
                        self.points.append((pos.x(), pos.y()))
                        # Draw the point on the image
                        self.draw_point(pos.x(), pos.y())
                        # Test if the figure is ending
                        if len(self.points) == 3:
                            self.can_draw = False

                case 'rectangular':
                    if len(self.points) < 2:
                        self.points.append((pos.x(), pos.y()))
                        self.draw_point(pos.x(), pos.y())
                        # Test if the figure is ending
                        if len(self.points) == 2:
                            self.can_draw = False
                case 'polygon':
                    limit = np.int32(10 * self.ratio)  # px
                    self.points.append((pos.x(), pos.y()))
                    # Display a red circle for the end of the polygon
                    if len(self.points) == 1:
                        combined_pixmap = self.pixmap
                        painter = QPainter(combined_pixmap)
                        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                        pen = QPen(Qt.GlobalColor.red, 2)
                        painter.setPen(pen)
                        painter.drawEllipse(QPoint(pos.x(), pos.y()), limit, limit)
                        painter.end()
                        self.label.setPixmap(combined_pixmap)

                    self.draw_point(pos.x(), pos.y())
                    dx = self.points[-1][0] - self.points[0][0]
                    dy = self.points[-1][1] - self.points[0][1]
                    dist = dx ** 2 + dy ** 2
                    # Test if the figure is ending
                    if len(self.points) > 1 and dist < limit ** 2:
                        self.can_draw = False

        # When figure ended
        if self.can_draw is False:
            match self.type:
                case 'circular':
                    self.draw_circle()
                case 'rectangular':
                    self.draw_rectangle()
                case 'polygon':
                    self.draw_polygon()

            QTimer.singleShot(1000, self.accept)

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.
        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        """
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.blue, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Combine the point layer pixmap with the original image pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

    def find_circle_center(self, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int]:
        """
        Finds the center of a circle given three points.

        Parameters
        ----------
        x0, y0 : int
            Coordinates of the first point.
        x1, y1 : int
            Coordinates of the second point.
        x2, y2 : int
            Coordinates of the third point.

        Returns
        -------
        tuple
            Coordinates of the circle center (x, y).
        """
        # Calculate midpoints and perpendicular bisectors
        mid_x_01 = (x0 + x1) / 2
        mid_y_01 = (y0 + y1) / 2
        mid_x_02 = (x0 + x2) / 2
        mid_y_02 = (y0 + y2) / 2

        if x0 == x1:
            slope_perp_01 = None
            intercept_perp_01 = mid_x_01
        else:
            slope_perp_01 = -1 / ((y1 - y0) / (x1 - x0))
            intercept_perp_01 = mid_y_01 - slope_perp_01 * mid_x_01

        if x0 == x2:
            slope_perp_02 = None
            intercept_perp_02 = mid_x_02
        else:
            slope_perp_02 = -1 / ((y2 - y0) / (x2 - x0))
            intercept_perp_02 = mid_y_02 - slope_perp_02 * mid_x_02

        # Calculate circle center coordinates
        if slope_perp_01 is None or slope_perp_02 is None:
            if slope_perp_01 is None:
                X = mid_x_01
                Y = slope_perp_02 * X + intercept_perp_02
            else:
                X = mid_x_02
                Y = slope_perp_01 * X + intercept_perp_01
        else:
            X = (intercept_perp_02 - intercept_perp_01) / \
                (slope_perp_01 - slope_perp_02)
            Y = slope_perp_01 * X + intercept_perp_01

        return X, Y

    def draw_circle(self) -> None:
        """
        Draws a circle based on the points selected by the user.
        """
        try:
            # Get the last three points selected by the user
            x0, y0 = self.points[-3]
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]

            # Find the center of the circle and radius
            x_center, y_center = self.find_circle_center(
                x0, y0, x1, y1, x2, y2)
            x_center = int(x_center)
            y_center = int(y_center)
            radius = int(np.sqrt((x_center - x0) ** 2 + (y_center - y0) ** 2))

            # Draw the circle on the pixmap
            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(Qt.GlobalColor.blue, 2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x_center, y_center), radius, radius)
            painter.end()

            # Combine the circle with the point layer pixmap
            combined_pixmap = self.pixmap.copy()
            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, self.point_layer)
            painter.end()

            # Update the label pixmap to show the combined image
            self.label.setPixmap(combined_pixmap)

            # Update mask
            self.mask = self.create_circular_mask(x_center * self.ratio, y_center * self.ratio, radius * self.ratio)

        except Exception as e:
            print(f'Exception - circle_mask_draw {e}')

    def create_circular_mask(self, x_center: int, y_center: int, radius: int) -> np.ndarray:
        """
        Creates a circular mask.

        Parameters
        ----------
        x_center : int
            The x-coordinate of the circle center.
        y_center : int
            The y-coordinate of the circle center.
        radius : int
            The radius of the circle.

        Returns
        -------
        np.ndarray
            The binary mask with the circular region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create grid of coordinates
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]

        # Calculate distance from center
        dist_from_center = np.sqrt((x - x_center) ** 2 + (y - y_center) ** 2)

        # Set mask values inside the circle to 1
        mask[dist_from_center <= radius] = 1
        mask = mask > 0.5
        return mask

    def draw_rectangle(self) -> None:
        """
        Draws a rectangle based on the points selected by the user.
        """
        # Get the two points defining the rectangle
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

        # Draw the rectangle on the pixmap
        painter = QPainter(self.pixmap)
        pen = QPen(Qt.GlobalColor.blue, 2)
        painter.setPen(pen)
        painter.drawRect(x1, y1, (x2-x1), (y2-y1))
        painter.end()

        # Combine the rectangle with the point layer pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_rectangular_mask(x1, y1, x2, y2)

    def create_rectangular_mask(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """
        Creates a rectangular mask.

        Parameters
        ----------
        x1, y1 : int
            Coordinates of the top-left corner of the rectangle.
        x2, y2 : int
            Coordinates of the bottom-right corner of the rectangle.

        Returns
        -------
        np.ndarray
            The binary mask with the rectangular region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)
        # Invert y1,y2 or/and x1,x2 if not in ascending order
        if y2 < y1:
            y1, y2 = y2, y1
        if x2 < x1:
            x1, x2 = x2, x1
        # Set mask values inside the rectangle to 1
        mask[int(y1*self.ratio):int(y2*self.ratio), int(x1*self.ratio):int(x2*self.ratio)] = 1
        mask = mask > 0.5
        return mask

    def draw_polygon(self) -> None:
        """
        Draws a polygon based on the points selected by the user and updates the mask.

        Draws a polygon using the points stored in `self.points` and updates the displayed image
        (`self.label`) and the mask (`self.mask`) accordingly.

        Notes
        -----
        This method assumes `QPoint` and `QPixmap` are correctly imported from PyQt6.QtCore and PyQt6.QtGui,
        respectively. Ensure `self.points`, `self.pixmap`, `self.point_layer`, `self.label`, and `self.mask`
        are initialized correctly before calling this method.

        """
        # Convert points to QPoint objects
        points = [QPoint(self.points[i][0], self.points[i][1])
                  for i in range(len(self.points))]

        # Draw polygon on the main pixmap
        painter = QPainter(self.pixmap)
        pen = QPen(Qt.GlobalColor.blue, 2)
        painter.setPen(pen)
        painter.drawPolygon(points)
        painter.end()

        # Update combined pixmap to show polygon and points
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update label with the combined pixmap
        self.label.setPixmap(combined_pixmap)

        # Update mask with the newly drawn polygon
        self.mask = self.create_polygonal_mask()

    def create_polygonal_mask(self) -> np.ndarray:
        """
        Creates a polygonal mask based on the points selected by the user.

        Returns
        -------
        np.ndarray
            The binary mask with the polygonal region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create a list of vertices for the polygon
        vertices = []
        for point in self.points:
            # Swap x and y for numpy indexing
            vertices.append((int(point[0]*self.ratio), int(point[1]*self.ratio)))

        # Convert the list of vertices to numpy array format
        vertices = np.array([vertices], dtype=np.int32)

        # Fill the polygon region in the mask with 1
        cv2.fillPoly(mask, vertices, 1)
        mask = mask > 0.5
        return mask



if __name__ == '__main__':
    app = QApplication(sys.argv)

    image = np.random.randint(0, 255, (2000, 1000), dtype=np.uint8)
    try:
        dialog = MasksView(image, 'polygon')
        result = dialog.exec()
    except Exception as e:
        print(e)

    sys.exit(app.exec())