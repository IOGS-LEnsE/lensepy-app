import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt6.QtGui import QTransform

class DualGraph3D(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graphiques 3D avec Colormap Fixe")
        self.setGeometry(100, 100, 800, 900)  # Fenêtre plus haute

        # Conteneur principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)  # Layout en colonne (empilé)
        self.setCentralWidget(central_widget)

        # Création des vues OpenGL
        self.view1 = gl.GLViewWidget()
        self.view2 = gl.GLViewWidget()

        # Ajouter une grille 3D dans chaque vue
        self.view1.addItem(gl.GLGridItem())
        self.view2.addItem(gl.GLGridItem())

        # Ajouter la colormap **dans la vue du bas**
        #self.add_colormap_to_view(self.view2)

        # Ajouter les vues au layout (l'une au-dessus de l'autre)
        main_layout.addWidget(self.view1, 1)
        main_layout.addWidget(self.view2, 1)

        # Démarrer la synchronisation des vues
        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_views)
        self.timer.start(50)

    def create_point_cloud(self):
        """Crée un nuage de points 3D coloré avec la même colormap que la surface."""
        n = 1000
        pos = np.random.rand(n, 3) * 4 - 2  # Points entre -2 et 2
        colors = self.compute_colormap(pos[:, 2], np.min(pos[:, 2]), np.max(pos[:, 2]))

        scatter = gl.GLScatterPlotItem(pos=pos, color=colors, size=5)
        #self.view1.addItem(scatter)

    def create_mesh_surface(self, x, y, Z1, Z2):
        """Crée une surface maillée avec une colormap."""
        X, Y = np.meshgrid(x, y)

        # Convertir en points pour OpenGL
        points1 = np.vstack((X.flatten(), Y.flatten(), Z1.flatten())).T
        points2 = np.vstack((X.flatten(), Y.flatten(), Z2.flatten())).T

        # Générer les faces triangulaires
        faces1 = []
        faces2 = []
        rows, cols = X.shape
        for i in range(rows - 1):
            for j in range(cols - 1):
                idx1 = i * cols + j
                idx2 = idx1 + 1
                idx3 = (i + 1) * cols + j
                idx4 = idx3 + 1
                faces1.append([idx1, idx3, idx2])
                faces2.append([idx2, idx3, idx4])

            # Vérifier si les points ne sont pas masqués avant d'ajouter les faces
            if (not np.any(points1[idx1].mask) and not np.any(points1[idx2].mask) and not np.any(points1[idx3].mask) and
                    not np.any(points1[idx4].mask)):
                faces1.append([idx1, idx3, idx2])
                faces1.append([idx2, idx3, idx4])
            if (not np.any(points2[idx1].mask) and not np.any(points2[idx2].mask) and not np.any(points2[idx3].mask) and
                    not np.any(points1[idx4].mask)):
                faces2.append([idx1, idx3, idx2])
                faces2.append([idx2, idx3, idx4])

        faces1 = np.array(faces1)
        faces2 = np.array(faces2)

        # Appliquer la colormap en fonction de Z
        colors1 = self.compute_colormap(points1[:, 2], np.min(points1[:, 2]), np.max(points1[:, 2]))
        colors2 = self.compute_colormap(points2[:, 2], np.min(points2[:, 2]), np.max(points2[:, 2]))

        # Création du maillage
        mesh1 = gl.GLMeshItem(
            vertexes=points1, faces=faces1, faceColors=colors1, smooth=True, drawEdges=True
        )
        mesh2 = gl.GLMeshItem(
            vertexes=points2, faces=faces2, faceColors=colors2, smooth=True, drawEdges=True
        )
        self.view1.addItem(mesh1)
        self.view2.addItem(mesh2)

    def compute_colormap(self, values, vmin, vmax):
        """Génère des couleurs basées sur une colormap (bleu → rouge) en fonction des valeurs Z."""

        # Appliquer un masque sur les valeurs en dehors de la plage [vmin, vmax]
        masked_values = np.ma.masked_outside(values, vmin, vmax)

        # Normalisation entre 0 et 1, mais seulement pour les valeurs non masquées
        norm_values = (masked_values - vmin) / (vmax - vmin)
        norm_values = np.ma.masked_invalid(masked_values)  # Masque les NaN éventuels

        colors = np.zeros((len(values), 4))
        colors[:, 0] = norm_values  # Rouge augmente avec la hauteur
        colors[:, 1] = 0.2  # Vert constant
        colors[:, 2] = 1 - norm_values  # Bleu diminue avec la hauteur
        colors[:, 3] = 1  # Opacité totale par défaut

        # Remplacer les couleurs des points masqués par une valeur "invisible"
        colors[norm_values.mask, :] = 0  # Rendre les points masqués totalement invisibles

        return colors

    def add_colormap_to_view(self, view):
        """Ajoute une colormap fixe dans la vue OpenGL."""
        colormap = np.linspace(0, 1, 256).reshape(256, 1)  # Gradient vertical
        colormap = np.hstack([colormap] * 20)  # Étire horizontalement

        # Convertir la colormap en une image OpenGL (GLImageItem)
        img = gl.GLImageItem(colormap.T)
        img.setDepthValue(10)  # Priorité d'affichage plus élevée

        # Appliquer une transformation pour ajuster la taille et la position
        transform = QTransform()
        transform.scale(50, 200)  # Ajuster l'échelle (largeur, hauteur)
        transform.translate(-2.5, -2)  # Déplacer l'image

        img.setTransform(transform)  # Appliquer la transformation

        # Ajouter à la scène
        view.addItem(img)

    def sync_views(self):
        """Synchronise les caméras des deux vues."""
        self.view2.opts['azimuth'] = self.view1.opts['azimuth']
        self.view2.opts['elevation'] = self.view1.opts['elevation']
        self.view2.opts['distance'] = self.view1.opts['distance']
        self.view2.opts['fov'] = self.view1.opts['fov']
        self.view2.update()

if __name__ == "__main__":
    import sys, os
    from matplotlib import pyplot as plt

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    nb_of_images_per_set = 5
    file_path = '../_data/test3.mat'
    data_set = DataSetModel()
    data_set.load_images_set_from_file(file_path)
    data_set.load_mask_from_file(file_path)

    phase_test = PhaseModel(data_set)
    data_set.phase = phase_test
    ## Test class
    data_set.phase.prepare_data()
    print(f'Number of sets = {data_set.phase.cropped_images_sets.get_number_of_sets()}')

    if data_set.phase.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = data_set.phase.get_wrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(wrapped.T, cmap='gray')

    if data_set.phase.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = data_set.phase.get_unwrapped_phase()
    if wrapped is not None:
        plt.figure()
        plt.imshow(unwrapped, cmap='gray')

    plt.show()

    wrapped_s = wrapped[::5,::5]
    unwrapped_s = unwrapped[::5,::5]

    app = QApplication(sys.argv)
    window = DualGraph3D()
    x = np.linspace(-10, 10, wrapped_s.shape[1])
    y = np.linspace(-10, 10, wrapped_s.shape[0])
    window.create_mesh_surface(x, y, wrapped_s, unwrapped_s)
    window.show()
    sys.exit(app.exec())