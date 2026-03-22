

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = pg.mkQApp("ImageView Example")

## Create window with ImageView widget
win = QtWidgets.QMainWindow()
win.resize(800,800)

## Create random 3D data set with time varying signals
array_2D = (np.random.rand(20, 20)*255).astype(np.uint8)

imv = pg.ImageItem(image=array_2D)

gr_wid = pg.GraphicsLayoutWidget(show=True)
p1 = gr_wid.addPlot(title="non-interactive")
# Basic steps to create a false color image with color bar:
p1.addItem(imv)
p1.setAspectLocked(True)
p1.addColorBar(imv, colorMap='plasma', interactive=False)
p1.setMouseEnabled(x=False, y=False)
p1.hideButtons()
#p1.setRange(xRange=(0, 20), yRange=(0, 20), padding=0)
p1.showAxes(True, showValues=(True, False, False, True))

win.setCentralWidget(gr_wid)
win.show()

if __name__ == '__main__':
    pg.exec()
