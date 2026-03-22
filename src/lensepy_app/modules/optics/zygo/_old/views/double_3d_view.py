# -*- coding: utf-8 -*-
"""*double_3d_view.py* file.

./views/double_3d_view.py contains DoubleGraph3DView class to display two synchronised
graphics in 3D.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : april/2025
"""
import sys, os
import time
import numpy as np
from lensepy.css import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from OpenGL.GL import glClearColor
from PyQt6.QtGui import QTransform


class Surface3DView(QWidget):
    def __init__(self):
        super().__init__()
        # Graphical structure
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.widget1 = QWidget()
        self.layout1 = QHBoxLayout()
        self.widget1.setLayout(self.layout1)
        # Title of each graphic
        self.label1 = QLabel('')
        self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout1.addWidget(self.label1, stretch=1)
        # OpenGL View
        self.view1 = gl.GLViewWidget()
        self.view1.setBackgroundColor(205, 205, 205, 255)
        # 3D Grid
        self.create_grid(15, 5)
        # Colormap ?
        # self.add_colormap_to_view(self.view2)
        self.layout1.addWidget(self.view1, stretch=5)
        self.main_layout.addWidget(self.widget1)

    def create_grid(self, size, spacing):
        color = (0.0, 0.0, 0.0, 1.0)  # vert RGBA
        # Generate lines
        lines = []
        positions = np.arange(-size / 2, size / 2 + spacing, spacing)

        for x in positions:
            lines.append(gl.GLLinePlotItem(pos=np.array([[x, -size / 2, 0], [x, size / 2, 0]]),
                                           color=color,
                                           width=1,
                                           antialias=True))
        for y in positions:
            lines.append(gl.GLLinePlotItem(pos=np.array([[-size / 2, y, 0], [size / 2, y, 0]]),
                                           color=color,
                                           width=1,
                                           antialias=True))
        # Add lines in the view
        for line in lines:
            self.view1.addItem(line)

    def create_point_cloud(self):
        """Crée un nuage de points 3D coloré avec la même colormap que la surface."""
        n = 1000
        pos = np.random.rand(n, 3) * 4 - 2  # Points entre -2 et 2
        colors = self.compute_colormap(pos[:, 2], np.min(pos[:, 2]), np.max(pos[:, 2]))

        scatter = gl.GLScatterPlotItem(pos=pos, color=colors, size=5)
        #self.view1.addItem(scatter)

    def prepare_data_for_mesh(self, Z1, undersampling: int = 20):
        """
        Prepare data for display (undersampling data to increase processing speed).
        :param Z1: First surface to display.
        :param Z2: Second surface to display.
        :param undersampling: Value for undersampling data (to increase speed of processing).
        Default 10.
        :return: x and y - the meshgrid axis - Z1 and Z2 - after undersampling.
        """
        Z1_s = Z1[::undersampling, ::undersampling]
        min_Z1_s = np.min(Z1_s)
        Z1_s = Z1_s - min_Z1_s
        x = np.linspace(-5, 5, Z1_s.shape[1])
        y = np.linspace(-5, 5, Z1_s.shape[0])
        return x, y, Z1_s

    def add_labels(self, name1: str = '', name2: str = ''):
        """
        Add labels (title) to each graph.
        :param name1: Title of the first graphic.
        :param name2: Title of the second graphic.
        """
        self.label1.setText(name1)
        self.label1.setStyleSheet(styleH2)

    def create_mesh_surface(self, x, y, Z1):
        """Crée une surface maillée avec une colormap."""
        ## Process data for displaying
        X, Y = np.meshgrid(x, y)
        # Convert points for OpenGL
        points1 = np.vstack((X.flatten(), Y.flatten(), Z1.flatten())).T
        # Generate triangular faces
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

            # Check if dots are masked before adding them.
            if (not np.any(points1[idx1].mask) and not np.any(points1[idx2].mask) and not np.any(points1[idx3].mask) and
                    not np.any(points1[idx4].mask)):
                faces1.append([idx1, idx3, idx2])
                faces1.append([idx2, idx3, idx4])

        faces1 = np.array(faces1)

        # Apply Z colormap
        colors1 = self.compute_colormap(points1[:, 2], np.min(points1[:, 2]), np.max(points1[:, 2]))

        # Generate Mesh grid
        mesh1 = gl.GLMeshItem(
            vertexes=points1, faces=faces1, faceColors=colors1, smooth=True, drawEdges=True
        )
        self.view1.addItem(mesh1)

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


