import numpy as np
from lensepy_app import *
from lensepy_app.appli import *

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QRectF, QPoint
import pyqtgraph as pg





class ImageCrossSections(ModuleWidget):
    """
    Widget PyQtGraph displaying :

           title      slice X
                 ┌───────────────┐
                 │               │
         slice Y │    image      │
                 │               │
                 └───────────────┘

    :param data: 2D array.
    :param cmap: Colormap for image. Optional.
        Examples : 'viridis', 'plasma', 'inferno', 'magma', etc.
    :param title: Title of the widget. Optional.
    """

    def __init__(self, data=None, cmap="viridis", parent=None, title=''):
        super().__init__(parent=parent)

        self.data = None
        self.title = title

        self.nx = 0
        self.ny = 0

        self.x_index = 0
        self.y_index = 0
        self.x_axis = None
        self.y_axis = None
        self.x_label = 'X'
        self.y_label = 'Y'
        self.x_value_label = ''
        self.y_value_label = ''

        self.cmap = self._get_colormap(cmap)

        self._build_ui()

        if data is not None:
            self.set_data(data)

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        # X slice
        self.plot_x = pg.PlotWidget()
        self.plot_x.setBackground(IMAGE_BG[self.global_theme])
        self.plot_x.showGrid(x=True, y=True, alpha=0.15)
        self.plot_x.setLabel("bottom", self.x_label)
        self.plot_x.setLabel("left", self.x_value_label)
        self.curve_x = self.plot_x.plot(
            pen=pg.mkPen("b", width=2)
        )

        # Y slice
        self.plot_y = pg.PlotWidget()
        self.plot_y.setBackground(IMAGE_BG[self.global_theme])
        self.plot_y.showGrid(x=True, y=True, alpha=0.15)
        self.plot_y.setLabel("bottom", self.y_value_label)
        self.plot_y.setLabel("left", self.y_label)
        self.curve_y = self.plot_y.plot(
            pen=pg.mkPen("r", width=2)
        )

        # Image plot
        self.plot_image = pg.PlotWidget()
        self.plot_image.setBackground(IMAGE_BG[self.global_theme])
        self.plot_image.showGrid(x=False, y=False, alpha=0.15)
        self.plot_image.setLabel("bottom", self.x_label)
        self.plot_image.setLabel("left", self.y_label)

        self.plot_image.setAspectLocked(True)

        self.image_item = pg.ImageItem()
        self.image_item.setLookupTable(
            self.cmap.getLookupTable(0.0,1.0,256)
        )
        self.plot_image.addItem(self.image_item)

        # Slice line
        self.vline = pg.InfiniteLine(
            angle=90, movable=False,
            pen=pg.mkPen("r", width=1)
        )
        self.hline = pg.InfiniteLine(
            angle=0, movable=False,
            pen=pg.mkPen("b", width=1)
        )

        self.plot_image.addItem(self.vline)
        self.plot_image.addItem(self.hline)

        layout.addWidget(self.plot_x, 0, 1)
        layout.addWidget(self.plot_y, 1, 0)
        layout.addWidget(self.plot_image, 1, 1)
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label, 0, 0)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)

        # Sync of axis
        self.plot_x.setXLink(self.plot_image)
        self.plot_y.setYLink(self.plot_image)
        # Mouse click management
        self.plot_image.scene().sigMouseClicked.connect(
            self._mouse_clicked
        )

    def set_title(self, title):
        self.title = title
        self.title_label.setText(title)

    @staticmethod
    def _get_colormap(cmap):
        if isinstance(cmap, pg.ColorMap):
            return cmap
        # Colormaps PyQtGraph intégrées
        try:
            return pg.colormap.get(cmap)
        except Exception:
            raise ValueError(f"Colormap inconnue : {cmap}")

    def set_data(self, data):
        """Update data to display."""
        data = np.asarray(data)
        if data.ndim != 2:
            raise ValueError("data doit être un tableau 2D")
        self.data = data
        self.ny, self.nx = data.shape

        # Image center
        self.x_index = self.nx // 2
        self.y_index = self.ny // 2

        self.image_item.setImage(self.data, autoLevels=True)
        self.image_item.setLookupTable(
            self.cmap.getLookupTable(0.0, 1.0, 256)
        )
        self.x_range = (0, self.nx)
        self.y_range = (0, self.ny)
        self._set_range()

        self.vline.setValue(self.x_index)
        self.hline.setValue(self.y_index)

        self._update_profiles()
        self._update_slice_lines()

    def _set_range(self):
        self.plot_image.setXRange(
            self.x_range[0], self.x_range[1], padding=0
        )
        self.plot_image.setYRange(
            self.y_range[0], self.y_range[1], padding=0
        )

    def set_x_axis(self, x_axis, label="X", value_label=""):
        self.x_label = label
        self.x_value_label = value_label

        self.x_axis = x_axis

        self.plot_image.setLabel("bottom", self.x_label)
        self.plot_x.setLabel("bottom", self.x_label)
        self.plot_x.setLabel("left", self.x_value_label)

        self._update_coordinates()

    def set_y_axis(self, y_axis, label="Y", value_label=""):
        self.y_label = label
        self.y_value_label = value_label

        self.y_axis = y_axis

        self.plot_image.setLabel("left", self.y_label)
        self.plot_y.setLabel("bottom", self.y_value_label)
        self.plot_y.setLabel("left", self.y_label)

        self._update_coordinates()

    def _update_profiles(self):
        if self.data is None:
            return

        x = (self.x_axis if self.x_axis is not None
             else np.arange(self.nx))
        y = (self.y_axis if self.y_axis is not None
             else np.arange(self.ny))

        self.curve_x.setData(x, self.data[self.y_index, :])
        self.curve_y.setData(self.data[:, self.x_index], y)

    def _mouse_clicked(self, event):

        if self.data is None:
            return
        if event.button() != 1: # Left click only
            return

        # Click in the viewbox
        if not self.plot_image.sceneBoundingRect().contains(event.scenePos()):
            return

        # Convert coordinate from scene to image
        mouse_point = self.plot_image.getPlotItem().vb.mapSceneToView(
            event.scenePos()
        )
        x = mouse_point.x()
        y = mouse_point.y()

        x_axis = (
            self.x_axis if self.x_axis is not None
            else np.arange(self.nx)
        )
        y_axis = (
            self.y_axis if self.y_axis is not None
            else np.arange(self.ny)
        )

        # Retrouver les indices des pixels les plus proches
        self.x_index = int(np.argmin(np.abs(x_axis - x)))
        self.y_index = int(np.argmin(np.abs(y_axis - y)))

        self._update_slice_lines()
        self._update_profiles()

    def set_color_map(self, cmap):
        """Change colormap of the 2D surface."""
        self.cmap = self._get_colormap(cmap)
        self.image_item.setLookupTable(
            self.cmap.getLookupTable(0.0, 1.0, 256)
        )

    def _update_coordinates(self):
        if self.data is None:
            return

        # Coordonnées par défaut : indices des pixels
        x = (self.x_axis if self.x_axis is not None
             else np.arange(self.nx, dtype=float))
        y = (self.y_axis if self.y_axis is not None
             else np.arange(self.ny, dtype=float))

        if len(x) != self.nx or len(y) != self.ny:
            raise ValueError("Les axes doivent correspondre aux dimensions de l'image")

        if self.nx < 2 or self.ny < 2:
            raise ValueError("L'image doit avoir au moins 2 pixels par dimension")

        dx = x[1] - x[0]
        dy = y[1] - y[0]

        if not np.allclose(np.diff(x), dx) or not np.allclose(np.diff(y), dy):
            raise ValueError("Cette méthode nécessite des axes régulièrement espacés")

        # Positionner l'image dans le repère physique
        self.image_item.setRect(
            QRectF(x[0] - dx / 2, y[0] - dy / 2,
                self.nx * dx, self.ny * dy,
            )
        )

        # Plages visibles
        self.x_range = (x[0] - dx / 2, x[-1] + dx / 2)
        self.y_range = (y[0] - dy / 2, y[-1] + dy / 2)

        self._set_range()

        # Mise à jour des profils
        self._update_profiles()

        # Mise à jour des lignes de coupe
        self._update_slice_lines()

    def _update_slice_lines(self):
        if self.data is None:
            return

        x = (
            self.x_axis[self.x_index]
            if self.x_axis is not None
            else self.x_index
        )
        y = (
            self.y_axis[self.y_index]
            if self.y_axis is not None
            else self.y_index
        )

        self.vline.setPos(x)
        self.hline.setPos(y)