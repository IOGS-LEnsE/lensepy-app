import numpy as np
import matplotlib.pyplot as plt

def zernike_coefficient(surface, Z_nm, mask):
    """Calcule un coefficient de Zernike à partir d'une surface donnée."""
    return np.sum(surface * Z_nm * mask) / np.sum(Z_nm**2 * mask)

# Définition de la grille
N, M = 200, 500  # Taille de la grille
x = np.linspace(-1, 1, N)
y = np.linspace(-1, 1, M)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)
mask = R <= 1  # Pupille circulaire


# Création d'une surface avec un tilt (pente)
tilt_x = -0.2  # Amplitude du tilt en x
tilt_y = 0.5  # Amplitude du tilt en y
surface = tilt_x * X + tilt_y * Y + np.exp(-5 * R**2) + 0.8 * (2 * R**2 - 1)
surface = surface * mask


# Définition des polynômes de Zernike pour le tilt
Z_1m1 = X * mask  # Tilt en x
Z_11 = Y * mask  # Tilt en y

# Calcul des coefficients de tilt
a_1m1 = zernike_coefficient(surface, Z_1m1, mask)
a_11 = zernike_coefficient(surface, Z_11, mask)

# Reconstruction de l'aberration (tilt)
surface_aberration = a_1m1 * Z_1m1 + a_11 * Z_11

# Correction de la surface
surface_corrigée = surface - surface_aberration

# Affichage des résultats
fig, axs = plt.subplots(1, 3, figsize=(12, 4))
im1 = axs[0].imshow(surface * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[0].set_title("Surface aberrations")
fig.colorbar(im1, ax=axs[0])

im2 = axs[1].imshow(surface_aberration, extent=(-1, 1, -1, 1), cmap='jet')
axs[1].set_title("Correction appliquée")
fig.colorbar(im2, ax=axs[1])

im3 = axs[2].imshow(surface_corrigée * mask, extent=(-1, 1, -1, 1), cmap='jet')
axs[2].set_title("Surface corrigée")
fig.colorbar(im3, ax=axs[2])

plt.show()
