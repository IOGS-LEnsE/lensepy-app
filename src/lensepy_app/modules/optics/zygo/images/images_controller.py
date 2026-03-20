__all__ = ["ZygoImagesController"]

from PyQt6.QtWidgets import QWidget
from lensepy_app.modules.optics.zygo.images.images_views import ImagesOpeningWidget
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget


class ZygoImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = QWidget()
        self.bot_right = ImagesOpeningWidget()
        self.top_right = ImageDisplayWidget()

        # Setup widgets

        # Signals


