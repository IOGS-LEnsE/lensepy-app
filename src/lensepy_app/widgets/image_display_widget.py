"""
image_display_widget.py
=======================

PyQt6 widget for displaying images from numpy arrays in a QGraphicsView.
Supports both grayscale and RGB images, with optional text overlay and
customizable bits depth.

Features
--------

- Supports grayscale and RGB images
- Converts higher bit-depth images to 8-bit for display
- Optional overlay text
- Maintains aspect ratio in QGraphicsView
- Customizable background color

Usage Example
-------------

.. code-block:: python

    import sys
    import numpy as np
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())


Author : Julien VILLEMEJANE / LEnsE - IOGS
Date   : 2025-10-09
"""

import numpy as np
from PyQt6 import sip

from lensepy.css import *
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsView,
    QVBoxLayout, QGraphicsTextItem, QWidget, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsRectItem
)


class ImageDisplayWidget(QWidget):
    """Widget d'affichage d'image depuis un array NumPy, avec ajustement automatique à la vue."""

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(None)
        self.parent = parent
        self.bits_depth = 8
        self.zoom = zoom
        self.pixmap_item = None
        self.text_item = None

        # --- Scene & View ---
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() |
                                 QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene.setBackgroundBrush(QColor(bg_color))

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        """Affiche une image NumPy (grayscale ou RGB)."""
        if pixels_array is None:
            return
        if sip.isdeleted(self) or sip.isdeleted(self.scene):
            return
        # Delete only pixmap and text.
        if self.pixmap_item:
            self.scene.removeItem(self.pixmap_item)
            self.pixmap_item = None
        if self.text_item:
            self.scene.removeItem(self.text_item)
            self.text_item = None

        qimage = self._convert_array_to_qimage(pixels_array)
        if qimage is None:
            return

        # Crée le pixmap et l'ajoute à la scène
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Ajoute le texte (facultatif)
        if text:
            font = QFont('Arial', 12)
            self.text_item = QGraphicsTextItem(text)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setPos(5, pixmap.height() - 25)
            self.scene.addItem(self.text_item)

        # Si un point était sélectionné, on redessine la croix
        if hasattr(self, 'selected_point') and self.selected_point:
            self._draw_crosshair(self.selected_point.x(), self.selected_point.y())

        # Ajustement automatique
        QTimer.singleShot(0, self._update_view_fit)

    def set_bits_depth(self, value_depth: int):
        """Définit la profondeur de bits des pixels."""
        self.bits_depth = value_depth

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _convert_array_to_qimage(self, pixels: np.ndarray) -> QImage | None:
        """Convertit un tableau numpy en QImage compatible avec PyQt."""
        pixels = np.ascontiguousarray(pixels)
        if pixels.ndim == 2:
            # Grayscale
            if self.bits_depth > 8:
                scale = 2 ** (self.bits_depth - 8)
                pixels = (pixels / scale).astype(np.uint8)
            else:
                pixels = pixels.astype(np.uint8)
            h, w = pixels.shape
            return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_Grayscale8)

        elif pixels.ndim == 3:
            h, w, c = pixels.shape
            if c == 3:
                pixels = pixels.astype(np.uint8)
                return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_RGB888)
            elif c == 4:    # Remove alpha
                pixels = pixels[:,:,0:2]
                pixels = pixels.astype(np.uint8)
                return QImage(pixels.data, w, h, pixels.strides[0], QImage.Format.Format_RGB888)
            else:
                raise ValueError(f"Unsupported number of channels: {c}")

        else:
            raise ValueError(f"Unsupported image shape: {pixels.shape}")

    def _update_view_fit(self):
        """
        Adjust the view to the image size, without scrollbars,
        and without enlarging images that are smaller than the view.
        """
        if not self.pixmap_item:
            return

        view_size = self.view.viewport().size()
        img_size = self.scene.sceneRect().size()

        # Readjust image if bigger than the window.
        if img_size.width() > view_size.width() or img_size.height() > view_size.height():
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # No adjustment if smaller than the window.
            self.view.resetTransform()
            self.view.centerOn(self.pixmap_item)

    def resizeEvent(self, event):
        """Ajuste l'image automatiquement lors du redimensionnement."""
        super().resizeEvent(event)
        self._update_view_fit()


