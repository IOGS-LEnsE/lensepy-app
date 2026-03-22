
import numpy as np
from PyQt6.QtGui import QImage


def array_to_qimage(array: np.ndarray) -> QImage:
    """Transcode an array to a QImage.
    :param array: Array containing image data.
    :type array: numpy.ndarray
    :return: Image to display.
    :rtype: QImage
    """
    shape_size = len(array.shape)
    if shape_size == 2:
        height, width = array.shape
        bytes_per_line = width  # only in 8 bits gray
        return QImage(array, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
    else:
        height, width, _ = array.shape
        bytes_per_line = 3 * width  # only in 8 bits gray
        return QImage(array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
