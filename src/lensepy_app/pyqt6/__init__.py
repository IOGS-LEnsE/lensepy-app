__all__ = [
    "widget_slider",      # refers to the 'widget_slider.py' file
    "widget_histogram",   # refers to the 'widget_histogram.py' file
    "widget_progress_bar",   # refers to the 'widget_progress_bar.py' file
    "widget_checkbox",   # refers to the 'widget_checkbox.py' file
    "widget_editline",   # refers to the 'widget_editline.py' file
    "widget_image_display",     # refers to the 'widget_image_display.py' file
    "widget_image_histogram",     # refers to the 'widget_image_display.py' file
    "widget_combobox",
    "qobject_to_widget"
]

from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

def qobject_to_widget(obj) -> QWidget:
    """Include a graphical element (from PyQt6) in a QWidget.
    :param obj: Graphical element to transform.
    :return: QWidget object containing the graphical element. Center.
    """
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.addWidget(obj)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return container