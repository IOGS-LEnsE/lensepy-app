
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QVBoxLayout, QLineEdit, QSlider, QProgressBar, \
    QSizePolicy
from lensepy.css import *


class SelectWidget(QWidget):
    """
    Widget including a select list.
    """
    choice_selected = pyqtSignal(str)

    def __init__(self, title: str, values: list, units: str = None):
        """

        :param title:   Title of the widget.
        :param values:  Values of the selection list.
        :param units:   Units of the data.
        """
        super().__init__()
        # Graphical objects
        self.label_title = QLabel(title)
        self.label_title.setStyleSheet(styleH2)
        self.combo_box = QComboBox()
        self.combo_box.addItems(values)
        self.combo_box.currentIndexChanged.connect(self.handle_choice_selected)
        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.label_title, 2)
        layout.addWidget(self.combo_box, 2)
        if units is not None:
            self.label_units = QLabel(units)
            layout.addWidget(self.label_units, 1)
        self.setLayout(layout)

    def handle_choice_selected(self):
        """
        Action performed when the colormode choice changed.
        """
        index = self.get_selected_index()
        value = self.get_selected_value()
        self.choice_selected.emit(str(index))

    def get_selected_value(self) -> str:
        """Get the selected value."""
        return self.combo_box.currentText()

    def get_selected_index(self) -> str:
        """Get the index of the selection."""
        return self.combo_box.currentIndex()

    def set_values(self, values: list[str]):
        """Update the list of values.
        :param values: List of values.
        """
        self.combo_box.clear()
        self.combo_box.addItems(values)

    def set_title(self, title: str):
        """
        Change the title of the selection object.
        :param title:   Title of the selection object.
        """
        self.label_title.setText(title)

    def set_choice(self, index):
        """
        Set the index of the selection.
        :param index: Index of the selection.
        """
        self.combo_box.setCurrentIndex(index)


class LabelWidget(QWidget):
    """Widget to display a label, with title, value and units."""
    def __init__(self, title: str, value: str, units: str = None):
        super().__init__()
        widget_w = QWidget()
        layout_w = QHBoxLayout()
        widget_w.setLayout(layout_w)

        self.title = QLabel(title)
        self.value = QLabel(value)
        self.title.setStyleSheet(styleH2)
        self.value.setStyleSheet(styleH2)
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_w.addWidget(self.title, 2)
        layout_w.addWidget(self.value, 2)
        if units is not None:
            self.units = QLabel(units)
            self.units.setStyleSheet(styleH3)
            self.units.setStyleSheet(styleH3)
            layout_w.addWidget(self.units, 1)
        else:
            self.units = QLabel('')
        self.setLayout(layout_w)

    def set_value(self, value):
        """Update widget value."""
        self.value.setText(value)


