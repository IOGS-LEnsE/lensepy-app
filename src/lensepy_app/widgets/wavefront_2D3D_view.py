"""
Front d'onde d'un système optique (phase-shifting à 4 pas) :
affichage 3D (OpenGL) et 2D (image) sous forme de QWidget, pyqtgraph.

Classes : Wavefront3D, Wavefront2D (même API), ViewLink (zoom synchronisé).

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
# Classe de base : données, stats, colormap, sous-échantillonnage
# ======================================================================
class _WavefrontBase(QtWidgets.QWidget):
    """
    API commune :
        set_data(W, masque=None, X=None, Y=None)
        set_colormap(name)
        set_subsample(k, methode=None)     # "moyenne" ou "decimation"
        pv, rms                            # propriétés (pleine résolution)
    Signal : statsChanged(pv, rms)
    """
    statsChanged = QtCore.Signal(float, float)

    def __init__(self, parent=None, colormap="viridis", subsample=1,
                 subsample_method="moyenne"):
        super().__init__(None)
        self.parent = parent
        self._cmap_name = colormap
        self._k = max(1, int(subsample))
        self._methode = subsample_method

        # Données en pleine résolution
        self._W = self._mask = self._X = self._Y = None
        self._pv = self._rms = np.nan

        self.label = QtWidgets.QLabel("PV = –   RMS = –")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self._build_ui()

    # --- à implémenter dans les sous-classes -------------------------
    def _build_ui(self):
        raise NotImplementedError

    def _refresh(self):
        raise NotImplementedError

    # --- API publique -------------------------------------------------
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

    @property
    def pv(self):
        return self._pv

    @property
    def rms(self):
        return self._rms

    # --- utilitaires internes ----------------------------------------
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

        # Moyenne par blocs k x k sur les pixels valides de la pupille
        n = (W.shape[0] // k) * k
        m = (W.shape[1] // k) * k
        blocs = lambda A: A[:n, :m].reshape(n // k, k, m // k, k)

        cnt = blocs(masque.astype(float)).sum(axis=(1, 3))
        Wb = blocs(np.where(masque, W, 0.0)).sum(axis=(1, 3)) / np.maximum(cnt, 1)
        Xb = blocs(X).mean(axis=(1, 3))
        Yb = blocs(Y).mean(axis=(1, 3))
        mb = cnt >= 0.5 * k * k
        return np.where(mb, Wb, 0.0), mb, Xb, Yb

    def _donnees_affichage(self):
        """Renvoie W, masque, X, Y sous-échantillonnés + cmap, vmin, vmax (pleine résolution)."""
        W, masque, X, Y = self._sous_echantillonner(
            self._W, self._mask, self._X, self._Y, self._k, self._methode)
        vals = self._W[self._mask]
        return W, masque, X, Y, self._get_cmap(), vals.min(), vals.max()


# ======================================================================
# Affichage 3D (OpenGL)
# ======================================================================
class _GLView(gl.GLViewWidget):
    """GLViewWidget qui émet cameraChanged quand le zoom ou le centre change."""
    cameraChanged = QtCore.Signal()

    def _etat(self):
        c = self.opts["center"]
        return (self.opts["distance"], c.x(), c.y(), c.z())

    def _puis_signaler(self, handler, ev):
        avant = self._etat()
        handler(ev)
        if self._etat() != avant:
            self.cameraChanged.emit()

    def wheelEvent(self, ev):
        self._puis_signaler(super().wheelEvent, ev)

    def mouseMoveEvent(self, ev):
        self._puis_signaler(super().mouseMoveEvent, ev)


class Wavefront3D(_WavefrontBase):
    """Surface 3D OpenGL + barre de couleur + stats. set_z_scale() en plus."""
    viewChanged = QtCore.Signal()

    def __init__(self, parent=None, colormap="viridis", subsample=1,
                 subsample_method="moyenne", z_scale=1.0):
        super().__init__(parent, colormap, subsample, subsample_method)
        self._z_scale = z_scale

    def _build_ui(self):
        self._surf = None
        self._z_scale = 1.0

        self.view = _GLView()
        self.view.cameraChanged.connect(self.viewChanged)
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

        haut = QtWidgets.QHBoxLayout()
        haut.addWidget(self.view, stretch=1)
        haut.addWidget(self._cb_widget)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(haut, stretch=1)
        lay.addWidget(self.label)

    # --- état de la vue (pour la synchronisation avec la vue 2D) -----
    def view_state(self):
        """(cx, cy, largeur) : largeur = étendue en x visible au point visé."""
        o = self.view.opts
        c = o["center"]
        largeur = 2 * o["distance"] * np.tan(np.radians(o["fov"]) / 2)
        return c.x(), c.y(), largeur

    def set_view_state(self, largeur, cx=None, cy=None):
        o = self.view.opts
        o["distance"] = largeur / (2 * np.tan(np.radians(o["fov"]) / 2))
        c = o["center"]
        o["center"] = pg.Vector(c.x() if cx is None else cx,
                                c.y() if cy is None else cy, c.z())
        self.view.update()

    def set_z_scale(self, z_scale):
        self._z_scale = z_scale
        if self._W is not None:
            self._refresh()

    def _refresh(self):
        W, masque, X, Y, cmap, vmin, vmax = self._donnees_affichage()
        etendue = max(vmax - vmin, 1e-12)

        norm = np.clip((W - vmin) / etendue, 0, 1)
        colors = cmap.map(norm.ravel(), mode="float").reshape(*W.shape, 4)
        colors[~masque, 3] = 0.0              # hors pupille : transparent

        z = np.where(masque, W, self._W[self._mask].mean())
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
# Affichage 2D (image)
# ======================================================================
class Wavefront2D(_WavefrontBase):
    """Carte 2D du front d'onde (ImageItem) + ColorBarItem + stats."""
    viewChanged = QtCore.Signal()

    def _build_ui(self):
        self.glw = pg.GraphicsLayoutWidget()
        self.plot = self.glw.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.setLabel("bottom", "x (pupille normalisée)")
        self.plot.setLabel("left", "y (pupille normalisée)")
        self.plot.getViewBox().sigRangeChanged.connect(
            lambda *args: self.viewChanged.emit())

        self.img = pg.ImageItem()             # tableau indexé [x, y] (col-major)
        self.plot.addItem(self.img)

        self.cbar = pg.ColorBarItem(values=(0, 1), interactive=False,
                                    label="Front d'onde (λ)")
        self.cbar.setImageItem(self.img, insert_in=self.plot)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.glw, stretch=1)
        lay.addWidget(self.label)

    # --- état de la vue (pour la synchronisation avec la vue 3D) -----
    def view_state(self):
        """(cx, cy, largeur) : centre et étendue en x de la zone visible."""
        r = self.plot.getViewBox().viewRect()
        return r.center().x(), r.center().y(), r.width()

    def set_view_state(self, largeur, cx=None, cy=None):
        vb = self.plot.getViewBox()
        r = vb.viewRect()
        if r.width() <= 0:
            return
        cx = r.center().x() if cx is None else cx
        cy = r.center().y() if cy is None else cy
        h = r.height() * largeur / r.width()          # garde le rapport d'aspect
        vb.setRange(xRange=(cx - largeur / 2, cx + largeur / 2),
                    yRange=(cy - h / 2, cy + h / 2), padding=0)

    def _refresh(self):
        W, masque, X, Y, cmap, vmin, vmax = self._donnees_affichage()

        # Hors pupille : NaN (rendu transparent)
        img = np.where(masque, W, np.nan)
        self.img.setImage(img.T, autoLevels=False)    # .T : [x, y]
        self.cbar.setColorMap(cmap)
        self.cbar.setLevels((vmin, vmax))

        # Position/échelle de l'image en coordonnées de la pupille
        nx, ny = W.shape[1], W.shape[0]
        dx = (X.max() - X.min()) / max(nx - 1, 1)
        dy = (Y.max() - Y.min()) / max(ny - 1, 1)
        self.img.setRect(QtCore.QRectF(X.min() - dx / 2, Y.min() - dy / 2,
                                       dx * nx, dy * ny))
        self.plot.autoRange()


