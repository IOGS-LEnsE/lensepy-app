# -*- coding: utf-8 -*-
"""
File: zernike_coefficients.py

This file is associated with a first-year and second year engineering lab in photonics.
First-year subject: http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf
Second-year subject: https://lense.institutoptique.fr/s8-aberrations/

Development details for this interface:
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import matplotlib.pyplot as plt
import numpy as np
import math
from models.dataset import DataSetModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.phase import PhaseModel


aberrations_type = {
    "piston": [0],
    "tilt": [1, 2],
    "defocus": [3],
    "astig3" : [4, 5],
    "coma3" : [6, 7],
    "sphere3" : [8],
    "trefoil5" : [9, 10],
    "astig5" : [11, 12],
    "coma5" : [13, 14],
    "sphere5" : [15],
    "quadra7" : [16, 17],
    "trefoil7" : [18, 19],
    "astig7" : [20, 21],
    "coma7" : [22, 23],
    "sphere7" : [24],
    "penta9" : [25, 26],
    "quadra9" : [27, 28],
    "trefoil9" : [29, 30],
    "astig9" : [31, 32],
    "coma9" : [33, 34],
    "sphere9" : [35],
    "sphere11" : [36]
}

aberrations_list = [
    "piston",
    "tilt",
    "defocus",
    "astig3" ,
    "coma3",
    "sphere3",
    "trefoil5",
    "astig5",
    "coma5",
    "sphere5",
    "quadra7",
    "trefoil7",
    "astig7",
    "coma7",
    "sphere7",
    "penta9",
    "quadra9",
    "trefoil9",
    "astig9",
    "coma9",
    "sphere9",
    "sphere11" 
]

COEFFICIENTS_ROUND_RANGE = 4 # decimals


class Zernike:
    """
    Notes
    -----
    For more information on Zernike polynomials and their coefficients, refer to:
    https://iopscience.iop.org/article/10.1088/2040-8986/ac9e08/pdf
    """

    def __init__(self, phase: "PhaseModel", max_order:int = 36):
        self.max_order: int = max_order
        self.phase: "PhaseModel" = phase
        self.surface = self.phase.get_unwrapped_phase()
        self.lambda_value = 0       # Value of the wavelength
        self.lambda_nm = False      # If False, display in lambda else in um

        self.corrected_phase = None
        self.coeff_counter = 0
        self.coeff_calculated = False  # Zernike coefficients are calculated
        self.coeff_list = [None] * (self.max_order + 1)
        self.polynomials = [None] * (self.max_order + 1)
        self.X = None
        self.Y = None
        self.pow1 = None
        self.pow2 = None

        if self.init_data():
            print("Data Ok")

    def set_phase(self, phase) -> bool:
        """
        Set the phase to process.
        :param phase: Phase to process.
        :return: True if the data is initialized.
        """
        self.phase = phase
        self.reset_coeffs()
        return self.init_data()

    def set_wedge_factor(self, wedge_factor: float):
        """
        Set the wedge factor for displaying data.
        :param wedge_factor: Value of the wedge factor.
        """
        self.phase.set_wedge_factor(wedge_factor)

    def init_data(self) -> bool:
        """
        Initialize data.
        :return: True if initialization procedure is correctly done.
        """
        if self.phase.is_analysis_ready():
            self.surface = self.phase.get_unwrapped_phase()
            # Dimensions of the surface
            a, b = self.surface.shape

            # Creating coordinate grids
            x = np.linspace(-1, 1, b)
            y = np.linspace(-1, 1, a)
            self.X, self.Y = np.meshgrid(x, y)
            self.pow1 = (self.X**2 - self.Y**2)
            self.pow2 = (self.X**2 + self.Y**2)

            self.corrected_phase = np.zeros_like(self.surface)
            return True
        return False

    def process_cartesian_polynomials(self, noll_index: int) -> np.ndarray:
        '''Normalized (RMS) Zernike coefficients calculation.'''
        if noll_index == 0:     # Piston
            return np.ones_like(self.X)
        elif noll_index == 1:   # x-Tilt
            return 2*self.X
        elif noll_index == 2:   # y-Tilt
            return 2*self.Y
        elif noll_index == 3:   # defocus
            return np.sqrt(3)*(2*self.pow2 - 1)
        ## ORDER 3
        elif noll_index == 4:   # defocus / 45d primary astig
            return 2*np.sqrt(6)*(self.X * self.Y)
        elif noll_index == 5:   # defocus / 0d primary astig
            return np.sqrt(6)*self.pow1
        elif noll_index == 6:   # Primary coma
            return np.sqrt(8)*self.Y*(3*self.pow2-2)
        elif noll_index == 7:   # Primary coma
            return np.sqrt(8)*self.X*(3*self.pow2-2)
        elif noll_index == 8:   # Primary coma
            return np.sqrt(8)*self.Y*(3*self.X**2 - self.Y**2)
        ## ORDER 5
        elif noll_index == 9:   # Primary coma
            return np.sqrt(8)*self.X*(self.X**2 - 3*self.Y**2)
        elif noll_index == 10:   # Primary Spherical Aber.
            return np.sqrt(5)*(6*self.pow2**2 - 6*self.pow2 + 1)
        elif noll_index == 11:   # Primary Spherical Aber.
            return np.sqrt(10)*self.pow1*(4*self.pow2 - 3)
        elif noll_index == 12:   # Primary Spherical Aber.
            return 2*np.sqrt(10)*self.X*self.Y*(4*self.pow2 - 3)
        elif noll_index == 13:   # Primary Spherical Aber.
            return np.sqrt(10)*(self.pow2**2 - 8*self.X**2*self.Y**2)
        elif noll_index == 14:   # Primary Spherical Aber.
            return 4*np.sqrt(10)*self.X*self.Y*self.pow1
        elif noll_index == 15:   # Secondary coma
            return np.sqrt(12)*self.X*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        ## ORDER 7
        elif noll_index == 16:   # Secondary coma
            return np.sqrt(12)*self.Y*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        elif noll_index == 17:   # Secondary coma
            return np.sqrt(12)*self.X*(self.X**2 - 3*self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 18:   # Secondary coma
            return np.sqrt(12)*self.Y*(3 * self.X**2 - self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 19:   # Secondary coma
            return np.sqrt(12)*self.X*(16*self.X**4 - 20*self.X**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 20:   # Secondary coma
            return np.sqrt(12)*self.Y*(16*self.Y**4 - 20*self.Y**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 21:   # Secondary Spherical Aber.
            return np.sqrt(7)*(20*self.pow2**3 - 30*self.pow2**2 + 12*self.pow2 - 1)
        elif noll_index == 22:   # Secondary Spherical Aber.
            return 2*np.sqrt(14)*self.X*self.Y*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 23:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.pow1*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 24:   # Secondary Spherical Aber.
            return 4*np.sqrt(14)*self.X*self.Y*self.pow1*(6*self.pow2 - 5)
        ## ORDER 9
        elif noll_index == 25:   # Secondary Spherical Aber.
            return np.sqrt(14)*(self.pow2**2 - 8*self.X**2*self.Y*2)*(6*self.pow2 - 5)
        elif noll_index == 26:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.X*self.Y*(32*self.X**4 - 32*self.X**2*self.pow2 + 6*self.pow2**2)
        elif noll_index == 27:   # Secondary Spherical Aber.
            return np.sqrt(14)*(32*self.X**6 - 48*self.X**4*self.pow2 + 18*self.X**2*self.pow2**2 - self.pow2**3)

        elif noll_index == 28:   # Secondary Spherical Aber.
            return 4*self.Y*(35*self.pow2**3-60*self.pow2**2+30*self.pow2-4)
        elif noll_index == 29:   # Secondary Spherical Aber.
            return 4*self.X*(35*self.pow2**3-60*self.pow2**2+30*self.pow2-4)
        elif noll_index == 30:   # Tertiary y-Coma
            return 4*self.Y*(3*self.X**2-self.Y**2)*(21*self.pow2**2-30*self.pow2+10)
        elif noll_index == 31:   # Tertiary x-Coma
            return 4*self.X*(self.X**2-3*self.Y**2)*(21*self.pow2**2-30*self.pow2+10)
        elif noll_index == 32:   # Secondary Spherical Aber.
            return 4*(4*self.X**2*self.Y*self.pow1+self.Y*self.pow2**2-8*self.X**2*self.Y**3)*(7*self.pow2-6)
        elif noll_index == 33:   # Secondary Spherical Aber.
            return 4*(self.X*self.pow2**2-8*self.X**3*self.Y**2-4*self.X*self.Y**2*self.pow1)*(7*self.pow2-6)
        elif noll_index == 34:   # Secondary Spherical Aber.
            return 8*self.X**2*self.Y*(3*self.pow2**2-16*self.X**2*self.Y**2)+4*self.Y*self.pow1*(self.pow2**2-16*self.X**2*self.Y**2)
        elif noll_index == 35:   # Secondary Spherical Aber.
            return 4*self.X*self.pow1*(self.pow2**2-16*self.X**2*self.Y**2)-8*self.X*self.Y**2*(3*self.pow2**2-16*self.X**2*self.Y**2)

        ## ORDER 11
        elif noll_index == 36: # Tertiary spherical
            return 3*(70*self.pow2**4-140*self.pow2**3 +90*self.pow2**2-20*self.pow2+1)

    def process_zernike_coefficient(self, order: int) -> np.ndarray:
        if order <= self.max_order:
            if self.coeff_list[order] is None:
                Z_nm = self.process_cartesian_polynomials(order)
                # Mask NaN values
                valid_mask = ~np.isnan(self.surface)
                surface_filtered = self.surface[valid_mask]
                Z_nm_filtered = Z_nm[valid_mask]

                num = np.sum(surface_filtered * Z_nm_filtered)
                den = np.sum(Z_nm_filtered ** 2)
                self.coeff_list[order] = num / den
        else:
            return None

    def process_surface_correction(self, aberrations: list[str]):
        self.corrected_phase = np.zeros_like(self.surface)
        for k, type_ab in enumerate(aberrations):
            coeffs = aberrations_type[type_ab]
            for c in coeffs:
                if self.coeff_list[c] is None:
                    self.process_zernike_coefficient(c)
                self.corrected_phase += self.coeff_list[c] * self.process_cartesian_polynomials(c)
        # Correction de la surface
        new_surface = self.surface - self.corrected_phase
        return self.corrected_phase, new_surface
    
    def phase_correction(self, corrected_coeffs: list[float]):
        self.corrected_phase = np.zeros_like(self.surface)
        for i, c in enumerate(corrected_coeffs):
            self.corrected_phase += c * self.process_cartesian_polynomials(i)
        # Correction de la surface
        new_surface = self.surface - self.corrected_phase

        return self.corrected_phase, new_surface

    def get_coeff_counter(self) -> int:
        """
        Get the calculated coefficients counter.
        :return: Number of coefficients already calculated.
        """
        return self.coeff_counter

    def get_coeffs(self):
        """
        Return an array of the coefficients.
        :return: 1D array with the coefficients.
        """
        coeffs = -np.array(self.coeff_list.copy()) * self.phase.get_wedge_factor()
        if self.lambda_nm:
            coeffs = coeffs * self.lambda_value * 1e-3 # nm -> um
        return coeffs

    def reset_coeffs(self):
        """Reset all the coefficients."""
        self.corrected_phase = None
        self.coeff_counter = 0
        self.coeff_calculated = False
        self.coeff_list = [None] * (self.max_order + 1)
        self.polynomials = [None] * (self.max_order + 1)
        self.X = None
        self.Y = None
        self.pow1 = None
        self.pow2 = None

    def update_lambda(self, value: int = None, um_check: bool = False):
        """
        Update coefficients value depending on displaying lambda in um or not.
        :param value: Value of the wavelength.
        :param um_check: True to display in um, False in lambda.
        """
        self.lambda_nm = um_check
        if value is not None:
            self.lambda_value = value


    def convert_to_seidel(self):
        """
        Process Seidel coefficients from Zernike coefficients. Order 3.

        Actual convention:

        Aberration  | Amplitude     | Angle
        ---------------------------------------------------
        Tilt        | √(C3²+C2²)    | arctan(C3/C2)
        Defocus     | 2*C4          |    no
        Astigmatism | √(C5²+C6²)    | 1/2 * arctan(C6/C5)
        Coma        | 3*√(C8²+C7²)  | arctan(C8/C7)
        Sph. Ab.    | 6*C11         |    no
        """
        c = self.coeff_list
        state = True
        for k in range(11):
            if c[k] is None:
                state = False

        if state:
            # Tilt
            tilt_magnitude = np.sqrt(c[3]**2 + c[2]**2)
            tilt_angle = np.rad2deg(np.arctan2(c[3], c[2]))

            # Defocus
            defocus_amplitude = 2*c[4]

            # Astigmatism
            astigmatism_magnitude = 2 * np.sqrt(c[6]**2+c[5]**2)
            astigmatism_angle = np.rad2deg(1/2* np.arctan2(c[6], c[5]))

            # Coma
            coma_amplitude = 3 * np.sqrt(c[7]**2+c[8]**2)
            coma_angle = np.rad2deg(np.arctan2(c[8], c[7]))

            # Spherical aberration
            sp_ab_magnitude = 6*c[11]

            # Round
            tilt_magnitude = np.round(tilt_magnitude, COEFFICIENTS_ROUND_RANGE)
            tilt_angle = np.round(tilt_angle, COEFFICIENTS_ROUND_RANGE)
            defocus_amplitude = np.round(defocus_amplitude, COEFFICIENTS_ROUND_RANGE)
            astigmatism_magnitude = np.round(astigmatism_magnitude, COEFFICIENTS_ROUND_RANGE)
            astigmatism_angle = np.round(astigmatism_angle, COEFFICIENTS_ROUND_RANGE)
            coma_amplitude = np.round(coma_amplitude, COEFFICIENTS_ROUND_RANGE)
            coma_angle = np.round(coma_angle, COEFFICIENTS_ROUND_RANGE)
            sp_ab_magnitude = np.round(sp_ab_magnitude, COEFFICIENTS_ROUND_RANGE)

            # Return dict
            result = {'tilt_mag': tilt_magnitude, 'tilt_ang': tilt_angle,
                      'defocus_mag': defocus_amplitude, 'sphere_mag': sp_ab_magnitude,
                      'astig_mag': astigmatism_magnitude, 'astig_ang': astigmatism_angle,
                      'coma_mag': coma_amplitude_, 'coma_ang': coma_angle}
            return result
        else:
            return {}



def display_3_figures(init, zer, corr):
    """Displaying results."""
    vmin = np.nanmin([init.min(), corr.min()])
    vmax = np.nanmax([init.max(), corr.max()])

    init = np.ma.array(init, mask=np.isnan(init))
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    im1 = axs[0].imshow(init, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[0].set_title("Initial Surface")
    fig.colorbar(im1, ax=axs[0])

    im2 = axs[1].imshow(zer, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[1].set_title("Correction")
    fig.colorbar(im2, ax=axs[1])

    corr = np.ma.array(corr, mask=np.isnan(corr))
    im3 = axs[2].imshow(corr, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[2].set_title("Corrected surface")
    fig.colorbar(im3, ax=axs[2])
    plt.show()


def zernike_radial(n, m, r):
    """ Calcule la composante radiale des polynômes de Zernike. """
    R = np.zeros_like(r)
    for k in range((n - abs(m)) // 2 + 1):
        c = (-1)**k * math.factorial(n - k) / (
            math.factorial(k) *
            math.factorial((n + abs(m)) // 2 - k) *
            math.factorial((n - abs(m)) // 2 - k)
        )
        R += c * r**(n - 2*k)
    return R


def zernike(n, m, rho, theta):
    """ Calcule un polynôme de Zernike. """
    if m >= 0:
        return zernike_radial(n, m, rho) * np.cos(m * theta)
    else:
        return zernike_radial(n, -m, rho) * np.sin(-m * theta)


def elliptic_mask(image, cx=0, cy=0, a=0.5, b=0.5):
    """Create elliptic mask on an image.
    :param image: initial image to mask
    :param cx: X-axis center
    :param cy: Y-axis center
    :param a: X-axis dimension
    :param b: Y-axis dimension
    """
    height, width = image.shape
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    return ((X - cx) ** 2) / a ** 2 + ((Y - cy) ** 2) / b ** 2 < 1


if __name__ == "__main__":
    '''
    # Grid definition
    N, M = 256, 128  # Taille de la grille
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, M)
    X, Y = np.meshgrid(x, y)
    # Circular mask
    R = np.sqrt(X ** 2 + Y ** 2)
    theta = np.arctan2(Y, X)
    mask = R < 1

    # Surface creation
    tilt_x = -0.27
    tilt_y = 0.35
    surface = tilt_x * X + tilt_y * Y #+ np.exp(-3 * R ** 2) + 0.48 * (2 * R ** 2 - 1)

    mask = elliptic_mask(surface, 0.2, 0, a=0.4)

    # Coma horizontale (Z3^1) et verticale (Z3^-1)
    coma_horizontal = zernike(3, 1, R, theta)  # Z3^1
    coma_vertical = zernike(3, -1, R, theta)  # Z3^-1
    surface += coma_vertical #+coma_vertical

    surface[~mask] = np.nan
    '''
    from models.phase import PhaseModel, process_statistics_surface
    from utils.dataset_utils import read_mat_file, split_3d_array
    data = read_mat_file("../_data/test3.mat")
    images_mat = data['Images']
    images = split_3d_array(images_mat)

    mask = data['Masks'].squeeze()
    mask = mask.astype(bool)

    plt.figure()
    plt.imshow(images[0]*mask)
    plt.show()


    ### Class test
    data_set = DataSetModel(5)
    print(f'Set ok ? {data_set.add_set_images(images)}')
    data_set.add_mask(mask)
    phase = PhaseModel(data_set)
    phase.prepare_data()
    phase.process_wrapped_phase()
    wrapped = phase.get_wrapped_phase()
    plt.figure()
    plt.imshow(wrapped, cmap='gray')
    plt.colorbar()

    phase.process_unwrapped_phase()
    surface = phase.get_unwrapped_phase()
    plt.figure()
    plt.imshow(surface, cmap='gray')
    plt.colorbar()
    plt.show()

    zer = Zernike(phase)
    mask_d, _, _ = data_set.get_global_cropped_mask()

    phase.unwrapped_phase[~mask_d] = np.nan
    zer.set_phase(phase)

    ab_list = ['tilt']  #,'defocus'] #,'coma1','sphere1','coma2','sphere2']

    correction, new_image = zer.process_surface_correction(ab_list)

    print(f'Init = {process_statistics_surface(surface)}')
    print(f'End = {process_statistics_surface(new_image)}')

    display_3_figures(surface, correction, new_image)






