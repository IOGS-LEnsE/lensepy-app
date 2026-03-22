import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111, projection='3d')
        super().__init__(fig)
        self.mpl_connect('scroll_event', self._zoom)

    def plot_surface(self):
        X = np.linspace(-1, 3, 100)
        Y = np.linspace(-2, 5, 100)
        X, Y = np.meshgrid(X, Y)
        Z = np.sin(np.sqrt(X ** 2 + Y ** 2))
        mask = np.ones_like(Z)
        mask[10:20, 20:30] = 0

        # Création d'un masque pour rendre transparentes les zones où Z == 0
        colors = cm.viridis(Z)
        colors[..., -1] = np.where(mask == 0, 0, 1)  # Alpha à 0 pour Z == 0

        # Affichage de la surface avec les couleurs transparentes
        self.axes.plot_surface(X, Y, Z, facecolors=colors, rstride=1, cstride=1)
        self.draw()

    def _zoom(self, event):
        """ Fonction de zoom pour la molette de la souris """
        scale_factor = 1.1 if event.button == 'up' else 0.9
        self.axes.set_xlim3d([x * scale_factor for x in self.axes.get_xlim3d()])
        self.axes.set_ylim3d([y * scale_factor for y in self.axes.get_ylim3d()])
        self.axes.set_zlim3d([z * scale_factor for z in self.axes.get_zlim3d()])
        self.draw()  # Redessiner la figure avec les nouvelles limites
        '''
        scale_factor = 0.9 if event.button == 'up' else 1.1
        xlim, ylim, zlim = self.axes.get_xlim3d(), self.axes.get_ylim3d(), self.axes.get_zlim3d()
        x_center, y_center, z_center = np.mean(xlim), np.mean(ylim), np.mean(zlim)
        new_xlim = [x_center + (x - x_center) * scale_factor for x in xlim]
        new_ylim = [y_center + (y - y_center) * scale_factor for y in ylim]
        new_zlim = [z_center + (z - z_center) * scale_factor for z in zlim]
        self.axes.set_xlim3d(new_xlim)
        self.axes.set_ylim3d(new_ylim)
        self.axes.set_zlim3d(new_zlim)
        self.draw()
        '''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = MplCanvas(self)
        self.canvas.plot_surface()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowTitle("Surface 3D avec valeurs nulles masquées")
        self.setGeometry(100, 100, 800, 600)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