class DoubleGraph3DView(QWidget):
    def __init__(self):
        super().__init__()
        # Graphical structure
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.widget1 = QWidget()
        self.layout1 = QHBoxLayout()
        self.widget1.setLayout(self.layout1)
        self.widget2 = QWidget()
        self.layout2 = QHBoxLayout()
        self.widget2.setLayout(self.layout2)
        # Title of each graphic
        self.label1 = QLabel('')
        self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout1.addWidget(self.label1, stretch=1)
        self.label2 = QLabel('')
        self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout2.addWidget(self.label2, stretch=1)
        # OpenGL View
        self.view1 = gl.GLViewWidget()
        self.view1.setBackgroundColor(205, 205, 205, 255)
        self.view2 = gl.GLViewWidget()
        self.view2.setBackgroundColor(205, 205, 205, 255)
        # 3D Grid
        '''
        grid1 = gl.GLGridItem()
        grid1.setSize(x=15, y=15)
        grid1.setSpacing(x=1, y=1)
        '''
        self.create_grid(15, 1)
        '''
        self.view1.addItem(grid1)
        self.view2.addItem(grid1)
        '''
        # Colormap ?
        # self.add_colormap_to_view(self.view2)
        self.layout1.addWidget(self.view1, stretch=5)
        self.layout2.addWidget(self.view2, stretch=5)
        self.main_layout.addWidget(self.widget1)
        self.main_layout.addWidget(self.widget2)

        # Timer for synchronization
        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_views)
        self.timer.start(50)

    def create_grid(self, size, spacing):
        color = (0.0, 0.0, 0.0, 1.0)  # vert RGBA
        # Generate lines
        lines = []
        positions = np.arange(-size / 2, size / 2 + spacing, spacing)

        for x in positions:
            lines.append(gl.GLLinePlotItem(pos=np.array([[x, -size / 2, 0], [x, size / 2, 0]]),
                                           color=color,
                                           width=1,
                                           antialias=True))
        for y in positions:
            lines.append(gl.GLLinePlotItem(pos=np.array([[-size / 2, y, 0], [size / 2, y, 0]]),
                                           color=color,
                                           width=1,
                                           antialias=True))
        # Add lines in the view
        for line in lines:
            self.view1.addItem(line)
            self.view2.addItem(line)

    def create_point_cloud(self):
        """Crée un nuage de points 3D coloré avec la même colormap que la surface."""
        n = 1000
        pos = np.random.rand(n, 3) * 4 - 2  # Points entre -2 et 2
        colors = self.compute_colormap(pos[:, 2], np.min(pos[:, 2]), np.max(pos[:, 2]))

        scatter = gl.GLScatterPlotItem(pos=pos, color=colors, size=5)
        #self.view1.addItem(scatter)

    def prepare_data_for_mesh(self, Z1, Z2, undersampling: int = 20):
        """
        Prepare data for display (undersampling data to increase processing speed).
        :param Z1: First surface to display.
        :param Z2: Second surface to display.
        :param undersampling: Value for undersampling data (to increase speed of processing).
        Default 10.
        :return: x and y - the meshgrid axis - Z1 and Z2 - after undersampling.
        """
        Z1_s = Z1[::undersampling, ::undersampling]
        min_Z1_s = np.min(Z1_s)
        Z1_s = Z1_s - min_Z1_s
        Z2_s = Z2[::undersampling, ::undersampling]
        min_Z2_s = np.min(Z2_s)
        Z2_s = Z2_s - min_Z2_s
        x = np.linspace(-5, 5, Z1_s.shape[1])
        y = np.linspace(-5, 5, Z1_s.shape[0])
        return x, y, Z1_s, Z2_s

    def add_labels(self, name1: str = '', name2: str = ''):
        """
        Add labels (title) to each graph.
        :param name1: Title of the first graphic.
        :param name2: Title of the second graphic.
        """
        self.label1.setText(name1)
        self.label1.setStyleSheet(styleH2)
        self.label2.setText(name2)
        self.label2.setStyleSheet(styleH2)

    def create_mesh_surface(self, x, y, Z1, Z2):
        """Crée une surface maillée avec une colormap."""
        ## Process data for displaying
        X, Y = np.meshgrid(x, y)
        # Convert points for OpenGL
        points1 = np.vstack((X.flatten(), Y.flatten(), Z1.flatten())).T
        points2 = np.vstack((X.flatten(), Y.flatten(), Z2.flatten())).T
        # Generate triangular faces
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

            # Check if dots are masked before adding them.
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

        # Apply Z colormap
        colors1 = self.compute_colormap(points1[:, 2], np.min(points1[:, 2]), np.max(points1[:, 2]))
        colors2 = self.compute_colormap(points2[:, 2], np.min(points2[:, 2]), np.max(points2[:, 2]))

        # Generate Mesh grid
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
        self.view1.opts['azimuth'] = self.view2.opts['azimuth']
        self.view1.opts['elevation'] = self.view2.opts['elevation']
        self.view1.opts['distance'] = self.view2.opts['distance']
        self.view1.opts['fov'] = self.view2.opts['fov']
        self.view1.update()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    nb_of_images_per_set = 5
    file_path = '../_data/test4.mat'
    data_set = DataSetModel()
    data_set.load_images_set_from_file(file_path)
    data_set.load_mask_from_file(file_path)

    phase_test = PhaseModel(data_set)
    data_set.phase = phase_test
    data_set.phase.prepare_data()

    if data_set.phase.process_wrapped_phase():
        print('Wrapped Phase OK')
    wrapped = data_set.phase.get_wrapped_phase()

    if data_set.phase.process_unwrapped_phase():
        print('Unwrapped Phase OK')
    unwrapped = data_set.phase.get_unwrapped_phase()

    # Test class
    app = QApplication(sys.argv)
    main_widget = DoubleGraph3DView()
    x, y, w_s, u_s = main_widget.prepare_data_for_mesh(wrapped, unwrapped, undersampling=3)
    main_widget.create_mesh_surface(x, y, w_s, u_s)
    main_widget.setGeometry(100, 100, 800, 700)
    main_widget.add_labels('Wrapped Phase', 'Unwrapped Phase')
    main_widget.show()


    sys.exit(app.exec())