class SliderBloc(QWidget):
    """
    Slider block combining a numeric input and a horizontal slider.
    Emits the current value whenever it changes.
    """

    slider_changed = pyqtSignal(float)

    def __init__(self, name: str, unit: str, min_value: float, max_value: float,
                 integer: bool = False) -> None:
        super().__init__()

        self.integer = integer
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.ratio = 1 if integer else 100
        self.value = 0 #round(min_value + (max_value - min_value) / 3, 2)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- First line: label + input + unit ---
        self._init_value_line(name)

        # --- Second line: slider + min/max labels ---
        self._init_slider_line()

        self.update_block()

    # ----------------------------
    # Initialization subfunctions
    # ----------------------------

    def _styled_label(self, text: str, style: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(style)
        return label

    def _init_value_line(self, name: str):
        line = QHBoxLayout()
        self.label_name = self._styled_label(f"{name}:", styleH2)
        self.lineedit_value = QLineEdit(str(self.value))
        self.lineedit_value.textEdited.connect(self.handle_input_changed)
        self.lineedit_value.editingFinished.connect(self.handle_input_changed_finish)
        self.label_unit = self._styled_label(self.unit, styleH3)

        for widget in (self.label_name, self.lineedit_value, self.label_unit):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    def _init_slider_line(self):
        line = QHBoxLayout()
        self.label_min_value = self._styled_label(f"{self.min_value} {self.unit}", styleH3)
        self.label_max_value = self._styled_label(f"{self.max_value} {self.unit}", styleH3)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(self.min_value * self.ratio), int(self.max_value * self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)

        for widget in (self.label_min_value, self.slider, self.label_max_value):
            line.addWidget(widget)
        line.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setLayout(line)
        self.layout.addWidget(container)

    # ----------------------------
    # Event handling
    # ----------------------------

    def slider_position_changed(self):
        self.value = self.slider.value() / self.ratio
        if self.integer:
            self.value = int(self.value)
        self.lineedit_value.setText(str(self.value))
        self.slider_changed.emit(self.value)

    def handle_input_changed(self):
        """Triggered when user edits the numeric value."""
        try:
            val = float(self.lineedit_value.text())
        except ValueError:
            return

        self.value = self._clamp(val, self.min_value, self.max_value)

        self.slider.blockSignals(True)
        self.slider.setValue(int(self.value * self.ratio))
        self.slider.blockSignals(False)

        self.slider_changed.emit(self.value)

    def handle_input_changed_finish(self):
        """Triggered when user finishes to edit the numeric value."""
        try:
            val = float(self.lineedit_value.text())
        except ValueError:
            val = self.value
            return
        self.value = self._clamp(val, self.min_value, self.max_value)
        self.update_block()

    # ----------------------------
    # Utilities
    # ----------------------------

    def update_block(self):
        """Sync text and slider position."""
        val = int(self.value) if self.integer else self.value
        self.lineedit_value.setText(str(val))
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.ratio))
        self.slider.blockSignals(False)

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = int(value) if self.integer else float(value)
        self.update_block()

    def set_min_max_slider_values(self, min_value: float, max_value: float, value: float | None = None):
        """Update slider bounds and optionally reset its current value."""
        self.min_value, self.max_value = min_value, max_value
        self.slider.setRange(int(min_value * self.ratio), int(max_value * self.ratio))
        if value is not None:
            self.set_value(value)
        self.label_min_value.setText(f"{min_value} {self.unit}")
        self.label_max_value.setText(f"{max_value} {self.unit}")

    def set_enabled(self, enabled: bool):
        """Enable or disable the whole block."""
        self.slider.setEnabled(enabled)
        self.lineedit_value.setEnabled(enabled)

    @staticmethod
    def _clamp(val, vmin, vmax):
        return max(vmin, min(vmax, val))


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit
)

# Styles
styleH2 = "font-weight: bold; font-size: 14px;"
styleH3 = "font-size: 12px; color: gray;"