# ======================================================================
# Synchronisation du zoom (et du déplacement) entre deux vues
# ======================================================================
class ViewLink(QtCore.QObject):
    """
    Synchronise le zoom (et, si pan=True, le centre) de deux widgets
    Wavefront2D / Wavefront3D, dans les deux sens.
    À conserver dans une variable (sinon il est détruit).

        lien = ViewLink(w2d, w3d)
        lien.set_enabled(False)
    """

    def __init__(self, a, b, pan=True, parent=None):
        super().__init__(parent)
        self._a, self._b, self._pan = a, b, pan
        self._busy = False
        self._enabled = True
        a.viewChanged.connect(lambda: self._sync(a, b))
        b.viewChanged.connect(lambda: self._sync(b, a))
        self._sync(a, b)                      # alignement initial sur a

    def set_enabled(self, on):
        self._enabled = bool(on)
        if self._enabled:
            self._sync(self._a, self._b)

    def _sync(self, src, dst):
        if self._busy or not self._enabled:
            return
        self._busy = True                     # évite les rebonds a -> b -> a
        try:
            cx, cy, largeur = src.view_state()
            if largeur > 0:
                if self._pan:
                    dst.set_view_state(largeur, cx, cy)
                else:
                    dst.set_view_state(largeur)
        finally:
            self._busy = False


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


