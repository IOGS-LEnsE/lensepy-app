import numpy as np

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout
import pyqtgraph as pg


class ImageCrossSections(QWidget):
    """
    Widget PyQtGraph affichant :

                       coupe X
                 ┌───────────────┐
                 │               │
        coupe Y  │    image      │
                 │               │
                 └───────────────┘

    Un clic sur l'image positionne les deux coupes.
    Les coupes restent fixes jusqu'au prochain clic.

    Parameters
    ----------
    data : np.ndarray
        Tableau 2D, indexé data[y, x].

    cmap : str ou pg.ColorMap, optional
        Colormap utilisé pour l'image.
        Exemples : 'viridis', 'plasma', 'inferno', 'magma', etc.
    """

    def __init__(self, data=None, cmap="viridis", parent=None):
        super().__init__(parent)

        self.data = None

        self.nx = 0
        self.ny = 0

        self.x_index = 0
        self.y_index = 0

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
        self.plot_x.setBackground("k")
        self.plot_x.showGrid(x=True, y=True, alpha=0.15)
        self.plot_x.setLabel("bottom", "X")
        self.plot_x.setLabel("left", "Value")
        self.curve_x = self.plot_x.plot(
            pen=pg.mkPen("b", width=2)
        )

        # Y slice
        self.plot_y = pg.PlotWidget()
        self.plot_y.setBackground("k")
        self.plot_y.showGrid(x=True, y=True, alpha=0.15)
        self.plot_y.setLabel("bottom", "Value")
        self.plot_y.setLabel("left", "Y")
        self.curve_y = self.plot_y.plot(
            pen=pg.mkPen("r", width=2)
        )

        # Image plot
        self.plot_image = pg.PlotWidget()
        self.plot_image.setBackground("k")
        self.plot_image.showGrid(x=False, y=False, alpha=0.15)
        self.plot_image.setLabel("bottom", "X")
        self.plot_image.setLabel("left", "Y")

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
        # Left Corner ! USE ??
        layout.addWidget(QWidget(), 0, 0)

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

        self.plot_image.setXRange(0, self.nx, padding=0)
        self.plot_image.setYRange(0, self.ny, padding=0)

        self.vline.setValue(self.x_index)
        self.hline.setValue(self.y_index)

        self._update_profiles()

    def _update_profiles(self):

        if self.data is None:
            return

        profile_x = self.data[self.y_index, :]
        x = np.arange(self.nx)
        self.curve_x.setData(x, profile_x)

        profile_y = self.data[:, self.x_index]
        y = np.arange(self.ny)
        self.curve_y.setData(profile_y, y)

    def _mouse_clicked(self, event):

        if self.data is None:
            return
        if event.button() != 1: # Left click only
            return

        # Click in the viewbox
        if not self.plot_image.sceneBoundingRect().contains(event.scenePos()):
            return

        # Convert coordinate from scene to image
        mouse_point = (self.plot_image.getPlotItem().vb
            .mapSceneToView(event.scenePos())
        )
        x = mouse_point.x()
        y = mouse_point.y()

        # Check values
        if (x < 0 or x >= self.nx
            or y < 0 or y >= self.ny):
            return

        # Slice Update
        self.x_index = int(round(x))
        self.y_index = int(round(y))
        self.vline.setValue(self.x_index)
        self.hline.setValue(self.y_index)

        self._update_profiles()

    def set_color_map(self, cmap):
        """Change colormap of the 2D surface."""
        self.cmap = self._get_colormap(cmap)
        self.image_item.setLookupTable(
            self.cmap.getLookupTable(0.0, 1.0, 256)
        )