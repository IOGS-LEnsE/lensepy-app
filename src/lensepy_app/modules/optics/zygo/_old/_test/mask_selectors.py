# -*- coding: utf-8 -*-
"""
File: zygo_lab_app.py

This file contains the definition of the ZygoLabApp class, which serves as the main interface 
for a photonics laboratory in both first-year and second-year engineering courses.

First-year subject: http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf
Second-year subject: https://lense.institutoptique.fr/s8-aberrations/

Development details for this interface:
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QKeyEvent, QMouseEvent
import numpy as np
import cv2


class CircularMaskSelection(QDialog):
    """
    A dialog for selecting a circular mask on an image.

    This dialog allows the user to define a circular region on an image. Points are selected 
    by clicking on the image, and a circular mask is generated based on these points.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_circle(event)
        Captures points clicked by the user to define the circle.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    find_circle_center(x0, y0, x1, y1, x2, y2)
        Finds the center of a circle given three points.
    draw_circle()
        Draws a circle based on the points selected by the user.
    create_circular_mask(x_center, y_center, radius)
        Creates a circular mask.
    close_window()
        Closes the dialog window.

    See Also
    --------
    RectangularMaskSelection, PolygonalMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Examples
    --------
    >>> image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    >>> dialog = CircularMaskSelection(image)
    >>> dialog.exec()
    """

    def __init__(self, image: np.ndarray) -> None:
        """
        Initializes the CircularMaskSelection dialog.

        Parameters
        ----------
        image : np.ndarray
            The image on which the mask will be drawn.
        """
        super().__init__()

        # Initialize layout and image attributes
        self.layout = QVBoxLayout()
        self.image = image

        # Convert image to QImage and QPixmap for display
        self.qimage = QImage(
            self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_circle

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.close_window()

    def get_points_circle(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the circle.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points and limit to three points
        self.can_draw = True
        if self.can_draw and len(self.points) < 3:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 3:
                self.draw_circle()
                self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.red, point_size)
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
            radius = int(np.sqrt((x_center-x0)**2+(y_center-y0)**2))

            # Draw the circle on the pixmap
            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(255, 0, 0), 2)
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
            self.mask = self.create_circular_mask(x_center, y_center, radius)
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
            The binary mask with the circular region set to 1.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create grid of coordinates
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]

        # Calculate distance from center
        dist_from_center = np.sqrt((x - x_center)**2 + (y - y_center)**2)

        # Set mask values inside the circle to 1
        mask[dist_from_center <= radius] = 1

        return mask

    def close_window(self) -> None:
        """
        Closes the dialog window.
        """
        self.close()


class RectangularMaskSelection(QDialog):
    """
    A dialog for selecting a rectangular mask on an image.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user defining the rectangle.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_rectangle(event)
        Captures points clicked by the user to define the rectangle.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    draw_rectangle()
        Draws a rectangle based on the points selected by the user.
    create_rectangular_mask(x1, y1, x2, y2)
        Creates a rectangular mask.
    close_window()
        Closes the dialog window.

    See Also
    --------
    CircularMaskSelection, PolygonalMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Examples
    --------
    >>> image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    >>> dialog = RectangularMaskSelection(image)
    >>> dialog.exec()
    """

    def __init__(self, image: np.ndarray) -> None:
        """
        Initializes the RectangularMaskSelection dialog.

        Parameters
        ----------
        image : np.ndarray
            The image on which the mask will be drawn.
        """
        super().__init__()

        # Initialize layout and image attributes
        self.layout = QVBoxLayout()
        self.image = image

        # Convert image to QImage and QPixmap for display
        self.qimage = QImage(
            self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_rectangle

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.close_window()

    def get_points_rectangle(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the rectangle.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points and limit to two points
        self.can_draw = True
        if self.can_draw and len(self.points) < 2:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 2:
                self.draw_rectangle()
                self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.red, point_size)
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

    def draw_rectangle(self) -> None:
        """
        Draws a rectangle based on the points selected by the user.
        """
        # Get the two points defining the rectangle
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

        # Draw the rectangle on the pixmap
        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
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
            The binary mask with the rectangular region set to 1.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Set mask values inside the rectangle to 1
        mask[y1:y2, x1:x2] = 1

        return mask

    def close_window(self) -> None:
        """
        Closes the dialog window.
        """
        self.close()


class PolygonalMaskSelection(QDialog):
    """
    A dialog for selecting a polygonal mask on an image.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user defining the polygon.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_polygon(event)
        Captures points clicked by the user to define the polygon.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    draw_polygon()
        Draws a polygon based on the points selected by the user.
    create_polygonal_mask()
        Creates a polygonal mask based on the points selected.
    close_window()
        Closes the dialog window.

    See Also
    --------
    CircularMaskSelection, RectangularMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Examples
    --------
    >>> image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    >>> dialog = PolygonalMaskSelection(image)
    >>> dialog.exec()
    """

    def __init__(self, image: np.ndarray) -> None:
        """
        Initializes the PolygonalMaskSelection dialog.

        Parameters
        ----------
        image : np.ndarray
            The image on which the mask will be drawn.
        """
        super().__init__()

        # Initialize layout and image attributes
        self.layout = QVBoxLayout()
        self.image = image

        # Convert image to QImage and QPixmap for display
        self.qimage = QImage(
            self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_polygon

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.close_window()

    def get_points_polygon(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the polygon.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points
        self.can_draw = True
        limit = 10  # px

        # Get the position of the mouse click
        pos = event.pos()

        # Add the point to the list of polygon points
        self.points.append((pos.x(), pos.y()))

        # Draw the point on the image
        self.draw_point(pos.x(), pos.y())

        # Draw the polygon if the user has selected more than one point and the last point is close to the first point
        if len(self.points) > 1 and (self.points[-1][0] - self.points[0][0])**2+(self.points[-1][1] - self.points[0][1])**2 < limit**2:
            self.draw_polygon()
            self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.red, point_size)
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
        pen = QPen(QColor(255, 0, 0), 2)
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
            The binary mask with the polygonal region set to 1.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create a list of vertices for the polygon
        vertices = []
        for point in self.points:
            # Swap x and y for numpy indexing
            vertices.append((point[1], point[0]))

        # Convert the list of vertices to numpy array format
        vertices = np.array([vertices], dtype=np.int32)

        # Fill the polygon region in the mask with 1
        cv2.fillPoly(mask, vertices, 1)

        return mask

    def close_window(self) -> None:
        """
        Closes the dialog window.
        """
        self.close()


# %% Example
if __name__ == '__main__':
    app = QApplication(sys.argv)
    image = np.random.randint(0, 255, (700, 700))
    main = CircularMaskSelection(image)
    main.show()
    sys.exit(app.exec())
