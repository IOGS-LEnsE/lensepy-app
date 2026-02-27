from lensepy import translate
from lensepy.appli._app.template_controller import TemplateController
from lensepy.modules.images.spatial_images import *
from lensepy.widgets import *


class SpatialImagesController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # Attributes
        self.x_cross = None
        self.y_cross = None
        # Widgets
        self.top_left = ImageDisplayWithCrosshair()
        self.bot_left = HistogramWidget()
        self.bot_right = XYMultiChartWidget(base_color=ORANGE_IOGS, allow_point_selection=False)
        self.top_right = XYMultiChartWidget(allow_point_selection=False)
        # Setup widgets
        self.bot_left.set_labels(translate('histo_xlabel'), translate('histo_ylabel'))
        self.bot_left.set_background('white')
        self.top_right.set_background('white')
        self.top_right.set_title(translate('slice_display_h'))
        self.bot_right.set_background('white')
        self.bot_right.set_title(translate('slice_display_v'))
        if self.parent.variables['bits_depth'] is not None:
            self.bot_left.set_bits_depth(int(self.parent.variables['bits_depth']))
        else:
            self.bot_left.set_bits_depth(8)
        if self.parent.variables['image'] is not None:
            self.top_left.set_image_from_array(self.parent.variables['image'])
            self.bot_left.set_image(self.parent.variables['image'])
        self.bot_left.refresh_chart()
        # Signals
        self.top_left.point_selected.connect(self.handle_xy_changed)

    def handle_xy_changed(self, x, y):
        """
        Action performed when a crosshair is selected.
        :param x: X coordinate.
        :param y: Y coordinate.
        """
        self.x_cross = x
        self.y_cross = y
        image = self.parent.variables.get('image')
        if image is not None:
            self.update_slices(image)

    def update_slices(self, image):
        """
        Update slice values from image.
        :param image:   Numpy array containing the new image.
        """
        if self.x_cross is None or self.y_cross is None or image is None:
            return

        # Détection du type d'image et conversion en grayscale/luminance si nécessaire
        if image.ndim == 2:  # grayscale
            gray_image = image
        elif image.ndim == 3 and image.shape[2] == 3:  # RGB
            gray_image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            raise ValueError("Image format non supporté")

        x_idx, y_idx = int(self.x_cross), int(self.y_cross)
        x_data = gray_image[y_idx, :]
        y_data = gray_image[:, x_idx]

        xx = np.linspace(1, len(x_data), len(x_data))
        yy = np.linspace(1, len(y_data), len(y_data))

        self.top_right.set_data(xx, x_data, x_label='position', y_label='intensity')
        self.top_right.refresh_chart()
        self.top_right.set_information(
            f'Mean = {np.mean(x_data):.1f} / Min = {np.min(x_data):.1f} / Max = {np.max(x_data):.1f}')

        self.bot_right.set_data(yy, y_data, x_label='position', y_label='intensity')
        self.bot_right.refresh_chart()
        self.bot_right.set_information(
            f'Mean = {np.mean(y_data):.1f} / Min = {np.min(y_data):.1f} / Max = {np.max(y_data):.1f}')


    def display_image(self, image: np.ndarray):
        """
        Display the image given as a numpy array.
        :param image:   numpy array containing the data.
        :return:
        """
        self.top_left.set_image_from_array(image)


