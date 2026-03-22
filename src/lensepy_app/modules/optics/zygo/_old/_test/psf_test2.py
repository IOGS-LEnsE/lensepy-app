import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fftshift, fft2
from scipy.ndimage import zoom

# --- Paramètres de base ---
N = 256  # taille de la grille
radius = N // 4  # rayon de la pupille
wavelength = 632e-9  # en mètres
D = 10e-3 # diamètre de l'ouverture (10 mm)

# --- Coordonnées polaires centrées ---
y, x = np.indices((N, N)) - N // 2
r = np.sqrt(x**2 + y**2) / radius
theta = np.arctan2(y, x)

# --- Pupille circulaire ---
pupil = r <= 1

# --- Fonctions de Zernike simples (tilt, coma, astigmatisme, spherical) ---
def zernike(n, m, r, theta):
    if (n, m) == (1, -1): return 2*r*np.sin(theta)  # Tilt Y
    if (n, m) == (1, 1): return 2*r*np.cos(theta)   # Tilt X
    if (n, m) == (2, 0): return np.sqrt(3)*(2*r**2 - 1)  # Defocus
    if (n, m) == (2, -2): return np.sqrt(6)*r**2*np.sin(2*theta)  # Astigmatism
    if (n, m) == (3, 1): return np.sqrt(8)*(3*r**3 - 2*r)*np.cos(theta)  # Coma X
    if (n, m) == (4, 0): return np.sqrt(5)*(6*r**4 - 6*r**2 + 1)  # Spherical
    return np.zeros_like(r)

# --- Génération du front d’onde avec quelques aberrations ---
W = 0.05 * zernike(3, 1, r, theta)

W *= pupil  # masque de la pupille


# --- Fonction de transfert (optique) ---
phase = np.exp(1j * 2 * np.pi * W / wavelength)
field = pupil * phase

# --- PSF (magnitude au carré de la FFT) ---
PSF = np.abs(fftshift(fft2(field)))**2
PSF /= PSF.max()

# --- MTF (magnitude de la FFT de la PSF) ---
MTF = np.abs(fftshift(fft2(PSF)))
MTF /= MTF.max()

# --- Énergie encerclée ---
def energie_encerclée(psf, center=None):
    if center is None:
        center = np.array(psf.shape) // 2
    y, x = np.indices(psf.shape)
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    r_sorted = np.argsort(r.flat)
    psf_sorted = psf.flat[r_sorted]
    r_sorted_vals = r.flat[r_sorted]
    cum_energy = np.cumsum(psf_sorted)
    cum_energy /= cum_energy[-1]
    return r_sorted_vals, cum_energy

rvals, ec = energie_encerclée(PSF)

# --- Affichages ---
fig, axs = plt.subplots(2, 2, figsize=(10, 10))

axs[0, 0].imshow(W * pupil, cmap='RdBu', extent=[-1, 1, -1, 1])
axs[0, 0].set_title("Front d'onde (λ)")
axs[0, 0].set_xlabel("x")
axs[0, 0].set_ylabel("y")

axs[0, 1].imshow(PSF, cmap='inferno')
axs[0, 1].set_title("PSF")
axs[0, 1].set_xlabel("x")
axs[0, 1].set_ylabel("y")

axs[1, 0].imshow(MTF, cmap='viridis')
axs[1, 0].set_title("MTF")
axs[1, 0].set_xlabel("fx")
axs[1, 0].set_ylabel("fy")

axs[1, 1].plot(rvals, ec)
axs[1, 1].set_xlim(0, 50)
axs[1, 1].set_title("Énergie encerclée")
axs[1, 1].set_xlabel("Rayon (pixels)")
axs[1, 1].set_ylabel("Énergie cumulée")

plt.tight_layout()
plt.show()
