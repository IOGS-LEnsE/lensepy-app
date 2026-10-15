# -*- coding: utf-8 -*-
"""
.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys
from lensepy import translate
from lensepy_app import *
from lensepy_app.appli import *
from lensepy_app.widgets import Surface2DView
from lensepy_app.widgets.objects import *
from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QWidget,
    QVBoxLayout, QApplication
)
from PyQt6.QtCore import pyqtSignal


display_options_values = [
    'psf_and_slice',
    'psf_only',
    'psf_log',
    'psf_slice',
    'ftm_and_slice',
    'ftm_only',
    'ftm_slice',
    'circled_energy'
]


class AnalysisInProgressView(ModuleWidget):
    """Analysis in progress."""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout()
        self.text = translate('analysis_in_progress')
        self.label = QLabel(self.text)
        self.label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self, step: 0):
        self.text = translate('analysis_in_progress')
        if step >= 1:
            self.text += '\n'+translate('analysis_phase_ok')
        if step >= 2:
            self.text += '\n'+translate('analysis_auto_mask_ok')
        if step >= 3:
            self.text += '\n'+translate('analysis_surface_ok')
        if step >= 4:
            self.text += '\n'+translate('analysis_zernike_ok')

        self.label.setText(self.text)
        self.label.repaint()


class PSFInProgressView(ModuleWidget):
    """Analysis in progress."""
    def __init__(self, parent=None):
        super().__init__(None)
        layout = QVBoxLayout()
        self.text = translate('psf_in_progress')
        self.label = QLabel(self.text)
        self.label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self, step: 0):
        self.text = translate('psf_in_progress')
        if step >= 1:
            self.text += '\n'+translate('psf_phase_ok')

        self.label.setText(self.text)
        self.label.repaint()


class SurfaceOptionsView(ModuleWidget):

    selection_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.surface = Surface2DView(translate('interferogram'),
                                     colormap_2D='gray', parent=self.controller)
        self.options = OptionsView(parent=self.controller)

        layout.addWidget(self.surface, 4)
        layout.addWidget(self.options, 1)

        # Signals
        self.options.selection_changed.connect(self.handle_selection_changed)

    def set_surface(self, surface):
        self.surface.set_array(surface)

    def set_visible(self, index, value=True):
        self.options.set_visible(index, value)

    def handle_selection_changed(self, index, value):
        self.selection_changed.emit(index, value)


class OptionsView(ModuleWidget):

    selection_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QVBoxLayout()
        self.setLayout(layout)
        display_options_values_tr = [translate(x)
                                     for x in display_options_values]

        self.top_right_option = ComboBoxBloc(translate('top_right_option'),
                                             display_options_values_tr,
                                             parent=self.controller,
                                             default=False,
                                             vertical=True)
        self.bot_right_option = ComboBoxBloc(translate('bot_right_option'),
                                             display_options_values_tr,
                                             parent=self.controller,
                                             default=False,
                                             vertical=True)
        self.info_option = PSFInProgressView(parent=self.controller)

        layout.addWidget(self.top_right_option)
        self.top_right_option.hide()
        layout.addWidget(make_hline())
        layout.addWidget(self.bot_right_option)
        self.bot_right_option.hide()
        layout.addStretch()
        layout.addWidget(self.info_option)

        # Signals
        self.top_right_option.selection_changed.connect(self.handle_selection_changed)
        self.bot_right_option.selection_changed.connect(self.handle_selection_changed)

    def set_visible(self, index, value=True):
        if value:
            if index == 'top':
                self.top_right_option.show()
            if index == 'bot':
                self.bot_right_option.show()
            if index == 'info':
                self.info_option.hide()
        else:
            if index == 'top':
                self.top_right_option.hide()
            if index == 'bot':
                self.bot_right_option.hide()
            if index == 'info':
                self.info_option.show()

    def update_info(self, index):
        self.info_option.update_text(index)

    def handle_selection_changed(self):
        sender = self.sender()
        if sender == self.top_right_option:
            value = sender.get_text()
            self.selection_changed.emit('top', value)
        elif sender == self.bot_right_option:
            value = sender.get_text()
            self.selection_changed.emit('bot', value)


class TwoChartWidget(ModuleWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.chart_1 = XYChartWidget()
        self.chart_2 = XYChartWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.chart_1)
        layout.addWidget(self.chart_2)
        self.setLayout(layout)

    def set_background(self, color):
        self.chart_1.set_background(color)
        self.chart_2.set_background(color)

    def set_data1(self, x_axis, y_axis, x_label: str = '', y_label: str = ''):
        self.chart_1.set_data(x_axis, y_axis, x_label, y_label)

    def set_legend1(self, y_legend, x=0, y=0):
        self.chart_1.set_legend(y_legend, x, y)

    def set_legend2(self, y_legend, x=0, y=0):
        self.chart_2.set_legend(y_legend, x, y)

    def set_data2(self, x_axis, y_axis, x_label: str = '', y_label: str = ''):
        self.chart_2.set_data(x_axis, y_axis, x_label, y_label)

    def set_title1(self, title):
        self.chart_1.set_title(title)

    def set_title2(self, title):
        self.chart_2.set_title(title)

    def refresh_chart(self):
        self.chart_1.refresh_chart()
        self.chart_2.refresh_chart()


class AberrationsView(ModuleWidget):
    def __init__(self, parent=None, colormap='plasma'):
        super().__init__(parent=parent)
        m_layout = QVBoxLayout()
        widget1 = QWidget()
        layout1 = QHBoxLayout()
        widget1.setLayout(layout1)
        widget2 = QWidget()
        layout2 = QHBoxLayout()
        widget2.setLayout(layout2)
        m_layout.addWidget(widget1)
        m_layout.addWidget(widget2)
        self.setLayout(m_layout)

        self.unwrapped_surface = Surface2DView(
            translate('unwrapped_surface_no_correction'), colormap,
            parent=self.controller)
        layout1.addWidget(self.unwrapped_surface)
        self.unwrapped_surface_corr = Surface2DView(
            translate('unwrapped_surface_correction'), colormap,
            parent=self.controller)
        layout1.addWidget(self.unwrapped_surface_corr)

        self.psf_unwrapped = Surface2DView(translate('psf_unwrapped_surface'),
                                           colormap, parent=self.controller)
        layout2.addWidget(self.psf_unwrapped)
        self.psf_corrected = Surface2DView(translate('psf_corrected_surface'),
                                           colormap, parent=self.controller)
        layout2.addWidget(self.psf_corrected)

    def set_array_uncorrect(self, image):
        self.unwrapped_surface.set_array(image)

    def set_array_correct(self, image):
        self.unwrapped_surface_corr.set_array(image)

    def set_psf_uncorrect(self, surface):
        self.psf_unwrapped.set_array(surface)

    def reset_z_range(self):
        self.unwrapped_surface.reset_z_range()
        self.unwrapped_surface_corr.reset_z_range()

    def set_title_uncorrect(self, title):
        self.unwrapped_surface.set_title(title)

    def set_title_correct(self, title):
        self.unwrapped_surface_corr.set_title(title)


def main():

    app = QApplication(sys.argv)
    window = CoefficientsView()
    window.set_coeffs([1.01, -3.3, 2.5, 5.2, -6.7, 1.01,
                       -3.3, 2.5, 5.2, -6.7, 1.01, -3.3,
                       2.5, 5.2, -6.7, 1.01, -3.3, 2.5,
                       5.2, -0.7, 1.01, -0.3, 2.5, 5.2,
                       -6.7, 0.01, 0, 0.5, 5.2, -6.7,
                       1.01, -3.3, 2.5, 5.2, -0.7, 1.01, 0.5])
    window.set_pv_rms_uncorrected(1.5, -0.2, 'nm')
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()