import sys
import numpy as np

from PyQt6 import QtWidgets
import pyqtgraph.opengl as gl
import pyqtgraph as pg


class Wavefront3D(QtWidgets.QMainWindow):

    def __init__(self, z):
        super().__init__()

        self.setWindowTitle("Front d'onde 3D")
        self.resize(1200, 800)

        # -------------------------------------------------
        # Widget OpenGL
        # -------------------------------------------------

        self.view = gl.GLViewWidget()
        self.setCentralWidget(self.view)

        self.view.setCameraPosition(
            distance=250,
            elevation=25,
            azimuth=35
        )

        # -------------------------------------------------
        # Grille XY
        # -------------------------------------------------

        ny, nx = z.shape

        x = np.arange(nx, dtype=np.float32)
        y = np.arange(ny, dtype=np.float32)

        X, Y = np.meshgrid(x, y)

        # -------------------------------------------------
        # Sommets
        # -------------------------------------------------

        vertices = np.column_stack((
            X.ravel(),
            Y.ravel(),
            z.ravel()
        )).astype(np.float32)

        # -------------------------------------------------
        # Triangles
        # -------------------------------------------------

        faces = []

        for j in range(ny - 1):
            for i in range(nx - 1):

                p0 = j * nx + i
                p1 = p0 + 1
                p2 = p0 + nx
                p3 = p2 + 1

                faces.append([p0, p1, p2])
                faces.append([p1, p3, p2])

        faces = np.asarray(faces, dtype=np.uint32)

        # -------------------------------------------------
        # Couleur en fonction de Z
        # -------------------------------------------------

        colors = self.make_colors(z.ravel())

        meshdata = gl.MeshData(
            vertexes=vertices,
            faces=faces,
            vertexColors=colors
        )

        self.mesh = gl.GLMeshItem(
            meshdata=meshdata,
            smooth=True,
            drawEdges=False,
            shader="shaded"
        )

        self.view.addItem(self.mesh)

    # -----------------------------------------------------
    # Colormap proche d'une représentation interférométrique
    # -----------------------------------------------------

    def make_colors(self, z):

        zmin = np.nanmin(z)
        zmax = np.nanmax(z)

        t = (z - zmin) / (zmax - zmin + 1e-12)

        # bleu → cyan → vert → jaune → rouge
        stops = np.array([
            [0.00, 0.00, 0.80],
            [0.00, 0.80, 0.80],
            [0.00, 0.80, 0.00],
            [1.00, 1.00, 0.00],
            [1.00, 0.00, 0.00],
        ])

        positions = np.linspace(0, 1, len(stops))

        r = np.interp(t, positions, stops[:, 0])
        g = np.interp(t, positions, stops[:, 1])
        b = np.interp(t, positions, stops[:, 2])

        return np.column_stack((
            r, g, b,
            np.ones_like(r)
        )).astype(np.float32)


# ==========================================================
# Exemple de front d'onde
# ==========================================================

def create_test_wavefront(nx=300, ny=300):

    x = np.linspace(-1, 1, nx)
    y = np.linspace(-1, 1, ny)

    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2)

    # ouverture circulaire
    mask = R <= 1

    # Exemple : aberration sphérique + astigmatisme
    Z = (
        0.20 * (X**2 + Y**2)
        + 0.10 * (X**2 - Y**2)
        + 0.05 * (X**3 - 3*X*Y**2)
    )

    # extérieur de l'ouverture
    Z[~mask] = np.nan

    return Z


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    z = create_test_wavefront()

    # Pour visualiser, on remplace temporairement les NaN
    # par 0 ; voir plus bas pour une vraie gestion du masque.
    z_display = np.nan_to_num(z, nan=0.0)

    window = Wavefront3D(z_display)
    window.show()

    sys.exit(app.exec())