# -*- coding: utf-8 -*-
"""*hariharan_algorithm.py* file.

This file is attached to a 1st year of engineer training labwork in photonics.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian Mendes (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors


def hariharan_algorithm(intensity: list[np.ndarray], mask: np.ndarray = None) -> np.ndarray:
    """
    Apply the Hariharan phase demodulation algorithm to a set of intensity measurements.

    Parameters
    ----------
    intensity : list[np.ndarray]
        First intensity measurement, I_1 = I_0 * (1 + C * cos(phi)).
        Second intensity measurement, I_2 = I_0 * (1 + C * cos(phi + π/2)).
        Third intensity measurement, I_3 = I_0 * (1 + C * cos(phi + π)).
        Fourth intensity measurement, I_4 = I_0 * (1 + C * cos(phi + 3π/2)).
        Fifth intensity measurement, I_5 = I_0 * (1 + C * cos(phi + 2π)).

    Returns
    -------
    np.ndarray
        The demodulated phase phi array.

    Notes
    -----
    This function calculates the demodulated phase using the Hariharan algorithm, which is a method for phase recovery in interferometry.

    The five intensity measurements are taken with phase shifts of π/2 between them, specifically:
    - I_1 = I_0(1 + C * cos(phi))
    - I_2 = I_0(1 + C * cos(phi + pi/2))
    - I_3 = I_0(1 + C * cos(phi + pi))
    - I_4 = I_0(1 + C * cos(phi + 3*pi/2))
    - I_5 = I_0(1 + C * cos(phi + 2*pi))

    The returned phase values are in radians.

    This algorithm was originally published in:
    P. Hariharan, B. F. Oreb, and T. Eiju, "Digital phase-shifting interferometry: a simple error-compensating phase calculation algorithm," Appl. Opt. 26, 2504-2506 (1987).
    Available at: https://opg.optica.org/ao/fulltext.cfm?uri=ao-26-13-2504&id=168363
    """
    num = 2 * (intensity[3] - intensity[1])
    denum = 2 * intensity[2] - intensity[4] - intensity[0]
    if mask is not None:
        return np.arctan2(num, denum) * mask
    else:
        return np.arctan2(num, denum)


def display_3D_surface(Z: np.ndarray, mask: np.ndarray = None, size: int = 25, title: str = ''):
    """Display a 3D surface."""
    # Array for displaying data on 3D projection
    x = np.arange(Z.shape[1])
    y = np.arange(Z.shape[0])
    X, Y = np.meshgrid(x, y)

    # Display of the surface
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # [400:1200, 750:1900]
    if mask is not None:
        ZZ = np.ma.masked_array(Z, mask=~mask)
        max_ZZ = ZZ.max()
        min_ZZ = ZZ.min()
        norm = colors.Normalize(vmin=min_ZZ, vmax=max_ZZ)
        color_map = cm.magma(norm(Z))
        color_map[..., -1] = np.where(mask == 0, 0, 1)
        surface = ax.plot_surface(X, Y, Z, facecolors=color_map, shade=False,
                                  rstride=size, cstride=size)
        ax.set_zlim(min_ZZ, max_ZZ)
        mappable = cm.ScalarMappable(norm=norm, cmap='magma')
        mappable.set_array(Z)
        cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10)
    else:
        surface = ax.plot_surface(X, Y, Z, cmap='magma', shade=False,
                                  rstride=size, cstride=size)
        cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
    ax.set_title(title)

    cbar.set_label(r'Default magnitude ($\lambda$)')
    plt.show()


if __name__ == '__main__':
    X = np.linspace(-3, 3, 100)
    Y = np.linspace(-4, 5, 200)
    X, Y = np.meshgrid(X, Y)
    Z = np.sqrt(X ** 2 + Y ** 2)

    mask = np.zeros_like(Z)
    mask[80:120, 20:50] = 1
    mask = mask < 0.5

    plt.figure()
    plt.imshow(mask)
    plt.colorbar()

    display_3D_surface(Z, mask, size=10)
