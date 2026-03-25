# -*- coding: utf-8 -*-
"""*psf.py* file.

./models/psf.py contains PSFModel class to process the Point Spread Function of a wavefront.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
Creation : april/2025
"""
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.phase import PhaseModel

def process_statistics_surface(surface):
    # Process (Peak-to-Valley) and RMS
    PV = np.round(np.nanmax(surface) - np.nanmin(surface), 2)
    RMS = np.round(np.nanstd(surface), 2)
    return PV, RMS

class PSFModel:
    """Class to process the Point Spread Function of a wavefront
    """
    def __init__(self, phase: "PhaseModel"):
        """

        """
        self.phase: "PhaseModel" = phase

        self.wavefront = self.phase.get_unwrapped_phase() * 2 * np.pi
        self.mask, _ = self.phase.cropped_masks_sets.get_mask(1)
        self.amplitude = np.ones_like(self.wavefront)
        self.amplitude[np.isnan(self.mask)] = 0

        self.phase = np.exp(1j * self.wavefront)
        self.phase[np.isnan(self.mask)] = 0

        self.pupil = self.amplitude * self.phase

    def get_psf(self):
        fft_field = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(self.pupil)))
        psf = np.abs(fft_field) ** 2
        psf /= psf.max()
        return psf / psf.max()



if __name__ == '__main__':
    import sys, os
    from matplotlib import pyplot as plt
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    nb_of_images_per_set = 5
    file_path = '../_data/test4.mat'
    data_set = DataSetModel()
    data_set.load_images_set_from_file(file_path)
    data_set.load_mask_from_file(file_path)

    phase_test = PhaseModel(data_set)
    phase_test.prepare_data()
    print(f'Number of sets = {phase_test.cropped_images_sets.get_number_of_sets()}')

    if phase_test.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = phase_test.get_wrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(wrapped.T, cmap='gray')

    if phase_test.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = phase_test.get_unwrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(unwrapped, cmap='gray')


    # Test class
    psf = PSFModel(phase_test)
    psf_disp = psf.get_psf()

    plt.figure()
    plt.imshow(np.log(psf_disp), cmap='gray')

    psf_slice = psf_disp[psf_disp.shape[1]//2, :]

    plt.figure()
    plt.plot(psf_slice)

    plt.show()