import numpy as np
#import pyfits
import matplotlib.pyplot as plt
from scipy.fftpack import fftshift, ifftshift, fft2, ifft2

## polar coordinates
def Zernike_polar(coefficients, r, u):
    Z = coefficients
    Z1  =  Z[0]  * 1*(np.cos(u)**2+np.sin(u)**2)
    Z2  =  Z[1]  * 2*r*np.cos(u)
    Z3  =  Z[2]  * 2*r*np.sin(u)
    Z4  =  Z[3]  * np.sqrt(3)*(2*r**2-1)
    Z5  =  Z[4]  * np.sqrt(6)*r**2*np.sin(2*u)
    Z6  =  Z[5]  * np.sqrt(6)*r**2*np.cos(2*u)
    Z7  =  Z[6]  * np.sqrt(8)*(3*r**2-2)*r*np.sin(u)
    Z8  =  Z[7]  * np.sqrt(8)*(3*r**2-2)*r*np.cos(u)
    Z9  =  Z[9]  * np.sqrt(8)*r**3*np.sin(3*u)
    Z10 =  Z[10] * np.sqrt(8)*r**3*np.cos(3*u)
    '''
    Z11 =  Z[11] * np.sqrt(5)*(1-6*r**2+6*r**4)
    Z12 =  Z[12] * np.sqrt(10)*(4*r**2-3)*r**2*np.cos(2*u)
    Z13 =  Z[13] * np.sqrt(10)*(4*r**2-3)*r**2*np.sin(2*u)
    Z14 =  Z[14] * np.sqrt(10)*r**4*np.cos(4*u)
    Z15 =  Z[15] * np.sqrt(10)*r**4*np.sin(4*u)
    Z16 =  Z[16] * np.sqrt(12)*(10*r**4-12*r**2+3)*r*np.cos(u)
    Z17 =  Z[17] * np.sqrt(12)*(10*r**4-12*r**2+3)*r*np.sin(u)
    Z18 =  Z[18] * np.sqrt(12)*(5*r**2-4)*r**3*np.cos(3*u)
    Z19 =  Z[19] * np.sqrt(12)*(5*r**2-4)*r**3*np.sin(3*u)
    Z20 =  Z[20] * np.sqrt(12)*r**5*np.cos(5*u)
    Z21 =  Z[21] * np.sqrt(12)*r**5*np.sin(5*u)
    Z22 =  Z[22] * np.sqrt(7)*(20*r**6-30*r**4+12*r**2-1)
    Z23 =  Z[23] * np.sqrt(14)*(15*r**4-20*r**2+6)*r**2*np.sin(2*u)
    Z24 =  Z[24] * np.sqrt(14)*(15*r**4-20*r**2+6)*r**2*np.cos(2*u)
    Z25 =  Z[25] * np.sqrt(14)*(6*r**2-5)*r**4*np.sin(4*u)
    Z26 =  Z[26] * np.sqrt(14)*(6*r**2-5)*r**4*np.cos(4*u)
    Z27 =  Z[27] * np.sqrt(14)*r**6*np.sin(6*u)
    Z28 =  Z[28] * np.sqrt(14)*r**6*np.cos(6*u)
    Z29 =  Z[29] * 4*(35*r**6-60*r**4+30*r**2-4)*r*np.sin(u)
    Z30 =  Z[30] * 4*(35*r**6-60*r**4+30*r**2-4)*r*np.cos(u)
    Z31 =  Z[31] * 4*(21*r**4-30*r**2+10)*r**3*np.sin(3*u)
    Z32 =  Z[32] * 4*(21*r**4-30*r**2+10)*r**3*np.cos(3*u)
    Z33 =  Z[33] * 4*(7*r**2-6)*r**5*np.sin(5*u)
    Z34 =  Z[34] * 4*(7*r**2-6)*r**5*np.cos(5*u)
    Z35 =  Z[35] * 4*r**7*np.sin(7*u)
    Z36 =  Z[36] * 4*r**7*np.cos(7*u)
    Z37 =  Z[37] * 3*(70*r**8-140*r**6+90*r**4-20*r**2+1)
    '''
    ZW = Z1 + Z2 +  Z3+  Z4+  Z5+  Z6+  Z7+  Z8 + Z9 + Z10
        # + Z11+ Z12+ Z13+ Z14+ Z15+ Z16+ Z17+ Z18+
        #  Z19+Z20+ Z21+ Z22+ Z23+ Z24+ Z25+ Z26+ Z27+ Z28+
        #  Z29+Z30+ Z31+ Z32+ Z33+ Z34+ Z35+ Z36+ Z37)
    return ZW

def pupil_size(D,lam,pix,size):
    pixrad = pix*np.pi/(180*3600)  # Pixel-size in radians
    nu_cutoff = D/lam      # Cutoff frequency in rad^-1
    deltanu = 1./(size*pixrad)     # Sampling interval in rad^-1
    rpupil = nu_cutoff/(2*deltanu) #pupil size in pixels
    return int(rpupil)


