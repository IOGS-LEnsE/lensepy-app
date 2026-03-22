# -*- coding: utf-8 -*-
"""*unwrap_process.py* file.

This file contains functions to unwrap the phase.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (LEnsE) <julien.villemejane@institutoptique.fr>

"""

import scipy
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter
from scipy.interpolate import griddata
from skimage.restoration import unwrap_phase
from hariharan_algorithm import *
from zernike_coefficents import *
from polar_cartesian_transformations import *
from lensepy.images.conversion import *
from matplotlib import cm

PI = np.pi

def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    data = scipy.io.loadmat(file_path)
    return data

def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    scipy.io.savemat(file_path, data)

def split_3d_array(array_3d):
    # Ensure the array has the expected shape
    if array_3d.shape[2] != 5:
        raise ValueError("The loaded array does not have the expected third dimension size of 5.")
    
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(5)]
    return arrays

def surface_statistics(surface):
    # Calcul de PV (Peak-to-Valley)
    PV = np.nanmax(surface) - np.nanmin(surface)
    RMS = np.nanstd(surface)
    return PV, RMS


## Read data from MatLab file
data = read_mat_file("../_data/imgs2.mat")
images_mat = data['Imgs']
images = split_3d_array(images_mat)
## Write a new set of data into a MatLab file
new_data = np.stack((images), axis=2).astype(np.uint8)

# Display images
'''
for i, img in enumerate(images):
    plt.subplot(1,5,i+1)
    plt.imshow(img, cmap='gray')
    plt.axis('off')
plt.show()
'''

## Mask on the image
mask = np.zeros_like(images[0])
mask[400:1200, 790:1900] = 1
mask[200:400, 950:1600] = 1
mask[300:400, 880:1800] = 1
mask[1200:1400, 1350:1750] = 1


write_mat_file('test.mat', new_data, mask)
data2 = read_mat_file('test.mat')
images_mat = data2['Images']
images = split_3d_array(images_mat)
mask = data2['Masks']   # TO DO : add a test on the size of 'Masks'

mask = mask > 0.5

print(f'Mask Type = {mask.dtype}')

#mask = mask < 0.5

plt.figure()
plt.imshow(images[0]*mask, cmap='magma')
plt.show()


plt.figure()
plt.imshow(mask, cmap='magma')
plt.colorbar()
plt.show()


top_left, bottom_right = find_mask_limits(mask)
print("Top-left:", top_left)
print("Bottom-right:", bottom_right)
height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
pos_x, pos_y = top_left[1], top_left[0]
cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
images_c = crop_images(images, (height, width), (pos_x, pos_y))

print(f'H / W = {height} / {width}')

plt.figure()
plt.imshow(cropped_mask_phase)
plt.title('Cropped Mask !')
plt.show()


## TO DO : test with masks selection by user...

## Gaussian filter on image*
print('Opening Images...')
sigma = 10
images_filtered = images_c # list(map(lambda x:gaussian_filter(x, sigma), images_c))

for i, img in enumerate(images_filtered):
    plt.subplot(1,5,i+1)
    plt.imshow(img*cropped_mask_phase, cmap='gray')
    plt.axis('off')
plt.show()

## Calculation of the phase by Hariharan algorithm
print('Calculating Phase by Hariharan Algo...')
wrapped_phase = hariharan_algorithm(images_filtered, cropped_mask_phase)

# Array for displaying data on 3D projection
x = np.arange(wrapped_phase.shape[1])
y = np.arange(wrapped_phase.shape[0])
X, Y = np.meshgrid(x, y)

wrapped_phase_2 = np.ma.masked_where(np.logical_not(cropped_mask_phase), wrapped_phase)

# Display of the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(X, Y, wrapped_phase_2, cmap='magma', edgecolor='none', rstride=10, cstride=10)
ax.set_title('Wrapped surface')
cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'Default magnitude ($\lambda$)')
plt.show()

## Unwrap phase
print('Unwrapping Phase...')
unwrapped_phase = unwrap_phase(wrapped_phase)/(2*np.pi)
unwrapped_phase_2 = np.ma.masked_where(np.logical_not(cropped_mask_phase), unwrapped_phase)

# Display of the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(X, Y, unwrapped_phase_2, cmap='magma')
ax.set_title('Unwrapped surface')
cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'Default magnitude ($\lambda$)')
#plt.show()

## Statistics
PV, RMS = surface_statistics(unwrapped_phase_2) # [400:1200, 750:1900]
print(f"PV: {PV:.2f} λ | RMS: {RMS:.2f} λ")


## Zernike coefficients
print('Calculating Zernike coefficients...')
max_order = 3
coeffs = get_zernike_coefficient(unwrapped_phase_2, max_order=max_order)

'''
plt.figure()
plt.plot(coeffs)
plt.title('Zernike Coefficients')
'''
# Remove specified aberration
aberrations_considered = np.ones(max_order, dtype=int)
print(aberrations_considered)

corrected_phase, XX, YY = remove_aberration(unwrapped_phase_2, aberrations_considered)

PV, RMS = surface_statistics(corrected_phase)
print(f"PV: {PV:.2f} λ | RMS: {RMS:.2f} λ")

## Display initial and corrected phase
# Création de la figure et des sous-graphiques en 3D
fig = plt.figure(figsize=(14, 6))

# Initial phase with aberrations
min_value = np.round(np.min(unwrapped_phase_2), 0) - 1
max_value = np.round(np.max(unwrapped_phase_2), 0) + 1

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
surf1 = ax1.plot_surface(XX, YY, unwrapped_phase_2, cmap='viridis')
ax1.set_zlim([min_value, max_value])
ax1.set_title('Initial phase with aberrations')
fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

# Corrected phase without specified aberrations
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
surf2 = ax2.plot_surface(XX, YY, corrected_phase, cmap='viridis')
ax2.set_zlim([min_value, max_value])
ax2.set_title('Corrected phase without specified aberrations')
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

# Ajustement des paramètres de la figure
fig.tight_layout()

plt.show()