class ImageDisplayWithPoints(ImageDisplayWidget):

    def __init__(self, parent=None, bg_color='white', zoom=True):
        super().__init__(parent, bg_color, zoom)
        self.points = []
        self.point_items = []
        self.point_radius = 4
        self.point_color = QColor("red")
        self.pen = QPen(self.point_color)
        self.pen.setWidth(2)
        self.brush = self.point_color

    # ---------------------------------------------------------------
    # Public method to set or update the points
    # ---------------------------------------------------------------
    def set_points(self, points: list[tuple[int, int]]):
        """
        points: list of (x, y)
        """
        self.points = points
        self._draw_points()

    # ---------------------------------------------------------------
    # Override to redraw points after image refresh
    # ---------------------------------------------------------------
    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        super().set_image_from_array(pixels_array, text)
        self._draw_points()

    # ---------------------------------------------------------------
    # Internal drawing utility
    # ---------------------------------------------------------------
    def _draw_points(self):
        """Draws red circles at the given coordinates."""
        # Clear old point items
        for item in self.point_items:
            self.scene.removeItem(item)
        self.point_items = []

        if not hasattr(self, "pixmap_item") or self.pixmap_item is None:
            return

        for (x, y) in self.points:
            radius = self.point_radius
            ellipse = self.scene.addEllipse(
                x - radius, y - radius,
                radius * 2, radius * 2,
                self.pen, self.brush
            )
            ellipse.setZValue(10)  # draw on top
            self.point_items.append(ellipse)



class ImageDisplayWithCrosshair(ImageDisplayWidget):
    """ImageDisplayWidget avec sélection d’un point et affichage d’un réticule (crosshair)."""

    point_selected = pyqtSignal(float, float)

    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent, bg_color, zoom)

        # Couleurs et styles du crosshair
        self.crosshair_pen_h = QPen(QColor(BLUE_IOGS), 2, Qt.PenStyle.SolidLine)
        self.crosshair_pen_v = QPen(QColor(ORANGE_IOGS), 2, Qt.PenStyle.DashLine)

        # Lignes du crosshair
        self.h_line = None
        self.v_line = None

        # État du crosshair
        self.selected_point = None
        self.dragging = False

        # Active la détection de clics et mouvements sur la scène
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self._update_point(event)
            elif event.type() == event.Type.MouseMove and self.dragging:
                self._update_point(event)
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Crosshair logic
    # ------------------------------------------------------------------
    def _update_point(self, event):
        """Met à jour la position du point sélectionné lors du clic ou du drag."""
        pos = self.view.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        self.selected_point = QPointF(x, y)
        self._draw_crosshair(x, y)
        self.point_selected.emit(x, y)

    def _draw_crosshair(self, x, y):
        """Dessine ou déplace les lignes du crosshair."""
        scene_rect = self.scene.sceneRect()

        # Si les lignes n'existent pas ou ont été supprimées, on les recrée
        if not self.h_line or self.h_line.scene() is None:
            self.h_line = QGraphicsLineItem()
            self.h_line.setPen(self.crosshair_pen_h)
            self.scene.addItem(self.h_line)

        if not self.v_line or self.v_line.scene() is None:
            self.v_line = QGraphicsLineItem()
            self.v_line.setPen(self.crosshair_pen_v)
            self.scene.addItem(self.v_line)

        # Met à jour la position des lignes
        self.h_line.setLine(scene_rect.left(), y, scene_rect.right(), y)
        self.v_line.setLine(x, scene_rect.top(), x, scene_rect.bottom())

    def set_image_from_array(self, pixels_array: np.ndarray, text: str = ''):
        """Affiche une image NumPy et conserve le crosshair existant."""
        # Sauvegarde la position actuelle du crosshair
        saved_point = self.selected_point

        # Appel au parent (efface et réaffiche l’image)
        super().set_image_from_array(pixels_array, text)

        # --- Correction : les items ont été détruits, on oublie les anciens pointeurs Python ---
        self.h_line = None
        self.v_line = None

        # Réaffiche le crosshair si un point avait été sélectionné
        if saved_point is not None:
            x, y = saved_point.x(), saved_point.y()
            self.selected_point = saved_point
            self._draw_crosshair(x, y)