def phase(coefficients, rpupil):
    r = 1
    x = np.linspace(-r, r, 2 * rpupil)
    y = np.linspace(-r, r, 2 * rpupil)

    [X, Y] = np.meshgrid(x, y)
    R = np.sqrt(X ** 2 + Y ** 2)
    theta = np.arctan2(Y, X)

    Z = Zernike_polar(coefficients, R, theta)
    Z[R > 1] = 0
    return Z

def center(coefficients,size,rpupil):
    A = np.zeros([size,size])
    A[size//2-rpupil+1:size//2+rpupil+1,size//2-rpupil+1:size//2+rpupil+1]= phase(coefficients,rpupil)
    return A

def mask(rpupil, size):
    r = 1
    x = np.linspace(-r, r, 2*rpupil)
    y = np.linspace(-r, r, 2*rpupil)

    [X,Y] = np.meshgrid(x,y)
    R = np.sqrt(X**2+Y**2)
    theta = np.arctan2(Y, X)
    M = 1*(np.cos(theta)**2+np.sin(theta)**2)
    M[R>1] = 0
    Mask =  np.zeros([size,size])
    Mask[size//2-rpupil+1:size//2+rpupil+1,size//2-rpupil+1:size//2+rpupil+1]= M
    return Mask

def complex_pupil(A,Mask):
    abbe =  np.exp(1j*A)
    abbe_z = np.zeros((len(abbe),len(abbe)), dtype=np.complex128)
    abbe_z = Mask*abbe
    return abbe_z

def PSF(complx_pupil):
    PSF = ifftshift(fft2(fftshift(complx_pupil)))
    PSF = (np.abs(PSF))**2 #or PSF*PSF.conjugate()
    PSF = PSF/PSF.sum() #normalizing the PSF
    return PSF

def OTF(psf):
    otf = ifftshift(psf) #move the central frequency to the corner
    otf = fft2(otf)
    otf_max = float(otf[0,0]) #otf_max = otf[size/2,size/2] if max is shifted to center
    otf = otf/otf_max #normalize by the central frequency signal
    return otf

def MTF(otf):
    mtf = np.abs(otf)
    return mtf

def diffraction_limit(center, radius, size):
    '''The diffraction limit by using the parameters of the aperture disc and creating a blank disk
    a blank disk with the right dimensions
    center : [x0, y0]
    radius : float
    size : tuple (height, width)
    '''
    image = np.zeros(size)
    h, w = size
    x0, y0 = center[0], center[1]
    for i in range(h):
        for j in range(w):
            R = np.sqrt((i - x0)**2 + (j - y0)**2)
            if R <= radius:
                image[i][j] = 1
    return image

def find_rf(rpupil, image):
    '''compares the result of the PSF treatment on the diffraction limit with the PSF of the actual image'''
    size, _ = image.shape
    diff_lim_image = mask(rpupil, size)
    psf_diff_lim = PSF(diff_lim_image)
    psf_image = PSF(image)
    return psf_diff_lim, psf_image

D = 2               #diameter of the aperture
lam = 632.8*1e-6    #wavelength of observation
pix = 1 #plate scale
f = 50            #effective focal length
size = 1024 #size of detector in pixels

coefficients = np.zeros(11)
coefficients[1] = 0.1
coefficients[2] = 0.1
coefficients[3] = 0.3
coefficients[4] = -0.2
coefficients[5] = 0.3
coefficients[6] = -0.2
coefficients[7] = 0.5
coefficients[8] = -2

## Pupil
GAIN = 32
rpupil_disp = pupil_size(D*GAIN,lam,pix,size)
rpupil = pupil_size(D,lam,pix,size)
sim_phase_disp = center(coefficients,size,rpupil_disp)
sim_phase = center(coefficients,size,rpupil)
Mask_disp = mask(rpupil_disp, size)
Mask = mask(rpupil, size)

pupil_com = complex_pupil(sim_phase,Mask)

plt.figure(figsize=(18,10))
plt.imshow(sim_phase_disp)
plt.colorbar()

## PSF
psf = PSF(pupil_com)

psf_diff_lim, psf_image = find_rf(50, pupil_com)

plt.figure(figsize=(18,10))
plt.imshow(np.abs(psf))
plt.colorbar()

psf_slice = psf[psf.shape[1] // 2, :]

plt.figure(figsize=(18,10))
plt.plot(psf_slice)

## OTF/MTF
otf = OTF(psf)
mtf = MTF(otf)

plt.figure(figsize=(18,10))
plt.imshow(fftshift(mtf))
plt.colorbar()

plt.figure()
plt.imshow(psf_diff_lim, cmap = "gray")

plt.figure()
plt.imshow(psf_image, cmap = "gray")

plt.show()