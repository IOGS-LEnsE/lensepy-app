import cv2
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QGuiApplication
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.default.default_views import *
from lensepy.widgets import ImageDisplayWidget
from lensepy.widgets.html_view import HTMLView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _app.main_manager import MainManager

class DefaultController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent # main manager
        self.top_left = HTMLView()
        self.top_left.hide()
        self.top_right = ImageDisplayWidget(self)
        self.top_right.hide()
        self.bot_left = DefaultTopLeftWidget(self)
        self.bot_right = QWidget()


    def display(self):
        config = self.parent.parent.config

        if 'html' in config:
            if config['html'] is not None:
                self.top_left.show()
                url = config['html']
                self.top_left.set_url(url)
        if 'img_desc' in config:
            if config['img_desc'] is not None:
                self.top_right.show()
                image = cv2.imread(config['img_desc'])
                self.top_right.set_image_from_array(image)
                self.top_right.update()
        self.update_view()

        self.bot_left.display(config)


        