"""
Front d'onde d'un système optique (phase-shifting à 4 pas) en surface 3D.
pyqtgraph + OpenGL, affichage encapsulé dans un QWidget : Wavefront3D.

Dépendances : pip install numpy pyqtgraph PyQt5 PyOpenGL
Optionnel   : pip install scikit-image   (meilleur déroulement de phase)
              pip install matplotlib     (colormaps matplotlib)
"""
import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtWidgets, QtCore


# ======================================================================
# Widget d'affichage 3D
# ======================================================================
class Wavefront3D(QtWidgets.QWidget):
    """
    Affiche un front d'onde (tableau 2D en longueurs d'onde) en surface 3D OpenGL.

    Utilisation :
        w = Wavefront3D(colormap="inferno", subsample=4)
        w.set_data(W, masque)            # X, Y optionnels (défaut : [-1, 1])
        w.set_colormap("viridis")
        w.set_subsample(2, "moyenne")

    Signal :
        statsChanged(pv, rms) émis à chaque nouvelle donnée (calculé en pleine résolution).
    """
    statsChanged = QtCore.Signal(float, float)

    def __init__(self, parent=None, colormap="viridis", subsample=1,
                 subsample_method="moyenne", z_scale=1.0):
        super().__init__(parent)
        self._cmap_name = colormap
        self._k = max(1, int(subsample))
        self._methode = subsample_method
        self._z_scale = z_scale

        # Données en pleine résolution
        self._W = self._mask = self._X = self._Y = None
        self._pv = self._rms = np.nan
        self._surf = None

        self._build_ui()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Vue 3D
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor("k")
        self.view.setCameraPosition(distance=4.5, elevation=30, azimuth=-60)

        grille = gl.GLGridItem()
        grille.setSize(2, 2)
        grille.setSpacing(0.25, 0.25)
        grille.translate(0, 0, -1.2)
        self.view.addItem(grille)

        axes = gl.GLAxisItem()
        axes.setSize(1.2, 1.2, 1.2)
        self.view.addItem(axes)

        # Barre de couleur
        self._cb_widget = pg.GraphicsLayoutWidget()
        self._cb_widget.setFixedWidth(110)
        self._cb_plot = self._cb_widget.addPlot()
        self._cb_img = pg.ImageItem()
        self._cb_plot.addItem(self._cb_img)
        self._cb_plot.hideAxis("bottom")
        self._cb_plot.hideAxis("left")
        self._cb_plot.showAxis("right")
        self._cb_plot.getAxis("right").setLabel("Front d'onde (λ)")
        self._cb_plot.setMouseEnabled(False, False)
        self._cb_plot.setMenuEnabled(False)

        # Étiquette de stats
        self.label = QtWidgets.QLabel("PV = –   RMS = –")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Layout
        haut = QtWidgets.QHBoxLayout()
        haut.addWidget(self.view, stretch=1)
        haut.addWidget(self._cb_widget)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(haut, stretch=1)
        lay.addWidget(self.label)

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------
    def set_data(self, W, masque=None, X=None, Y=None):
        """W : front d'onde 2D (en λ). masque : booléen (pupille). X, Y : grilles 2D."""
        W = np.asarray(W, dtype=float)
        if masque is None:
            masque = np.isfinite(W)
        if X is None or Y is None:
            x = np.linspace(-1, 1, W.shape[1])
            y = np.linspace(-1, 1, W.shape[0])
            X, Y = np.meshgrid(x, y)

        self._W, self._mask, self._X, self._Y = W, np.asarray(masque, bool), X, Y

        # Stats en pleine résolution
        vals = W[self._mask]
        self._pv = float(vals.max() - vals.min())
        self._rms = float(vals.std())
        self.label.setText("PV = %.3f λ     RMS = %.3f λ" % (self._pv, self._rms))
        self.statsChanged.emit(self._pv, self._rms)

        self._refresh()

    def set_colormap(self, name):
        self._cmap_name = name
        if self._W is not None:
            self._refresh()

    def set_subsample(self, k, methode=None):
        self._k = max(1, int(k))
        if methode is not None:
            self._methode = methode
        if self._W is not None:
            self._refresh()

    def set_z_scale(self, z_scale):
        self._z_scale = z_scale
        if self._W is not None:
            self._refresh()

    @property
    def pv(self):
        return self._pv

    @property
    def rms(self):
        return self._rms

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------
    def _get_cmap(self):
        try:
            return pg.colormap.get(self._cmap_name)
        except Exception:
            return pg.colormap.get(self._cmap_name, source="matplotlib")

    @staticmethod
    def _sous_echantillonner(W, masque, X, Y, k, methode):
        if k <= 1:
            return W, masque, X, Y
        if methode == "decimation":
            s = np.s_[::k, ::k]
            return W[s], masque[s], X[s], Y[s]

        n = (W.shape[0] // k) * k
        m = (W.shape[1] // k) * k
        blocs = lambda A: A[:n, :m].reshape(n // k, k, m // k, k)

        cnt = blocs(masque.astype(float)).sum(axis=(1, 3))
        Wb = blocs(np.where(masque, W, 0.0)).sum(axis=(1, 3)) / np.maximum(cnt, 1)
        Xb = blocs(X).mean(axis=(1, 3))
        Yb = blocs(Y).mean(axis=(1, 3))
        mb = cnt >= 0.5 * k * k
        return np.where(mb, Wb, 0.0), mb, Xb, Yb

    def _refresh(self):
        W, masque, X, Y = self._sous_echantillonner(
            self._W, self._mask, self._X, self._Y, self._k, self._methode)

        cmap = self._get_cmap()
        vals = self._W[self._mask]            # bornes de couleur : pleine résolution
        vmin, vmax = vals.min(), vals.max()
        etendue = max(vmax - vmin, 1e-12)

        # Couleurs
        norm = np.clip((W - vmin) / etendue, 0, 1)
        colors = cmap.map(norm.ravel(), mode="float").reshape(*W.shape, 4)
        colors[~masque, 3] = 0.0              # hors pupille : transparent

        # Surface (hauteur normalisée à ~[-1, 1])
        z = np.where(masque, W, vals.mean())
        z = z * self._z_scale / max(abs(vmin), abs(vmax), 1e-12)

        if self._surf is not None:
            self.view.removeItem(self._surf)
        self._surf = gl.GLSurfacePlotItem(
            x=X[0, :], y=Y[:, 0], z=z.T, colors=colors.transpose(1, 0, 2),
            shader=None, smooth=True, computeNormals=False)
        self._surf.setGLOptions("translucent")
        self.view.addItem(self._surf)

        # Barre de couleur (1 colonne x 256 lignes, croissante vers le haut)
        self._cb_img.setImage(np.linspace(0, 1, 256)[None, :], levels=(0, 1))
        self._cb_img.setColorMap(cmap)
        self._cb_img.setRect(QtCore.QRectF(0, vmin, 1, etendue))
        self._cb_plot.setXRange(0, 1, padding=0)
        self._cb_plot.setYRange(vmin, vmax, padding=0)


# ======================================================================
# Traitement : simulation + phase-shifting
# ======================================================================
def pupille(n):
    x = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(x, x)
    R = np.hypot(X, Y)
    return X, Y, R, R <= 1.0


def front_d_onde_simule(X, Y, R):
    """Aberrations (en longueurs d'onde) : défocus, astigmatisme, coma, sphérique."""
    TH = np.arctan2(Y, X)
    return (0.30 * (2 * R**2 - 1)
            + 0.25 * R**2 * np.cos(2 * TH)
            + 0.15 * (3 * R**3 - 2 * R) * np.cos(TH)
            + 0.10 * (6 * R**4 - 6 * R**2 + 1)
            + 0.4 * X + 0.2 * Y)


def interferogrammes(W, masque, bruit=0.2):
    phi = 2 * np.pi * W
    return [np.where(masque, 0.1 + 0.4 * np.cos(phi + d) + bruit * np.random.randn(*W.shape), 0.0)
            for d in np.array([0, 0.5, 1.0, 1.5]) * np.pi]


def phase_4_pas(I1, I2, I3, I4):
    return np.arctan2(I4 - I2, I1 - I3)


def derouler(phase, masque):
    try:
        from skimage.restoration import unwrap_phase
        return np.asarray(unwrap_phase(np.ma.array(phase, mask=~masque)).filled(0))
    except ImportError:
        return np.unwrap(np.unwrap(phase, axis=0), axis=1)


def retirer_piston_tilt(W, X, Y, masque):
    A = np.column_stack([np.ones(masque.sum()), X[masque], Y[masque]])
    coef, *_ = np.linalg.lstsq(A, W[masque], rcond=None)
    return W - (coef[0] + coef[1] * X + coef[2] * Y)


# ======================================================================
if __name__ == "__main__":
    app = pg.mkQApp("Front d'onde 3D")

    # --- Calcul -------------------------------------------------------
    X, Y, R, masque = pupille(1200)
    I1, I2, I3, I4 = interferogrammes(front_d_onde_simule(X, Y, R), masque)
    W = derouler(phase_4_pas(I1, I2, I3, I4), masque) / (2 * np.pi)   # en λ
    #W = retirer_piston_tilt(W, X, Y, masque)

    # --- Affichage ----------------------------------------------------
    widget = Wavefront3D(colormap="viridis", subsample=4)
    widget.setWindowTitle("Front d'onde (phase-shifting)")
    widget.resize(1100, 780)
    widget.set_data(W, masque, X, Y)
    widget.show()

    sys.exit(app.exec())