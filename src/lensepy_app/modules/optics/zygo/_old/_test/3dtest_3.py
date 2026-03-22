import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from PIL import Image

z = np.random.randint(0, 255, (1000, 1000))
z[100:200, 300:500] = 50

# Créer le masque (par exemple : masquer les pixels en dessous d'une certaine valeur)
seuil = 100  # Valeur de seuil pour masquer (ajustez selon l'image)
masque = z < seuil
z_masque = np.ma.masked_where(masque, z)  # Appliquer le masque

# Générer les coordonnées x et y
x = np.arange(z.shape[1])
y = np.arange(z.shape[0])
x, y = np.meshgrid(x, y)

# Afficher la surface en 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Utiliser plot_surface avec le masque
ax.plot_surface(x, y, z_masque, cmap=cm.viridis, edgecolor='none')

# Personnaliser les axes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()