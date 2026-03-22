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

from numpy import sqrt, sin, cos
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from timeit import default_timer as timer

if __name__ == '__main__':
    from polar_cartesian_transformations import *
else:
    from polar_cartesian_transformations import *

PI = np.pi

def polar_zernike_polynomials(u: np.ndarray, phi: np.ndarray, osa_index: int) -> np.ndarray:
    """
    Calculate the Zernike polynomial coefficient for given polar coordinates and OSA index.

    Parameters
    ----------
    u : numpy.ndarray
        Radial coordinates, where 0 <= u <= 1.
    phi : numpy.ndarray
        Angular coordinates in radians.
    osa_index : int
        The OSA (Optical Society of America) index of the Zernike polynomial.

    Returns
    -------
    numpy.ndarray
        The values of the Zernike polynomial coefficient for the given u, phi, and osa_index.
        Returns 0 for points where u > 1.

    Notes
    -----
    For more information on Zernike polynomials and their coefficients, refer to:
    https://iopscience.iop.org/article/10.1088/2040-8986/ac9e08/pdf
    """
    # Handle points outside the pupil (where u > 1)
    u[u > 1] = 0
    
    if osa_index == 0:
        return np.ones_like(u)
    
    # ---------------------------------------------------------------
    
    elif osa_index == 1:
        return 2 * u * sin(phi)

    elif osa_index == 2:
        return 2 * u * cos(phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 3:
        return sqrt(6) * u**2 * sin(2 * phi)
    
    elif osa_index == 4:
        return sqrt(3) * (2* u**2 - 1)

    elif osa_index == 5:
        return sqrt(6) * u**2 * cos(2 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 6:
        return sqrt(8) * u**3 * sin(3 * phi)

    elif osa_index == 7:
        return sqrt(8) * (3 * u**3 - 2 * u) * sin(phi)

    elif osa_index == 8:
        return sqrt(8) * (3 * u**3 - 2 * u) * cos(phi)

    elif osa_index == 9:
        return sqrt(8) * u**3 * cos(3 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 10:
        return sqrt(10) * u**4 * sin(4 * phi)

    elif osa_index == 11:
        return sqrt(10) * (4 * u**4 - 3 * u**2) * sin(2 * phi)

    elif osa_index == 12:
        return sqrt(5) * (6 * u**4 - 6 * u**2 + 1)

    elif osa_index == 13:
        return sqrt(10) * (4 * u**4 - 3 * u**2) * cos(2 * phi)

    elif osa_index == 14:
        return sqrt(10) * u**4 * cos(4 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 15:
        return sqrt(12) * u**5 * sin(5 * phi)

    elif osa_index == 16:
        return sqrt(12) * (5 * u**5 - 4 * u**3) * sin(3 * phi)

    elif osa_index == 17:
        return sqrt(12) * (10 * u**5 - 12 * u**3 + 3 * u) * sin(phi)

    elif osa_index == 18:
        return sqrt(12) * (10 * u**5 - 12 * u**3 + 3 * u) * cos(phi)

    elif osa_index == 19:
        return sqrt(12) * (5 * u**5 - 4 * u**3) * cos(3 * phi)

    elif osa_index == 20:
        return sqrt(12) * u**5 * cos(5 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 21:
        return sqrt(14) * u**6 * sin(6 * phi)

    elif osa_index == 22:
        return sqrt(14) * (6 * u**6 - 5 * u**4) * sin(4 * phi)

    elif osa_index == 23:
        return sqrt(14) * (15 * u**6 - 20 * u**4 + 6 * u**2) * sin(2 * phi)

    elif osa_index == 24:
        return sqrt(7) * (20 * u**6 - 30 * u**4 + 12 * u**2 - 1)

    elif osa_index == 25:
        return sqrt(14) * (15 * u**6 - 20 * u**4 + 6 * u**2) * cos(2 * phi)

    elif osa_index == 26:
        return sqrt(14) * (6 * u**6 - 5 * u**4) * cos(4 * phi)

    elif osa_index == 27:
        return sqrt(14) * u**6 * cos(6 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 28:
        return 4 * u**7 * sin(7 * phi)

    elif osa_index == 29:
        return 4 * (7 * u**7 - 6 * u**5) * sin(5 * phi)

    elif osa_index == 30:
        return 4 * (21 * u**7 - 30 * u**5 + 10 * u**3) * sin(3 * phi)

    elif osa_index == 31:
        return 4 * (35 * u**7 - 60 * u**5 + 30 * u**3 - 4 * u) * sin(phi)

    elif osa_index == 32:
        return 4 * (35 * u**7 - 60 * u**5 + 30 * u**3 - 4 * u) * sin(phi)

    elif osa_index == 33:
        return 4 * (21 * u**7 - 30 * u**5 + 10 * u**3) * sin(3 * phi)

    elif osa_index == 34:
        return 4 * (7 * u**7 - 6 * u**5) * cos(5 * phi)

    elif osa_index == 35:
        return 4 * u**7 * sin(7 * phi)
    
    # ---------------------------------------------------------------

    elif osa_index == 36:
        return sqrt(18) * u**8 * sin(8 * phi)

    return 0

def cartesian_zernike_polynomials(x: np.ndarray, y: np.ndarray, osa_index: int) -> np.ndarray:
    """
    Calculate the Zernike polynomial coefficient for given Cartesian coordinates and OSA index.

    Parameters
    ----------
    x : numpy.ndarray
        Cartesian x coordinates.
    y : numpy.ndarray
        Cartesian y coordinates.
    osa_index : int
        The OSA (Optical Society of America) index of the Zernike polynomial.

    Returns
    -------
    numpy.ndarray
        The values of the Zernike polynomial coefficient for the given Cartesian coordinates (x, y)
        and OSA index.

    Notes
    -----
    This function converts Cartesian coordinates (x, y) to polar coordinates (u, phi),
    where u is the radial coordinate normalized to [0, 1] and phi is the angular coordinate in radians.
    It then calculates the Zernike polynomial coefficient using the polar coordinates.

    For more information on Zernike polynomials and their coefficients, refer to:
    https://iopscience.iop.org/article/10.1088/2040-8986/ac9e08/pdf
    """
    u, phi = cartesian_to_polar(x, y)  # Convert Cartesian to polar coordinates
    return polar_zernike_polynomials(u, phi, osa_index)

def get_zernike_coefficient(surface: np.ndarray, max_order: int = 3) -> np.ndarray:
    # Dimensions of the surface
    a, b = surface.shape
    
    # Creating coordinate grids
    x = np.linspace(-1, 1, b)
    y = np.linspace(-1, 1, a)
    X, Y = np.meshgrid(x, y)
    
    #surface = np.transpose(surface)
    
    # Converting to column vectors
    X = X.flatten()
    Y = Y.flatten()
    surface = surface.flatten()
    
    # Removing NaN values
    X = X[~np.isnan(surface)]
    Y = Y[~np.isnan(surface)]
    surface = surface[~np.isnan(surface)]

    # Normalizing the surface
    phi = surface # / (2 * PI)

    # Calculating the matrix M using polar_zernike_coefficients
    # m_(i,k) = Z_k(u_i, phi_i)
    M = np.zeros((len(phi), max_order))
    for i in range(0, max_order):
        M[:, i] = cartesian_zernike_polynomials(X, Y, i)

    # Calculating Zernike coefficients
    coeff_zernike = np.linalg.lstsq(M, phi, rcond=None)[0]
    #coeff_zernike = np.concatenate(([0], coeff_zernike))
    #coeff_zernike[np.abs(coeff_zernike) < limit] = 0  # removing insignificant coefficients

    return coeff_zernike.squeeze()

def get_polynomials_basis(x: np.ndarray, y: np.ndarray, max_order: int = 3) -> np.ndarray:
    """ Return Z_i(x, y) """
    polynomials = np.ones((len(x), max_order))
    for i in range(max_order):
        polynomials[:, i] = cartesian_zernike_polynomials(x, y, i)
    return polynomials

def remove_aberration(phase: np.ndarray, aberrations_considered: np.ndarray, coeffs=None, polynomials=None) -> np.ndarray:
    a, b = phase.shape
    normalized_phase = phase / (2 * PI)
    
    x = np.linspace(-1, 1, b)
    y = np.linspace(-1, 1, a)
    X, Y = np.meshgrid(x, y)

    print(len(aberrations_considered))

    if coeffs is None:
        coeffs = get_zernike_coefficient(normalized_phase, len(aberrations_considered))
    if polynomials is None:
        polynomials = get_polynomials_basis(X.flatten(), Y.flatten(), max_order=len(aberrations_considered))

    surface = polynomials.dot((aberrations_considered * coeffs))
    
    normalized_phase = normalized_phase - surface.reshape((a, b))
    
    return normalized_phase * 2 * PI, X, Y

if __name__ == '__main__':
    max_order = 5
    # Dimensions de l'image
    a, b = 100, 300

    # Définir une phase combinée avec piston, tilt et astigmatisme
    X, Y = np.meshgrid(np.linspace(-1, 1, b), np.linspace(-1, 1, a))

    # Piston
    phi_piston = np.ones((a, b)) * 5

    # Tilt
    phi_tilt = 3 * X
    phi_tilt += -2 * Y

    # Phase totale avec aberrations
    phi = phi_piston + phi_tilt

    # Appliquer la fonction pour retirer les aberrations
    aberrations_considered = np.zeros(max_order, dtype=int)
    aberrations_considered[:3] = 1
    print(aberrations_considered)

    corrected_phase, XX, YY = remove_aberration(phi, aberrations_considered)

    # Affichage de la phase initiale
    # Création de la figure et des sous-graphiques en 3D
    fig = plt.figure(figsize=(14, 6))

    # Graphique 1 : Phase initiale avec aberrations
    min_value = np.round(np.min(phi), 0) - 1
    max_value = np.round(np.max(phi), 0) + 1

    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    surf1 = ax1.plot_surface(XX, YY, phi, cmap='viridis')
    ax1.set_zlim([min_value, max_value])
    ax1.set_title('Phase initiale avec aberrations')
    fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

    # Graphique 2 : Phase corrigée sans aberrations
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    surf2 = ax2.plot_surface(XX, YY, corrected_phase, cmap='viridis')
    ax2.set_zlim([-1, 1])
    ax2.set_title('Phase corrigée sans aberrations')
    fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

    # Ajustement des paramètres de la figure
    fig.tight_layout()

    plt.show()