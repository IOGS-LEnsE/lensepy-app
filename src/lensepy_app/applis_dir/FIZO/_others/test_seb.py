import numpy as np

import matplotlib.pyplot as plt

from numpy.fft import fft2, ifft2, fftshift, ifftshift

from scipy.ndimage import shift

from skimage import io, img_as_float

from skimage.restoration import unwrap_phase




# ***** fonction pour le madsque ciculaire *****

def cercle_par_3_points(p1, p2, p3):

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    A = np.array([[2*(x2-x1), 2*(y2-y1)], [2*(x3-x1), 2*(y3-y1)]])
    B = np.array([x2**2 + y2**2 - x1**2 - y1**2, x3**2 + y3**2 - x1**2 - y1**2])

    xc, yc = np.linalg.solve(A, B)
    R = np.sqrt((x1-xc)**2 + (y1-yc)**2)
    return xc, yc, R


# -------- Chargement et affichage interférogramme 

img = img_as_float(io.imread("interference.png", as_gray=True))

N, M = img.shape 

iC, jC = N // 2, M // 2

Yf, Xf = np.indices((N, M)) # grille fréquentielle


plt.figure(figsize=(6,6))

plt.imshow(img, cmap='gray')

plt.title("Cliquez 3 points pour définir le masque spatial")

plt.axis('off')

#plt.show()


# -------- Masque circulaire

pts = plt.ginput(3, timeout=0)

plt.close()

xc, yc, R = cercle_par_3_points(*pts)

Y, X = np.indices((N, M))

masque_img = (X - xc)**2 + (Y - yc)**2 <= R**2


img[~masque_img] = 0 #np.nan




# -------- Traitement TF

Itf = fftshift(fft2(img))

module_TF = np.abs(Itf)

module_HF = module_TF.copy()


rayon_BF = 80 # rayon zone centrale

rayon_pic = 50 # largeur pic latéral


masque_BF = (Xf - jC)**2 + (Yf - iC)**2 <= rayon_BF**2 # masque central

module_HF[masque_BF] = 0 # filtrage centre

imx, jmx = np.unravel_index(np.argmax(module_HF),module_HF.shape)


masque_pic = (Xf - jmx)**2 + (Yf - imx)**2 <= rayon_pic**2

Itf_filtr = np.zeros_like(Itf)

Itf_filtr = Itf * masque_pic.astype(float) # filtrage pic

Itf_centre = np.roll(Itf_filtr,shift=(iC - imx, jC - jmx),axis=(0, 1)) # démodulation




# -------- Phase et déroulement

champ = ifft2(ifftshift(Itf_centre))

champ[~masque_img] = 0; 

phase_enroulee = np.angle(champ)

phase_deroulee = unwrap_phase(phase_enroulee)

phase_deroulee[~masque_img] = np.nan


# -------- Supression Tilt Piston

Masq = masque_img #& ~np.isnan(phase_deroulee)


xx = (np.arange(-M//2, M//2) / M) * 2

yy = (np.arange(-N//2, N//2) / N) * 2

Xg, Yg = np.meshgrid(xx, yy)


A = np.column_stack((np.ones(np.sum(Masq)),Xg[Masq],Yg[Masq]))


Z = phase_deroulee[Masq]

coeffs, *_ = np.linalg.lstsq(A, Z, rcond=None)


phase_corr = np.full_like(phase_deroulee, np.nan)

phase_corr[Masq] = Z - A @ coeffs




# -------- Défaut Surface

lambdam = 0.670 # longueur d’onde (micron)


surface = phase_corr / (4 * np.pi) * lambdam #d éfaut en réflexion

surface[~masque_img] = np.nan


surface_val = surface[masque_img & ~np.isnan(surface)]

PV_micron = np.max(surface_val) - np.min(surface_val)

RMS_micron = np.sqrt(np.mean((surface_val - np.mean(surface_val))**2))




# -------- AFFICHAGE

fig, axs = plt.subplots(2, 2, figsize=(13, 8))

axs = axs.ravel()

axs[0].imshow(img, cmap='gray')

axs[0].set_title("Interférogramme (masqué)")


axs[1].imshow(np.log(module_TF + 1), cmap='gray')

axs[1].set_title("TF (log)")

axs[1].contour(masque_BF, colors='red', linewidths=1)

axs[1].contour(masque_pic, colors='red', linewidths=1)


axs[2].imshow(phase_enroulee, cmap='jet')

axs[2].set_title("Phase enroulée")


im=axs[3].imshow(surface, cmap='jet')

axs[3].set_title("Hauteur (micron)")

fig.colorbar(im, ax=axs[3])

# Annotation PV

axs[3].text(0.02, 0.98,f"PV = {PV_micron:.2f} micron",transform=axs[3].transAxes,color='white',

fontsize=10,verticalalignment='top',

bbox=dict(facecolor='black', alpha=0.6, edgecolor='none'))


plt.show()