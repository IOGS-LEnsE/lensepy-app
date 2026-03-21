__all__ = ["ZygoMasksController"]

from PyQt6.QtWidgets import QWidget
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget


class ZygoMasksController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.data_set = self.parent.variables['dataset']

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = QWidget()

        # Setup widgets

        # Signals

