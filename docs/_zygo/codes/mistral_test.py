import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftshift
from scipy.signal import windows

# Paramètres
N = 1024 # Taille de la grille initiale
pad_factor = 4
pupil_radius = 128 # Rayon de la pupille (en pixels)
lambda_ = 632.8e-9  # Longueur d'onde (m)
focal_length = 1e-2  # Distance focale (m)
k = 2 * np.pi / lambda_  # Nombre d'onde

# Grille de coordonnées
x = np.linspace(-N/2, N/2, N)
y = np.linspace(-N/2, N/2, N)
X, Y = np.meshgrid(x, y)

# Pupille circulaire
pupil = (X**2 + Y**2) <= pupil_radius**2

window = windows.hann(N)
window = window[:, np.newaxis] * window[np.newaxis, :]  # Fenêtre 2D
pupil_w = pupil # * window

# --- Système parfait (sans aberration) ---
phase_perfect = np.zeros((N, N))
U_perfect = pupil_w * np.exp(1j * phase_perfect)

# --- Système avec défocus (amplitude augmentée) ---
defocus = 10 * lambda_  # Augmentation de l'amplitude
def_phase = np.zeros((N, N))
def_phase[pupil] = (k / (2 * focal_length**2)) * defocus * (X[pupil]**2 + Y[pupil]**2)
U_def = pupil_w * np.exp(1j * def_phase)

# --- Système avec coma (amplitude augmentée) ---
rho = np.sqrt(X**2 + Y**2) / pupil_radius  # Normalisé
theta = np.arctan2(Y, X)
A_c = 10 * lambda_ * k  # Augmentation de l'amplitude
coma_phase = np.zeros((N, N))
coma_phase[pupil] = A_c * (rho[pupil]**3) * np.cos(theta[pupil])
U_coma = pupil_w * np.exp(1j * coma_phase)

# --- Système avec aberration sphérique (3ème ordre) ---
A_s = 100 * k  # Amplitude de l'aberration sphérique (en radians)
spherical_phase = np.zeros((N, N), dtype=np.float64)
spherical_phase[pupil] = A_s * (rho[pupil]**4)  # Aberration sphérique (3ème ordre)
U_spherical = pupil_w * np.exp(1j * spherical_phase)

# --- Zéro-padding pour toutes les PSF ---

U_padded_perfect = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_perfect[N//2:N//2+N, N//2:N//2+N] = U_perfect
U_padded_def = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_def[N//2:N//2+N, N//2:N//2+N] = U_def
U_padded_coma = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_coma[N//2:N//2+N, N//2:N//2+N] = U_coma
U_padded_spher = np.zeros((pad_factor*N, pad_factor*N), dtype=complex)
U_padded_spher[N//2:N//2+N, N//2:N//2+N] = U_spherical

# --- Calcul des PSF SANS normalisation ---
PSF_perfect = np.abs(fftshift(fft2(U_padded_perfect)))**2
PSF_def = np.abs(fftshift(fft2(U_padded_def)))**2
PSF_coma = np.abs(fftshift(fft2(U_padded_coma)))**2
PSF_spherical = np.abs(fftshift(fft2(U_padded_spher)))**2

# --- Calcul du rapport de Strehl ---
strehl_def = PSF_def.max() / PSF_perfect.max()
strehl_coma = PSF_coma.max() / PSF_perfect.max()
strehl_spherical = PSF_spherical.max() / PSF_perfect.max()

print(f"Rapport de Strehl (Défocus) : {strehl_def:.3f}")
print(f"Rapport de Strehl (Coma) : {strehl_coma:.3f}")
print(f"Rapport de Strehl (Aberration sphérique) : {strehl_spherical:.3f}")

# --- Extraction de la partie centrale (pour affichage) ---
center = pad_factor*N // 2
half_width = N // 2
PSF_center_perfect = PSF_perfect[center-half_width:center+half_width, center-half_width:center+half_width]
PSF_center_def = PSF_def[center-half_width:center+half_width, center-half_width:center+half_width]
PSF_center_coma = PSF_coma[center-half_width:center+half_width, center-half_width:center+half_width]
PSF_center_spherical = PSF_spherical[center-half_width:center+half_width, center-half_width:center+half_width]

# --- Normalisation pour affichage ---
PSF_center_perfect /= PSF_center_perfect.max()
PSF_center_def /= PSF_center_def.max()
PSF_center_coma /= PSF_center_coma.max()
PSF_center_spherical /= PSF_center_spherical.max()

# --- Affichage ---
fig, axs = plt.subplots(2, 4)

# Phase
axs[0, 0].imshow(phase_perfect, cmap='twilight')
axs[0, 0].set_title('Phase - Système parfait')
axs[0, 1].imshow(def_phase, cmap='twilight')
axs[0, 1].set_title('Phase - Défocus (10λ)')
axs[0, 2].imshow(coma_phase, cmap='twilight')
axs[0, 2].set_title('Phase - Coma (10λ)')
axs[0, 3].imshow(spherical_phase, cmap='twilight')
axs[0, 3].set_title('Phase - Ab. Spherique (3e ordre)')

# PSF
axs[1, 0].imshow(PSF_center_perfect, cmap='hot')
axs[1, 0].set_title('PSF - Système parfait')
axs[1, 1].imshow(PSF_center_def, cmap='hot')
axs[1, 1].set_title(f'PSF - Défocus (Strehl = {strehl_def:.2f})')
axs[1, 2].imshow(PSF_center_coma, cmap='hot')
axs[1, 2].set_title(f'PSF - Coma (Strehl = {strehl_coma:.2f})')
axs[1, 3].imshow(PSF_center_spherical, cmap='hot')
axs[1, 3].set_title(f'PSF - Ab. Spherique 3 (Strehl = {strehl_spherical:.2f})')

plt.tight_layout()


# --- Comparaison 1D des PSF ---
plt.figure()
plt.plot(PSF_center_perfect[N//2, :], label='Système parfait')
#plt.plot(PSF_center_def[N//2, :], label='Défocus')
plt.plot(PSF_center_coma[N//2, :], label='Coma')
plt.plot(PSF_center_spherical[N//2, :], label='Ab. Spher.')
plt.title('Comparaison 1D des PSF')
plt.xlabel('Position (pixels)')
plt.ylabel('Intensité normalisée')
plt.legend()
plt.grid()
plt.show()
