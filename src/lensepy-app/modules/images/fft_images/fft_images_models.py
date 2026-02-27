import numpy as np


def process_FFT(image: np.ndarray):
    """
    Perform a Fast Fourier Transform (FFT) on a 2D NumPy array representing image data.
    If the image is in RGB format, the FFT is applied to its luminance component,
    computed according to the Rec. 709 standard.

    :param image: 2D numpy array (containing data of an image).
    :return: 2D numpy array (containing shifted FFT of the image).
    """
    img_lum = np.zeros_like(image)
    if image.ndim == 3: # RGB -> Y
        r_img = image[..., 0].astype(float)
        g_img = image[..., 1].astype(float)
        b_img = image[..., 2].astype(float)
        # Luminance / Rec. 709
        img_lum = 0.2126 * r_img + 0.7152 * g_img + 0.0722 * b_img
    elif image.ndim == 2:   # Gray scale
        img_lum = image.astype(float)
    if img_lum is not None:
        fft_img = np.fft.fft2(img_lum)
        fft_img_shift = np.fft.fftshift(fft_img)
        return fft_img_shift
    return None

def create_mask(image, form: str = None, radius: int = 10):
    H, W = image.shape[:2]
    cx = W // 2
    cy = H // 2
    if form == 'circular':
        y, x = np.ogrid[:H, :W]
        dist2 = (x - cx) ** 2 + (y - cy) ** 2
        mask = dist2 <= (radius ** 2)
        return mask
    elif form == 'square':
        mask = np.zeros_like(image)
        x0 = cx - radius
        y0 = cy - radius
        mask[y0:y0 + 2*radius, x0:x0 + 2*radius] = True
        return mask
    elif form == 'gaussian':
        sigma = 2
        y, x = np.ogrid[:H, :W]
        mask = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma ** 2))
        return mask
    res_mas = np.zeros_like(image)
    return res_mas