def interferogrammes(W, masque, bruit=0.02):
    phi = 2 * np.pi * W
    return [np.where(masque, 0.5 + 0.4 * np.cos(phi + d) + bruit * np.random.randn(*W.shape), 0.0)
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
# Démo : 2D et 3D côte à côte, colormap et sous-échantillonnage partagés
# ======================================================================
if __name__ == "__main__":
    app = pg.mkQApp("Front d'onde")

    # --- Calcul -------------------------------------------------------
    X, Y, R, masque = pupille(200)
    I1, I2, I3, I4 = interferogrammes(front_d_onde_simule(X, Y, R), masque)
    W = derouler(phase_4_pas(I1, I2, I3, I4), masque) / (2 * np.pi)   # en λ
    W = retirer_piston_tilt(W, X, Y, masque)

    # --- Affichage ----------------------------------------------------
    fen = QtWidgets.QWidget()
    fen.setWindowTitle("Front d'onde (phase-shifting)")
    w2d = Wavefront2D(colormap="viridis", subsample=1)
    w3d = Wavefront3D(colormap="viridis", subsample=4)

    combo = QtWidgets.QComboBox()
    combo.addItems(["viridis", "inferno", "plasma", "magma", "cividis"])
    spin = QtWidgets.QSpinBox()
    spin.setRange(1, 10)
    spin.setValue(4)
    spin.setPrefix("sous-éch. 3D : ")
    chk = QtWidgets.QCheckBox("Zoom synchronisé")
    chk.setChecked(True)
    btn = QtWidgets.QPushButton("Réinitialiser la vue")

    combo.currentTextChanged.connect(w2d.set_colormap)
    combo.currentTextChanged.connect(w3d.set_colormap)
    spin.valueChanged.connect(w3d.set_subsample)

    barre = QtWidgets.QHBoxLayout()
    barre.addWidget(QtWidgets.QLabel("Colormap :"))
    barre.addWidget(combo)
    barre.addWidget(spin)
    barre.addWidget(chk)
    barre.addWidget(btn)
    barre.addStretch()

    centre = QtWidgets.QHBoxLayout()
    centre.addWidget(w2d, stretch=1)
    centre.addWidget(w3d, stretch=1)

    lay = QtWidgets.QVBoxLayout(fen)
    lay.addLayout(barre)
    lay.addLayout(centre, stretch=1)

    lien = ViewLink(w2d, w3d)                 # garder la référence !
    chk.toggled.connect(lien.set_enabled)
    btn.clicked.connect(lambda: w2d.plot.autoRange())   # la vue 3D suit

    w2d.set_data(W, masque, X, Y)
    w3d.set_data(W, masque, X, Y)

    fen.resize(1500, 780)
    fen.show()
    sys.exit(app.exec())