class SliderBlocVertical(QWidget):
    """
    Slider block combining a numeric input and a vertical slider.
    Displays title above, slider in the center, and value below.
    Emits the current value whenever it changes.
    """

    slider_changed = pyqtSignal(float)

    def __init__(self, name: str, unit: str, min_value: float, max_value: float,
                 integer: bool = False) -> None:
        super().__init__()

        self.integer = integer
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.ratio = 1 if integer else 100
        self.value = 0

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider title
        self.label_name = QLabel(name)
        self.label_name.setStyleSheet(styleH2)
        self.label_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_name)

        self._init_value_line()
        self._init_slider_section()

        self.update_block()

    # ----------------------------
    # Sous-fonctions d’initialisation
    # ----------------------------

    def _styled_label(self, text: str, style: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(style)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _init_slider_section(self):
        slider_layout = QVBoxLayout()
        slider_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Valeur max en haut
        self.label_max_value = self._styled_label(f"{self.max_value} {self.unit}", styleH3)
        slider_layout.addWidget(self.label_max_value)

        # Slider vertical
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(int(self.min_value * self.ratio), int(self.max_value * self.ratio))
        self.slider.setFixedHeight(150)
        self.slider.valueChanged.connect(self.slider_position_changed)
        slider_layout.addWidget(self.slider)

        # Valeur min en bas
        self.label_min_value = self._styled_label(f"{self.min_value} {self.unit}", styleH3)
        slider_layout.addWidget(self.label_min_value)

        self.layout.addLayout(slider_layout)

    def _init_value_line(self):
        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineedit_value = QLineEdit(str(self.value))
        #self.lineedit_value.setFixedWidth(60)
        self.lineedit_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineedit_value.editingFinished.connect(self.input_changed)
        value_layout.addWidget(self.lineedit_value)

        if self.unit != '':
            self.label_unit = self._styled_label(self.unit, styleH3)
            value_layout.addWidget(self.label_unit)

        container = QWidget()
        container.setLayout(value_layout)
        self.layout.addWidget(container)

    # ----------------------------
    # Gestion des événements
    # ----------------------------

    def slider_position_changed(self):
        self.value = self.slider.value() / self.ratio
        if self.integer:
            self.value = int(self.value)
        self.lineedit_value.setText(str(self.value))
        self.slider_changed.emit(self.value)

    def input_changed(self):
        try:
            val = float(self.lineedit_value.text())
        except ValueError:
            val = self.value

        self.value = self._clamp(val, self.min_value, self.max_value)
        self.update_block()
        self.slider_changed.emit(self.value)

    # ----------------------------
    # Méthodes utilitaires
    # ----------------------------

    def update_block(self):
        val = int(self.value) if self.integer else self.value
        self.lineedit_value.setText(str(val))
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * self.ratio))
        self.slider.blockSignals(False)

    def get_value(self) -> float:
        return self.value

    def set_value(self, value: float):
        self.value = int(value) if self.integer else float(value)
        self.update_block()

    def set_min_max_slider_values(self, min_value: float, max_value: float, value: float | None = None):
        self.min_value, self.max_value = min_value, max_value
        self.slider.setRange(int(min_value * self.ratio), int(max_value * self.ratio))
        if value is not None:
            self.set_value(value)
        self.label_min_value.setText(f"{min_value} {self.unit}")
        self.label_max_value.setText(f"{max_value} {self.unit}")

    def set_enabled(self, enabled: bool):
        self.slider.setEnabled(enabled)
        self.lineedit_value.setEnabled(enabled)

    @staticmethod
    def _clamp(val, vmin, vmax):
        return max(vmin, min(vmax, val))


class LineEditWidget(QWidget):
    """
    Widget for line edit, including a title.
    """
    edit_changed = pyqtSignal(str)
    def __init__(self, title:str='', value='', parent=None):
        super().__init__(None)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.value = value

        # Label
        self.label = QLabel(title)
        layout.addWidget(self.label, 1)
        # Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setText(value)
        self.line_edit.editingFinished.connect(lambda: self.edit_changed.emit(self.line_edit.text()))
        layout.addWidget(self.line_edit, 2)

    def set_value(self, value):
        """
        Set the widget value in the line edit object.
        :param value:   Value to set.
        """
        self.line_edit.setText(value)

    def set_enabled(self, value: bool=True):
        """
        Set the widget enabled.
        :param value:   True or False.
        """
        self.line_edit.setEnabled(value)

class VerticalGauge(QWidget):

    def __init__(self, parent=None, title="", min_value=0, max_value=100):
        """Create a vertical gauge.
        :param title: Title of the gauge.
        :param min_value: Minimum value of the gauge.
        :param max_value: Maximum value of the gauge.
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Label au-dessus
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(styleH2)
        layout.addWidget(self.label)

        # Barre verticale
        self.progress = QProgressBar()
        self.progress.setOrientation(Qt.Orientation.Vertical)
        self.progress.setRange(min_value, max_value)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.progress.setMinimumWidth(100)

        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Custom Style
        self.progress.setStyleSheet(progressBar)

        self.value_label = QLabel(title)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(styleH3)
        layout.addWidget(self.value_label)

        self.setLayout(layout)

    def set_value(self, value):
        """
        Update the value of the gauge.
        :param value: value to set
        """
        self.progress.setValue(value)
        self.value_label.setText(str(value))
        self.repaint()

    def set_min_max_values(self, min_value, max_value):
        """
        Set min and max values.
        :param min_value: min value
        :param max_value: max value
        """
        self.progress.setRange(min_value, max_value)

    def set_title(self, text):
        """
        Set the title of the gauge.
        :param text: title
        """
        self.label.setText(text)