class RectangleDisplayWidget(ImageDisplayWidget):
    """Widget permettant de dessiner deux points et un rectangle associé,
    avec option d'activation/désactivation et dessin programmatique.
    """
    rectangle_changed = pyqtSignal(list)

    def __init__(self, parent=None, bg_color='white', zoom=True):
        super().__init__(parent, bg_color, zoom)

        # Drawing state
        self.draw_enabled = True        # To activate the drawing area
        self.drawing = False

        # Forms
        self.points = []                # QPointF List
        self.point_items = []           # QGraphicsEllipseItem
        self.rect_item = None           # QGraphicsRectItem

        # Drawing details
        self.point_radius = 4
        self.point_color = QColor("red")
        self.rect_color = QColor("blue")

        # Mouse event
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    # Manage mouse event
    def eventFilter(self, source, event):
        if not self.draw_enabled:
            return super().eventFilter(source, event)

        if source is self.view.viewport():
            # First click to start rectangle
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                pos = self.view.mapToScene(event.pos())
                self._on_click(pos)
                return True

            # Mouse event - real time detection
            elif event.type() == event.Type.MouseMove and self.drawing and len(self.points) == 1:
                pos = self.view.mapToScene(event.pos())
                self._update_temp_rectangle(pos)
                return True

        return super().eventFilter(source, event)

    # Drawing
    def _on_click(self, pos: QPointF):
        """Manage points acquisition (2 for a rectangle)."""
        if len(self.points) == 0:
            self._clear_shapes()
            self.drawing = True
            self.points.append(pos)
            self.point_items.append(self._draw_point(pos))
            self.rect_item = self.scene.addRect(QRectF(pos, pos), QPen(self.rect_color, 2))
            self.rect_item.setZValue(9)

        elif len(self.points) == 1:
            self.drawing = False
            self.points.append(pos)
            self.point_items.append(self._draw_point(pos))
            self._finalize_rectangle()

        else:
            # Nouveau cycle
            self._clear_shapes()
            self._on_click(pos)

    def _update_temp_rectangle(self, pos: QPointF):
        """Update rectangle during mouse movement."""
        if self.rect_item and len(self.points) == 1:
            p1 = self.points[0]
            rect = QRectF(p1, pos).normalized()
            self.rect_item.setRect(rect)

    def _finalize_rectangle(self):
        """Final size of the rectangle."""
        if len(self.points) == 2 and self.rect_item:
            rect = QRectF(self.points[0], self.points[1]).normalized()
            self.rect_item.setRect(rect)
            self.rectangle_changed.emit([self.points[0].x(), self.points[0].y(),
                                         self.points[1].x(), self.points[1].y()])

    # ------------------------------------------------------------------
    # Dessin manuel depuis le code
    # ------------------------------------------------------------------
    def draw_rectangle(self, coords: list):
        """
        Dessine un rectangle et ses coins directement depuis le code,
        sans interaction souris.
        """
        self._clear_shapes()
        p1, p2 = QPointF(coords[0], coords[1]), QPointF(coords[2], coords[3])
        self.points = [p1, p2]
        self.point_items = [self._draw_point(p1), self._draw_point(p2)]
        rect = QRectF(p1, p2).normalized()
        pen = QPen(self.rect_color)
        pen.setWidth(2)
        self.rect_item = self.scene.addRect(rect, pen)
        self.rect_item.setZValue(9)
        for p in self.point_items:
            p.setZValue(10)

    def clear_rect(self):
        self._clear_shapes()

    # Drawing cleaning
    def _draw_point(self, pos: QPointF):
        """Draw a red point at a specific position."""
        r = self.point_radius
        ellipse = QGraphicsEllipseItem(pos.x() - r, pos.y() - r, 2 * r, 2 * r)
        pen = QPen(self.point_color)
        pen.setWidth(2)
        ellipse.setPen(pen)
        ellipse.setBrush(self.point_color)
        ellipse.setZValue(10)
        self.scene.addItem(ellipse)
        return ellipse

    def _clear_shapes(self):
        """Delete all the shapes."""
        for item in self.point_items:
            self.scene.removeItem(item)
        self.point_items.clear()
        self.points.clear()
        if self.rect_item:
            self.scene.removeItem(self.rect_item)
            self.rect_item = None
        self.drawing = False

    # Persistent elements
    def set_image_from_array(self, pixels_array, text=''):
        """Display a new image without removing existing rectangle."""
        if pixels_array is None:
            return
        if sip.isdeleted(self) or sip.isdeleted(self.scene):
            return

        qimage = self._convert_array_to_qimage(pixels_array)
        if qimage is None:
            return
        pixmap = QPixmap.fromImage(qimage)

        if self.pixmap_item is not None:
            self.pixmap_item.setPixmap(pixmap)
        else:
            self.pixmap_item = self.scene.addPixmap(pixmap)

        # 🔥 Important : toujours mettre à jour !
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Texte optionnel (affiché une seule fois)
        if text and self.text_item is None:
            from PyQt6.QtGui import QFont
            from PyQt6.QtWidgets import QGraphicsTextItem
            font = QFont('Arial', 12)
            self.text_item = QGraphicsTextItem(text)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setPos(5, pixmap.height() - 25)
            self.scene.addItem(self.text_item)

        # Ajustement initial
        if not hasattr(self, "_fit_done") or not self._fit_done:
            QTimer.singleShot(0, self._update_view_fit)
            self._fit_done = True

    def set_enabled(self, value=True):
        self.draw_enabled = value
        self._clear_shapes()




if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = ImageDisplayWidget(bg_color='white')

    # Create a test RGB image 256x256
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    widget.set_image_from_array(test_image, text="Test Image")
    widget.show()
    sys.exit(app.exec())