import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftshift
from scipy.signal import windows

# Paramètres
N = 1024  # Taille de la grille
pupil_radius = 128  # Rayon de la pupille (en pixels)
lambda_ = 550e-9  # Longueur d'onde (m)
k = 2 * np.pi / lambda_  # Nombre d'onde

# Grille de coordonnées
x = np.linspace(-N/2, N/2, N)
y = np.linspace(-N/2, N/2, N)
X, Y = np.meshgrid(x, y)

# Pupille circulaire centrée
pupil = (X**2 + Y**2) <= pupil_radius**2

# Fenêtre de pondération (Hanning) pour atténuer les discontinuités aux bords
window = windows.hann(N)
window = window[:, np.newaxis] * window[np.newaxis, :]  # Fenêtre 2D
pupil_windowed = pupil * window

# --- Système parfait (sans aberration) ---
phase_perfect = np.zeros((N, N), dtype=np.float64)
U_perfect = pupil_windowed.astype(complex) * np.exp(1j * phase_perfect)

# --- Système avec astigmatisme ---
rho = np.sqrt(X**2 + Y**2) / pupil_radius
rho[pupil == False] = 0
theta = np.arctan2(Y, X)

A_a = 50 * k  # Amplitude de l'astigmatisme
astigmatism_phase = np.zeros((N, N), dtype=np.float64)
astigmatism_phase[pupil] = A_a * (rho[pupil]**2) * np.cos(theta[pupil])**2
U_astigmatism = pupil_windowed.astype(complex) * np.exp(1j * astigmatism_phase)

# --- Zéro-padding ---
pad_factor = 4
U_padded_perfect = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_perfect[N//2:N//2+N, N//2:N//2+N] = U_perfect
U_padded_astigmatism = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_astigmatism[N//2:N//2+N, N//2:N//2+N] = U_astigmatism

# --- Calcul des PSF ---
PSF_perfect = np.abs(fftshift(fft2(U_padded_perfect)))**2
PSF_astigmatism = np.abs(fftshift(fft2(U_padded_astigmatism)))**2

# --- Calcul du rapport de Strehl ---
strehl_astigmatism = PSF_astigmatism.max() / PSF_perfect.max()
print(f"Rapport de Strehl (Astigmatisme) : {strehl_astigmatism:.3f}")

# --- Normalisation pour affichage ---
PSF_perfect /= PSF_perfect.max()
PSF_astigmatism /= PSF_astigmatism.max()

# --- Extraction de la partie centrale ---
center = pad_factor*N // 2
half_width = N // 2
PSF_center_perfect = PSF_perfect[center-half_width:center+half_width, center-half_width:center+half_width]
PSF_center_astigmatism = PSF_astigmatism[center-half_width:center+half_width, center-half_width:center+half_width]

# --- Affichage avec échelle adaptée ---
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# Phase
im0 = axs[0].imshow(astigmatism_phase, cmap='twilight')
axs[0].set_title('Phase - Astigmatisme')
plt.colorbar(im0, ax=axs[0], label='Radians')

# PSF (échelle adaptée)
vmin, vmax = 1e-4, 1  # Limites pour éviter la saturation
axs[1].imshow(PSF_center_perfect, cmap='hot', vmin=vmin, vmax=vmax)
axs[1].set_title('PSF - Système parfait')
axs[2].imshow(PSF_center_astigmatism, cmap='hot', vmin=vmin, vmax=vmax)
axs[2].set_title(f'PSF - Astigmatisme (Strehl = {strehl_astigmatism:.2f})')

plt.tight_layout()
plt.show()

# --- Comparaison 1D des PSF ---
plt.figure(figsize=(8, 5))
plt.plot(PSF_center_perfect[N//2, :], label='Système parfait')
plt.plot(PSF_center_astigmatism[N//2, :], label=f'Astigmatisme (Strehl = {strehl_astigmatism:.2f})')
plt.title('Comparaison 1D des PSF')
plt.xlabel('Position (pixels)')
plt.ylabel('Intensité normalisée')
plt.legend()
plt.grid()
plt.show()
