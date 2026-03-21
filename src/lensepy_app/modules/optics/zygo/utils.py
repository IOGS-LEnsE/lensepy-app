import os
import numpy as np
import scipy

from lensepy.utils.images import resize_image_ratio

def generate_images_grid(images: list[np.ndarray]):
    """Generate a grid with 5 images.
    The 6th image is the mean of the 4 first images.
    :param images: List of 5 images.
    """
    img_height, img_width, *channels = images[0].shape
    if channels:
        for k in range(len(images)):
            if channels[0] != 1:
                images[k] = cv2.cvtColor(images[k], cv2.COLOR_RGB2GRAY)
            else:
                images[k] = images[k].squeeze()

    separator_size = 5
    # Global size
    total_height = 2 * img_height + separator_size  # 2 rows of images
    total_width = 3 * img_width + 2 * separator_size  # 3 columns of images
    # Empty image
    result = np.ones((total_height, total_width), dtype=np.uint8) * 255
    # Add each images
    result[0:img_height, 0:img_width] = images[0]
    result[0:img_height, img_width + separator_size:2 * img_width + separator_size] = images[1]
    result[0:img_height, 2 * img_width + 2 * separator_size:] = images[2]
    result[img_height + separator_size:, 0:img_width] = images[3]
    result[img_height + separator_size:, img_width + separator_size:2 * img_width + separator_size] = images[4]
    sum_image = (images[0] + images[1] + images[2] + images[3])/4
    sum_image = sum_image.astype(np.uint8)
    result[img_height + separator_size:, 2 * img_width + 2 * separator_size:] = sum_image
    result_s = resize_image_ratio(result, img_height, img_width)
    return result_s

def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    if os.path.exists(file_path):
        data = scipy.io.loadmat(file_path)
        return data
    else:
        print('read_mat_file / No File')

def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None, masks_type: list = []):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    :param masks_type: Type of the masks to save. Default [].
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    if len(masks_type) != 0:
        data['Masks_Type'] = masks_type
    scipy.io.savemat(file_path, data)

def split_3d_array(array_3d, size: int = 5):
    # Ensure the array has the expected shape
    if array_3d.shape[2]%size != 0:
        raise ValueError(f"The loaded array does not have the expected third dimension size of {size}.")
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(array_3d.shape[2])]
    return arrays
