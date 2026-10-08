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
        self.phase = None
        self.size_phase = 0
        self.padding_value = ['2', '4', '8', '16', '32']
        self.padding_selection = 2

        layout = QVBoxLayout()
        self.setLayout(layout)

        # f_number
        '''
        f_number = self.parent.get_variables('f_number') if self.parent.is_variable('f_number')\
            else self.parent.get_initial_params('f_number') or '4'
        '''
        f_number = '4'
        #self.parent.set_variables('f_number', f_number)
        self.f_number = LineEditWidget(title=translate('f_number_param'),
                                       value = f_number)
        # Wavelength
        '''
        w_length = self.parent.get_variables('wavelength') if self.parent.is_variable('wavelength') \
            else self.parent.get_initial_params('wavelength') or '632.8'
        '''
        w_length = '632.8'
        #self.parent.set_variables('wavelength', w_length)
        self.wavelength = LineEditWidget(title=translate('wavelength_param'),
                                         value=w_length, units='nm')

        ## PSF Padding for FFT
        self.padding_selector = ComboBoxBloc(translate('padding_selector'),
                                              self.padding_value,
                                              parent=self.parent,
                                              current=self.padding_selection-1,
                                              default=False)
        self.label_phase_size = LabelValueWidget(translate('label_phase_size'),
                                                   'OK', unit='pixels')
        self.label_padding_size = LabelValueWidget(translate('label_padding_size'),
                                                   'OK', unit='pixels')

        # Lambda / nm
        self.switch_scale = SwitchWidget('\u03BB', 'nm')

        # Global layout
        layout.addWidget(self.f_number)
        layout.addWidget(self.wavelength)
        layout.addWidget(make_hline())
        layout.addWidget(self.padding_selector)
        layout.addWidget(self.label_phase_size)
        layout.addWidget(self.label_padding_size)
        layout.addWidget(make_hline())
        layout.addWidget(self.switch_scale)
        layout.addStretch()

        # Signals
        self.padding_selector.selection_changed.connect(self.handle_padding_changed)

    def set_phase(self, phase):
        self.phase = phase
        _, self.size_phase = phase.get_surface()
        self.label_phase_size.set_value(str(self.size_phase),
                                        'pixels')
        pad_factor = int(self.padding_value[self.padding_selection-1])
        self.label_padding_size.set_value(str(pad_factor * self.size_phase),
                                          'pixels')

    def get_padding_value(self):
        return int(self.padding_value[self.padding_selection-1])

    def handle_padding_changed(self):
        index_pad = self.padding_selector.get_index()
        self.padding_selection = index_pad + 1
        pad_factor = int(self.padding_value[self.padding_selection - 1])
        self.label_padding_size.set_value(str(pad_factor * self.size_phase), 'pixels')

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