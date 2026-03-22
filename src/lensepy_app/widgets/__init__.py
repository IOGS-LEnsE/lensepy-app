__all__ = [
    'objects',
    "qobject_to_widget"
]

from .histogram_widget import *
from .image_display_widget import *
from .xy_multi_chart_widget import *
from .camera_widget import *
from .surface_2D_view import *


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