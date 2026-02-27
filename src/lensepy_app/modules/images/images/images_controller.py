__all__ = ["ImagesController"]

from lensepy.modules.images.images.images_views import ImagesOpeningWidget, ImagesInfosWidget
from lensepy.widgets.image_display_widget import ImageDisplayWidget
from lensepy.appli._app.template_controller import TemplateController
from lensepy.widgets.histogram_widget import HistogramWidget
from lensepy import translate
import numpy as np


class ImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = ImageDisplayWidget()
        self.bot_left = HistogramWidget()
        self.bot_right = ImagesOpeningWidget(self)
        self.top_right = ImagesInfosWidget(self)
        # Setup widgets
        self.bot_left.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))
        self.bot_left.set_background('white')
        if self.parent.variables['bits_depth'] is not None:
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image(self.parent.variables['image'])
        self.bot_left.refresh_chart()
        # Signals
        self.bot_right.image_opened.connect(self.action_image_opened)

    def action_image_opened(self, event):
        """
        Action performed when an image is opened via the bot_right widget.
        :return:
        """
        image = self.get_variables()['image']
        # Display image
        self.display_image(image)
        # Update histogram
        self.bot_left.set_image(image)
        self.bot_left.refresh_chart()
        # Update image information
        self.top_right.update_infos(image)
        self.parent.main_window.update_menu()

    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)


