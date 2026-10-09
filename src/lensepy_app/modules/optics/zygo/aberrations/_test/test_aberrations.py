from matplotlib import pyplot as plt
from lensepy_app.modules.optics.zygo.aberrations.aberrations_models import *
from lensepy.optics.zygo.dataset import *
import cv2

if __name__ == '__main__':
    filepath = ('../../../../../../../../lensepy-data/optics/zygo/test3.mat')

    dataset = DataSet()
    dataset.load_images_set_from_file(filepath)

    image1 = dataset.get_image_from_set(1, 1)

    img_diff1 = dataset.get_image_from_set(1, 1) - dataset.get_image_from_set(3, 1)
    img_diff2 = dataset.get_image_from_set(2, 1) - dataset.get_image_from_set(4, 1)

    img = np.zeros_like(image1)
    for k in range(3):
        img += dataset.get_image_from_set(k+1, 1)

    # Mask
    seuil = 100
    mask = np.ones_like(image1)
    mask[(img_diff1 < seuil) & (img_diff2 < seuil)] = 0

    plt.figure()
    plt.imshow(mask,cmap='gray')
    plt.title('Mask')


    mask_uint8 = (mask.astype(np.uint8)) * 255
    img_diff1 = img_diff1.astype(np.uint8)
    result = cv2.cvtColor(mask_uint8, cv2.COLOR_GRAY2BGR)

    contours, _ = cv2.findContours(
        mask_uint8,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    tf_mask = np.fft.fftshift(np.fft.fft2(img_diff1+img_diff2))
    plt.figure()
    plt.imshow(np.log(np.abs(tf_mask)+0.01),cmap='gray')
    plt.title('FFT Log mask')
    plt.show()

    '''
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circles.append((radius, x, y, contour))
            cv2.circle(
                result,
                (int(x), int(y)),
                int(np.ceil(radius)),
                (0, 0, 255),
                2
            )

    # Plus grand cercle
    radius, x, y, contour = max(circles, key=lambda c: c[0])
    
    '''
    # Visualisation

    plt.figure()
    plt.imshow(result, cmap='gray')
    plt.show()
