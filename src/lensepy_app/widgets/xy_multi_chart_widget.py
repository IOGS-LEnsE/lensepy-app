import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from pyqtgraph import mkPen, PlotWidget
import pyqtgraph as pg

from lensepy.css import *


class XYMultiChartWidget(QWidget):
    """
    Widget to display XY curves:
    – either all curves on a single plot (multi_chart=False)
    – or one curve per vertically stacked plot (multi_chart=True)
    """

    pointSelectionFinished = pyqtSignal(float, float, float, float)
    vertical_point_selected = pyqtSignal(int, int, int, int)
    horizontal_point_selected = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None, multi_chart=True,
                 base_color=None, max_points=2000,
                 allow_point_selection=True):
        super().__init__(parent)
        self.multi_chart = multi_chart
        self.allow_point_selection = allow_point_selection
        self.max_points = max_points
        self.__show_grid = True
        self.background_color = "white"
        self.base_color = base_color

        # Data
        self.plot_x_data = []
        self.plot_y_data = []
        self.y_names = []
        self.x_label = ""
        self.y_label = ""

        # Gestion couleurs
        if self.base_color is not None:
            base_colors = [self.base_color, BLUE_IOGS, ORANGE_IOGS, GREEN_IOGS, RED_IOGS]
        else:
            base_colors = [BLUE_IOGS, ORANGE_IOGS, GREEN_IOGS, RED_IOGS]
        self.pen = [pg.mkPen(color=c, style=Qt.PenStyle.SolidLine, width=2.5) for c in base_colors]

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel('', alignment=Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "background-color: darkgray; font-weight:bold; color:white; font-size:20px;"
        )
        self.layout.addWidget(self.title_label)

        self.charts_container = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_container)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.charts_container)
        self.layout.addWidget(self.scroll_area)

        self.info_label = QLabel(text='', alignment=Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-size: 14px;")
        self.layout.addWidget(self.info_label)

        # Variables internes
        self.plot_widgets = []
        self.curves = []
        self.selected_points = {}  # {plot_index: [(x0,y0),(x1,y1)]}
        self.scatter_items = {}  # {plot_index: ScatterPlotItem}

        self.set_background(self.background_color)

    # -------------------- API publique --------------------
    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_information(self, info: str):
        self.info_label.setText(info)

    def set_background(self, css_color: str):
        self.background_color = css_color
        self.setStyleSheet(f"background:{css_color};")
        for pw in self.plot_widgets:
            pw.setBackground(css_color)

    def set_data(self, x_axis, y_axis, y_names=None, x_label='', y_label=''):
        if not isinstance(y_axis[0], (list, np.ndarray)):
            y_axis = [y_axis]
        if not isinstance(x_axis[0], (list, np.ndarray)):
            x_axis = [x_axis] * len(y_axis)

        self.plot_x_data = [np.array(x) for x in x_axis]
        self.plot_y_data = [np.array(y) for y in y_axis]
        self.y_names = y_names if y_names else [f"Curve {i + 1}" for i in range(len(y_axis))]
        self.x_label = x_label
        self.y_label = y_label

    def show_grid(self, value=True):
        self.__show_grid = value
        for pw in self.plot_widgets:
            pw.showGrid(x=value, y=value)

    # -------------------- Rafraîchissement --------------------
    def refresh_chart(self, last=0):
        if not self.plot_widgets:
            if self.multi_chart:
                self._init_multiple_charts()
            else:
                self._init_single_chart()

        if self.multi_chart:
            for i, (x, y) in enumerate(zip(self.plot_x_data, self.plot_y_data)):
                if i >= len(self.plot_widgets):
                    continue
                x_plot, y_plot = self._slice_and_decimate(x, y, last)
                pw = self.plot_widgets[i]
                self.curves[i].setData(x_plot, y_plot)
                # mettre à jour les marqueurs existants
                if i in self.selected_points:
                    self._update_markers(i)
        else:
            pw = self.plot_widgets[0]
            for i, (x, y) in enumerate(zip(self.plot_x_data, self.plot_y_data)):
                x_plot, y_plot = self._slice_and_decimate(x, y, last)
                self.curves[i].setData(x_plot, y_plot)
            if 0 in self.selected_points:
                self._update_markers(0)

    # -------------------- Initialisation des graphiques --------------------
    def _configure_plot_widget(self, pw: pg.PlotWidget, plot_index=0):
        pw.setBackground(self.background_color)
        pw.showGrid(x=self.__show_grid, y=self.__show_grid)
        pw.setMouseEnabled(x=False, y=False)
        pw.setMenuEnabled(False)

        if self.allow_point_selection:
            pw.scene().sigMouseClicked.connect(lambda event, idx=plot_index: self._on_plot_click(event, idx))

    def _init_single_chart(self):
        plot_widget = pg.PlotWidget()
        self._configure_plot_widget(plot_widget, plot_index=0)
        self.plot_widgets.append(plot_widget)
        self.charts_layout.addWidget(plot_widget)

        legend = plot_widget.addLegend()
        self.curves = []

        for i, y in enumerate(self.plot_y_data):
            curve = plot_widget.plot([], [], pen=self.pen[i % len(self.pen)], name=self.y_names[i])
            self.curves.append(curve)

        styles = {"color": "black", "font-size": "14px"}
        if self.x_label:
            plot_widget.setLabel("bottom", self.x_label, **styles)
        if self.y_label:
            plot_widget.setLabel("left", self.y_label, **styles)

    def _init_multiple_charts(self):
        self.plot_widgets = []
        self.curves = []

        for i, y in enumerate(self.plot_y_data):
            plot_widget = pg.PlotWidget()
            self._configure_plot_widget(plot_widget, plot_index=i)
            self.plot_widgets.append(plot_widget)
            self.charts_layout.addWidget(plot_widget)

            curve = plot_widget.plot([], [], pen=self.pen[i % len(self.pen)], name=self.y_names[i])
            self.curves.append(curve)

            plot_widget.setTitle(self.y_names[i], color="black", size="12pt")
            styles = {"color": "black", "font-size": "14px"}
            if self.x_label:
                plot_widget.setLabel("bottom", self.x_label, **styles)
            if self.y_label:
                plot_widget.setLabel("left", self.y_label, **styles)

    # -------------------- Décimation --------------------
    def _slice_and_decimate(self, x, y, last):
        if last > 0 and len(x) > last:
            x, y = x[-last:], y[-last:]
        n = len(x)
        if n > self.max_points:
            step = n // self.max_points
            x = x[::step]
            y = y[::step]
        return x, y

    # -------------------- Gestion des clics --------------------
    def _on_plot_click(self, event, plot_index):
        if not self.allow_point_selection:
            return

        plot_item = self.plot_widgets[plot_index].getPlotItem()
        vb = plot_item.vb
        pos = vb.mapSceneToView(event.scenePos())
        x, y = pos.x(), pos.y()

        if event.button() == Qt.MouseButton.LeftButton:
            # Left click : add a new point
            if plot_index not in self.selected_points:
                self.selected_points[plot_index] = []

            if len(self.selected_points[plot_index]) >= 2:
                self.selected_points[plot_index].pop(0)
            self.selected_points[plot_index].append((x, y))

            self._update_markers(plot_index)

            if len(self.selected_points[plot_index]) == 2:
                # Emit signal
                if plot_index == 0:
                    (x0, y0), (x1, y1) = self.selected_points[plot_index]
                    self.horizontal_point_selected.emit(int(x0), int(y0), int(x1), int(y1))
                elif plot_index == 1:
                    (x0, y0), (x1, y1) = self.selected_points[plot_index]
                    self.horizontal_point_selected.emit(int(x0), int(y0), int(x1), int(y1))

        elif event.button() == Qt.MouseButton.RightButton:
            # Right click : delete all points
            if plot_index in self.selected_points:
                self.selected_points[plot_index] = []
            if plot_index in self.scatter_items:
                self.plot_widgets[plot_index].removeItem(self.scatter_items[plot_index])
                del self.scatter_items[plot_index]

    def _update_markers(self, plot_index):
        if plot_index in self.scatter_items:
            self.plot_widgets[plot_index].removeItem(self.scatter_items[plot_index])

        points = self.selected_points.get(plot_index, [])
        if points:
            spots = [{'pos': p, 'brush': 'r', 'size': 10} for p in points]
            scatter = pg.ScatterPlotItem(spots=spots)
            self.scatter_items[plot_index] = scatter
            self.plot_widgets[plot_index].addItem(scatter)