from lensepy import translate
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.images.sampling import *
from lensepy.widgets import *


class SamplingController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # Widgets
        self.top_left = ImageDisplayWidget()
        self.bot_left = ImageDisplayWidget()
        self.bot_right = HistogramWidget()
        self.top_right = QWidget()  # Options !
        # Setup widgets
        self.bot_right.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))
        self.bot_right.set_background('white')
        if self.parent.variables['bits_depth'] is not None:
            self.top_left.set_bits_depth(int(self.parent.variables['bits_depth']))
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.top_left.set_bits_depth(8)
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image_from_array(self.parent.variables['image'])
        # Signals


