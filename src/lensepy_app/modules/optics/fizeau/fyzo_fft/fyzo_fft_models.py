import numpy as np

if __name__ == '__main__':


    Itf = np.fft.fftshift(np.fft.fft2(img))

    module_TF = np.abs(Itf)

    module_HF = module_TF.copy()