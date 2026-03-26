import numpy as np
from lensepy.optics.zygo.dataset import *
from lensepy.optics.zygo.phase import *
from lensepy.optics.zygo.zernike_coefficients import *
from math import factorial

# Get Data
file_path = 'D:/_git/julien/lensepy-data/optics/zygo/test4.mat'
dataset = DataSet()
dataset.load_images_set_from_file(file_path)
dataset.load_masks_from_file(file_path)

# Process wavefront
phase = PhaseModel(dataset)
phase.prepare_data()
phase.process_wrapped_phase()
phase.process_unwrapped_phase()
zernike_coeffs = Zernike(phase)
zernike_coeffs.process_zernike_coefficient(36)

unwrapped_phase = phase.get_unwrapped_phase()
_, corrected_phase = zernike_coeffs.process_surface_correction(['piston', 'tilt'])

print(type(corrected_phase))
print(corrected_phase.dtype)
# -------------------------
# 3️⃣ Front d'onde masqué
# -------------------------
W = corrected_phase               # np.ma.MaskedArray
W_filled = W.filled(0.0)         # valeurs hors pupille = 0
mask_pupil = ~W.mask              # True dans la pupille

N = W.shape[0]
y, x = np.indices((N, N))
x = (x - N/2) / (N/2)
y = (y - N/2) / (N/2)
r = np.sqrt(x**2 + y**2)
theta = np.arctan2(y, x)

# Pupille géométrique + masque Zygo
pupil = (r <= 1) & (~W.mask)

# -------------------------
# 4️⃣ Définition des Zernike
# -------------------------
def zernike_radial(n, m, r):
    R = np.zeros_like(r)
    for k in range((n - abs(m))//2 + 1):
        num = (-1)**k * factorial(n - k)
        den = factorial(k) * factorial((n + abs(m))//2 - k) * factorial((n - abs(m))//2 - k)
        R += num / den * r**(n - 2*k)
    return R

def zernike(n, m, r, theta):
    if m > 0:
        return zernike_radial(n, m, r) * np.cos(m*theta)
    elif m < 0:
        return zernike_radial(n, -m, r) * np.sin(-m*theta)
    else:
        return zernike_radial(n, 0, r)

def noll_to_nm(j):
    n = 0
    j1 = j - 1
    while j1 > n:
        n += 1
        j1 -= n
    m = (-n + 2*j1)
    return n, m

# -------------------------
# 5️⃣ Calcul des coefficients de Zernike
# -------------------------
Z = []
coeffs = []

for j in range(1, 37):
    n, m = noll_to_nm(j)
    Zj = zernike(n, m, r, theta)
    Zj[~pupil] = 0
    num = np.sum(W_filled * Zj * pupil)
    den = np.sum(Zj**2 * pupil)
    coeffs.append(num / den)
    Z.append(Zj)

# -------------------------
# 6️⃣ Reconstruction du front d'onde
# -------------------------
W_rec = np.zeros_like(W_filled)
for a, Zj in zip(coeffs, Z):
    W_rec += a * Zj
W_rec[~pupil] = 0

# -------------------------
# 7️⃣ Pupille complexe correcte
# -------------------------
wavelength = 632.8e-9  # ex: HeNe
P = np.zeros_like(W_rec, dtype=complex)
P[pupil] = np.exp(1j * 2 * np.pi / wavelength * W_rec[pupil])

print("Amplitude min/max pupille:", np.abs(P).min(), np.abs(P).max())
print("Nombre de pixels pupille:", np.sum(np.abs(P) > 0))

# -------------------------
# 8️⃣ PSF
# -------------------------
ASF = np.fft.fftshift(np.fft.fft2(P))
PSF = np.abs(ASF)**2
PSF /= PSF.max()

# -------------------------
# 9️⃣ OTF / MTF
# -------------------------
OTF = np.fft.fftshift(np.fft.fft2(PSF))
MTF = np.abs(OTF)
MTF /= MTF.max()

# -------------------------
# 10️⃣ Strehl
# -------------------------
P0 = pupil.astype(float)
ASF0 = np.fft.fftshift(np.fft.fft2(P0))
PSF0 = np.abs(ASF0)**2
PSF0 /= PSF0.max()
strehl = PSF.max() / PSF0.max()
print("Strehl ratio:", strehl)

# -------------------------
# 11️⃣ Énergie encerclée
# -------------------------
yy, xx = np.indices(PSF.shape)
cx, cy = N//2, N//2
rr = np.sqrt((xx - cx)**2 + (yy - cy)**2)
r_max = N//2
encircled_energy = [PSF[rr <= rad].sum() for rad in range(r_max)]
encircled_energy = np.array(encircled_energy)
encircled_energy /= encircled_energy.max()

# -------------------------
# 12️⃣ F-number
# -------------------------
f_number = 10
pixel_scale = wavelength * f_number
x_psf = (np.arange(N) - N/2) * pixel_scale


print("Nombre de pixels pupille (masque géométrique + Zygo):", np.sum(pupil))
print("Nombre de pixels masqués dans W:", np.sum(W.mask))
print("Taille W:", W.shape)

# -------------------------
# 13️⃣ Affichage
# -------------------------
'''
plt.figure()
plt.imshow(W_filled, cmap='RdBu')
plt.colorbar(label='Front d’onde (m)')
plt.title("Front d’onde mesuré")

plt.figure()
for i in range(6):
    plt.subplot(2, 3, i+1)
    plt.imshow(Z[i], cmap='RdBu')
    plt.title(f"Zernike {i+1}")
    plt.axis('off')
plt.suptitle("Premiers modes de Zernike")

plt.figure()
plt.stem(coeffs)
plt.xlabel("Index Noll")
plt.ylabel("Coefficient (m)")
plt.title("Coefficients de Zernike")
'''
plt.figure()
plt.imshow(W_rec, cmap='RdBu')
plt.colorbar(label='Front d’onde (m)')
plt.title("Front d’onde reconstruit")

'''
error = (W_filled - W_rec) * pupil
plt.figure()
plt.imshow(error, cmap='RdBu')
plt.colorbar(label='Erreur (m)')
plt.title("Erreur de reconstruction")

phase_opt = 2*np.pi / wavelength * W_rec
plt.figure()
plt.imshow(phase_opt, cmap='twilight')
plt.colorbar(label='Phase (rad)')
plt.title("Phase optique")

plt.figure()
plt.imshow(np.abs(P), cmap='gray')
plt.title("Amplitude pupille")

plt.figure()
plt.imshow(np.angle(P), cmap='twilight')
plt.colorbar(label='Phase')
plt.title("Phase pupille")

plt.figure()
plt.imshow(PSF, cmap='inferno')
plt.colorbar()
plt.title("PSF (linéaire)")

plt.figure()
plt.imshow(np.log10(PSF + 1e-12), cmap='inferno')
plt.colorbar(label='log10')
plt.title("PSF (log)")

center = PSF.shape[0] // 2
plt.figure()
plt.plot(PSF[center, :])
plt.yscale('log')
plt.title("Coupe PSF")
plt.xlabel("Pixels")
plt.ylabel("Intensité")

plt.figure()
plt.imshow(MTF, cmap='viridis')
plt.colorbar()
plt.title("MTF")

plt.figure()
plt.plot(MTF[center, :])
plt.title("Coupe MTF")
plt.xlabel("Fréquence")
plt.ylabel("Contraste")

plt.figure()
plt.plot(encircled_energy)
plt.xlabel("Rayon (pixels)")
plt.ylabel("Énergie normalisée")
plt.title("Énergie encerclée")
plt.grid()

'''
plt.show()