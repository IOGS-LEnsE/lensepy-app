import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox,
    QGridLayout, QHBoxLayout
)
from scipy.fftpack import fftshift, ifftshift, fft2, ifft2
import matplotlib.pyplot as plt

from PyQt6.QtCore import pyqtSignal, QObject


class FourierManager(QObject):

    scanProgress = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QHBoxLayout()

        self.rpupil = 100
        self.center = [200, 200]
        self.lam = 650e-09
        """grandissement = (345e-6*2456)/(4*0.3)
        self.pix = 345e-6/grandissement"""

    def pupil_size(self, D, lam, pix, size):
        pixrad = pix * np.pi / (180 * 3600)  # Pixel-size in radians
        nu_cutoff = D / lam  # Cutoff frequency in rad^-1
        deltanu = 1. / (size * pixrad)  # Sampling interval in rad^-1
        rpupil = nu_cutoff / (2 * deltanu)  # pupil size in pixels
        self.rpupil = int(rpupil)

    def mask(self, size : tuple):
        r = 1
        x = np.linspace(-r, r, 2*self.rpupil)
        y = np.linspace(-r, r, 2*self.rpupil)

        x0, y0 = self.center[0], self.center[1]

        [X,Y] = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)
        theta = np.arctan2(Y, X)
        M = 1 * (np.cos(theta) ** 2 + np.sin(theta) ** 2)
        M[R > 1] = 0

        h, w = size
        Mask = np.zeros([h, w])
        Mask[x0 - self.rpupil + 1:x0 + self.rpupil + 1, y0 - self.rpupil + 1:y0 + self.rpupil + 1] = M
        return Mask

    def zernike_polar(self, coefficients, r, u):
        Z = coefficients
        Z0 = Z[0] * 1 * (np.cos(u) ** 2 + np.sin(u) ** 2) #n = 0, m = 0   #Ordre 0

        Z1 = Z[1] * 2 * r * np.cos(u) #n = 1, m = 1   #Ordre 1
        Z2 = Z[2] * 2 * r * np.sin(u) #n = 1, m = -1

        Z3 = Z[3] * np.sqrt(3) * (2 * r ** 2 - 1) #n = 2, m = 0   #Ordre 2
        Z4 = Z[4] * np.sqrt(6) * r ** 2 * np.sin(2 * u) #n = 2, m = -2
        Z5 = Z[5] * np.sqrt(6) * r ** 2 * np.cos(2 * u) #n = 2, m = 2

        Z6 = Z[6] * np.sqrt(8) * (3 * r ** 2 - 2) * r * np.sin(u) #n = 3, m = -1   #Ordre 3
        Z7 = Z[7] * np.sqrt(8) * (3 * r ** 2 - 2) * r * np.cos(u) #n = 3, m = 1
        Z8 = Z[8] * np.sqrt(8) * r ** 3 * np.sin(3 * u) #n = 3, m = -3
        Z9 = Z[9] * np.sqrt(8) * r ** 3 * np.cos(3 * u) #n = 3, m = 3

        Z10 = Z[10] * np.sqrt(5) * (1 - 6 * r ** 2 + 6 * r ** 4) #n = 4, m = 0   #Ordre 4
        Z11 = Z[11] * np.sqrt(10) * (4 * r ** 2 - 3) * r ** 2 * np.cos(2 * u) #n = 4, m = 2
        Z12 = Z[12] * np.sqrt(10) * (4 * r ** 2 - 3) * r ** 2 * np.sin(2 * u) #n = 4, m = -2
        Z13 = Z[13] * np.sqrt(10) * r ** 4 * np.cos(4 * u) #n = 4, m = 4
        Z14 = Z[14] * np.sqrt(10) * r ** 4 * np.sin(4 * u) #n = 4, m = -4

        Z15 = Z[15] * np.sqrt(7)*(20*r**6-30*r**4+12*r**2-1) #n = 6, m = 0   #Ordre 6

        ZW = Z0 + Z1 + Z2 + Z3 + Z4 + Z5 + Z6 + Z7 + Z8 + Z9 + Z10 + Z11 + Z12 + Z13 + Z14 + Z15
        return ZW

    def phase(self, coefficients, size : tuple):
        r = 1
        x = np.linspace(-r, r, 2 * self.rpupil)
        y = np.linspace(-r, r, 2 * self.rpupil)

        [X, Y] = np.meshgrid(x, y)
        R = np.sqrt(X ** 2 + Y ** 2)
        theta = np.arctan2(Y, X)

        Z = self.zernike_polar(coefficients, R, theta)
        Z[R > 1] = 0

        h, w = size
        x0, y0 = self.center[0], self.center[1]
        A = np.zeros([h, w])
        A[x0 - self.rpupil + 1:x0 + self.rpupil + 1, y0 - self.rpupil + 1:y0 + self.rpupil + 1] = Z
        return A

    def complex_pupil(self, A, Mask):
        abbe = np.exp(1j * A)
        abbe_z = np.zeros((len(abbe), len(abbe)), dtype=np.complex128)
        abbe_z = Mask * abbe
        return abbe_z

    def PSF(self, complx_pupil):
        PSF = ifftshift(fft2(fftshift(complx_pupil)))
        PSF = (np.abs(PSF)) ** 2  # or PSF*PSF.conjugate()
        PSF = PSF / PSF.sum()  # normalizing the PSF
        return PSF

    def find_rf_from_image(self, image):
        '''compares the result of the PSF treatment on the diffraction limit with the PSF of the actual image'''
        size = image.shape
        diff_lim_image = self.mask(size)
        psf_diff_lim = self.PSF(diff_lim_image)

        psf_image = self.PSF(image)
        h, w = size

        rf = psf_image[h // 2][w // 2] / psf_diff_lim[h // 2][w // 2]
        return rf, psf_diff_lim, psf_image

    def find_rf_from_coefs(self, coefficients, size):
        diff_lim_image = self.mask(size)
        psf_diff_lim = self.PSF(diff_lim_image)

        A = self.phase(coefficients, size)
        image = self.complex_pupil(A, diff_lim_image)
        psf_image = self.PSF(image)
        h, w = size

        rf = psf_image[h//2][w//2] / psf_diff_lim[h//2][w//2]
        return rf, psf_diff_lim, psf_image

    def afficher_pupille(self, coefficients, size):
        mask_image = self.mask(size)
        A = self.phase(coefficients, size)
        image = np.angle(self.complex_pupil(A, mask_image))
        return image

    def MTF(self, complx_pupil):
        psf_image = self.PSF(complx_pupil)
        otf = fft2(ifftshift(psf_image))
        otf_max = abs(otf[0, 0])
        otf = otf / otf_max
        mtf = abs(otf)
        return np.fft.fftshift(mtf)

    def MTF_from_PSF(self, psf):
        otf = fft2(ifftshift(psf))
        otf_max = abs(otf[0, 0])
        otf = otf / otf_max
        mtf = abs(otf)
        return np.fft.fftshift(mtf)

    """def lentille(self, complex_pupil, pix_size:float, dist_foc: float, d: float = 0):
        '''This function returns the diffraction pattern resulting from an optical system at whatever distance (d)
        from its focal point (in algebraic value) you chose'''
        r = 1
        x = np.linspace(-r, r, 2 * self.rpupil)
        y = np.linspace(-r, r, 2 * self.rpupil)

        [X, Y] = np.meshgrid(x, y)
        R2 = (X*pix_size) ** 2 + (Y*pix_size) ** 2

        if d!=-dist_foc:
            dist_phase = np.exp(1j * 2*np.pi/self.lam * (R2/2 * (1/(dist_foc + d) - 1/dist_foc)))
            dist_phase[R2 > 1] = 1
        else:
            return abs(complex_pupil)

        x0, y0 = self.center[0], self.center[1]
        h, w = complex_pupil.shape
        no_aberration = np.ones([h, w], dtype=np.complex128)
        no_aberration[x0 - self.rpupil + 1:x0 + self.rpupil + 1, y0 - self.rpupil + 1:y0 + self.rpupil + 1] = dist_phase

        diff_pattern = no_aberration * complex_pupil

        return self.PSF(diff_pattern)"""

    def normalize(self, image):
        max_image = image.max()
        return image/max_image

    def test_params(self):
        '''This function serves as a backup for testing when no acquisition is done beforehand,
        it returns the coefficients and the image size which are necessary for further use'''
        coefficients = np.zeros(16)
        coefficients[1] = 0.1
        coefficients[2] = 0.1
        coefficients[3] = 0.3
        coefficients[4] = -0.2
        coefficients[5] = 0.3
        coefficients[6] = -0.1
        coefficients[7] = 0.5
        coefficients[8] = -2
        size = (800, 800)
        self.center = [size[0] // 2, size[1] // 2]
        return coefficients, size

    def focal_scan(self, coefficients, size, Nstep, initial_c3, final_c3):
        img_size = 2 * self.rpupil
        y = np.zeros((Nstep, img_size, img_size))

        for i in range(Nstep):
            coefficients[3] = initial_c3 + i * (final_c3 - initial_c3) / (Nstep - 1)
            _, _, psf_image = self.find_rf_from_coefs(coefficients, size)

            x_center, y_center = size[0] // 2, size[1] // 2
            cropped = psf_image[
                      x_center - self.rpupil:x_center + self.rpupil,
                      y_center - self.rpupil:y_center + self.rpupil
                      ]

            y[i] = cropped

            self.scanProgress.emit(str(int((i + 1) * 100/Nstep)))

        return y


if __name__ == "__main__":
    F = FourierManager()
    coefficients, size = F.test_params()

    phase = F.afficher_pupille(coefficients, size)
    mask = F.mask(size)
    image = F.complex_pupil(F.phase(coefficients, size), mask)
    rf, psf_diff_lim, psf_image = F.find_rf_from_coefs(coefficients, size)

    plt.figure()
    plt.imshow(phase.astype(np.uint8), cmap = "gray")

    plt.figure()
    plt.imshow(psf_diff_lim, cmap="gray")

    plt.figure()
    plt.imshow(psf_image, cmap="gray")

    """plt.figure()
    plt.imshow(F.MTF(image), cmap = "gray")

    plt.figure()
    plt.imshow(F.MTF(mask), cmap = "gray")

    plt.figure()
    lentille = F.lentille(mask, 0.05, 100)
    plt.imshow(lentille, cmap = "gray")"""

    N = 50
    x0 = 0.0499
    ini_c3 = -1.5
    fin_c3 = 1.5
    #coefficients = np.zeros(11)
    y = F.focal_scan(coefficients, size, N, ini_c3, fin_c3)[:, F.rpupil, :]
    plt.figure()
    plt.imshow(y, cmap="gray")

    plt.show()