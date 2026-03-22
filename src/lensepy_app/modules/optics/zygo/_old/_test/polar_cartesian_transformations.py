# -*- coding: utf-8 -*-
"""
File: polar_cartesian_transformations.py

This file is associated with a first-year and second year engineering lab in photonics.
First-year subject: http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf
Second-year subject: https://lense.institutoptique.fr/s8-aberrations/

Development details for this interface:
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import numpy as np
from typing import Tuple

def polar_to_cartesian(u:np.ndarray, phi:np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert polar coordinates (u, phi) to Cartesian coordinates (x, y).

    Parameters
    ----------
    u : numpy.ndarray
        Radial coordinates, where 0 <= u <= 1.
    phi : numpy.ndarray
        Angular coordinates in radians.

    Returns
    -------
    numpy.ndarray
        Cartesian x coordinates corresponding to (u, phi).
    numpy.ndarray
        Cartesian y coordinates corresponding to (u, phi).
    """
    x = u * np.cos(phi)
    y = u * np.sin(phi)
    return x, y

def cartesian_to_polar(x:np.ndarray, y:np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert Cartesian coordinates (x, y) to polar coordinates (u, phi).

    Parameters
    ----------
    x : numpy.ndarray
        Cartesian x coordinates.
    y : numpy.ndarray
        Cartesian y coordinates.

    Returns
    -------
    numpy.ndarray
        Radial coordinates u, where 0 <= u <= 1.
    numpy.ndarray
        Angular coordinates phi in radians.
    """
    u = np.sqrt(x**2 + y**2)  # radial coordinate
    phi = np.arctan2(y, x)    # angular coordinate in radians
    
    # Normalize radial coordinate u to be within [0, 1]
    u = u / np.max(u)
    
    return u, phi

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    x = y = np.linspace(-1,1,100)
    X, Y = np.meshgrid(x, y)
    r, theta = cartesian_to_polar(X, Y)

    plt.figure()
    plt.subplot(2, 2, 1)
    plt.title(r'$x$')
    plt.imshow(X)
    plt.colorbar()

    plt.subplot(2, 2, 2)
    plt.title(r'$y$')
    plt.imshow(Y)
    plt.colorbar()

    plt.subplot(2, 2, 3)
    plt.title(r'$r$')
    plt.imshow(r)
    plt.colorbar()

    plt.subplot(2, 2, 4)
    plt.title(r'$\theta$')
    plt.imshow(theta)
    plt.colorbar()
    plt.show()