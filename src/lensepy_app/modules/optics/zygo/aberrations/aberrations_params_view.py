# -*- coding: utf-8 -*-
"""
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2026
"""
import sys, os, time
from lensepy import load_dictionary, translate, dictionary, is_float
from lensepy.css import *
from lensepy_app.widgets import Surface2DView
from lensepy_app.widgets.objects import *
from lensepy_app import make_hline
from lensepy_app.widgets.objects import *
from lensepy_app.appli._app.main_view import get_disp_mode
from lensepy_app.modules.optics.zygo.interfer_control.interfer_control_view import PVRMSView
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication
)
from PyQt6.QtCore import pyqtSignal


class ParamsView(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, parent=None):
        super(ParamsView, self).__init__(None)
        self.parent = parent # controller
        self.setWindowTitle(translate('params_window'))
        self.setMinimumWidth(300)
        self.general_display_mode = get_disp_mode(self.parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # f_number
        f_number = self.parent.get_variables('f_number') if self.parent.is_variable('f_number')\
            else self.parent.get_initial_params('f_number') or '4'
        self.parent.set_variables('f_number', f_number)
        self.f_number = LineEditWidget(title=translate('f_number_param'),
                                       value = f_number)
        layout.addWidget(self.f_number)
        # Wavelength
        w_length = self.parent.get_variables('wavelength') if self.parent.is_variable('wavelength') \
            else self.parent.get_initial_params('wavelength') or '632.8'
        self.parent.set_variables('wavelength', w_length)
        self.wavelength = LineEditWidget(title=translate('wavelength_param'),
                                         value=w_length, units='nm')
        layout.addWidget(self.wavelength)
        layout.addStretch()

        # Signals


    def closeEvent(self, event):
        ## Update all the processes !!!
        w_length = self.wavelength.get_value()
        self.parent.set_variables('wavelength', w_length)
        f_number = self.f_number.get_value()
        self.parent.set_variables('f_number', f_number)

        # Send signal to controller
        self.window_closed.emit()
        event.accept()




def main():

    app = QApplication(sys.argv)
    window = ParamsView()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()