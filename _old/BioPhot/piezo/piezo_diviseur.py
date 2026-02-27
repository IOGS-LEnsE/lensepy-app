# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 07:51:46 2023

@author: julien.villemejane
"""

import numpy as np
from matplotlib import pyplot as plt

R1 = 1.2e3
R2 = 12e3

P = np.linspace(0,1e3, 101)

FT_biophot = (R1 + P) / (R1 + P + R2)

plt.figure()
plt.plot(P, FT_biophot)
plt.show()
