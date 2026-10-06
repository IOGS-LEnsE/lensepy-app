
from lensepy.optics.zygo import *

def get_auto_mask(dataset: DataSet):
    img_diff1 = dataset.get_image_from_set(1, 1) - dataset.get_image_from_set(3, 1)
    img_diff2 = dataset.get_image_from_set(2, 1) - dataset.get_image_from_set(4, 1)


    center = (0, 0)
    radius = 100
    return center, radius


