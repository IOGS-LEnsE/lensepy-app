import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, \
    QMessageBox
from lensepy.css import *
from lensepy import translate
from lensepy.modules.camera.basler import BaslerController, BaslerCamera
from lensepy.utils import make_hline, process_hist_from_array, save_hist, save_slice
from lensepy.widgets import LabelWidget, SliderBloc, HistogramWidget, CameraParamsWidget
import numpy as np



class HistoSaveWidget(CameraParamsWidget):
    """
    Widget to control camera parameters and save histogram and slices.
    """

    contrast_activated = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes
        self.image_dir = self.parent.img_dir
        self.contrast_enabled = False
        # Graphical objects
        self.save_histo_button = QPushButton(translate('save_histo_button'))
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.handle_save_histogram)
        self.layout().addWidget(self.save_histo_button)
        self.save_histo_zoom_button = QPushButton(translate('save_histo_zoom_button'))
        self.save_histo_zoom_button.setStyleSheet(unactived_button)
        self.save_histo_zoom_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_histo_zoom_button.clicked.connect(self.handle_save_histogram)
        self.layout().addWidget(self.save_histo_zoom_button)
        self.save_slice_button = QPushButton(translate('save_slice_button'))
        self.save_slice_button.setStyleSheet(disabled_button)
        self.save_slice_button.setEnabled(False)
        self.save_slice_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_slice_button.clicked.connect(self.handle_save_slice)
        self.layout().addWidget(self.save_slice_button)
        self.layout().addWidget(make_hline())
        self.contrast_button = QPushButton(translate('contrast_button'))
        self.contrast_button.setStyleSheet(unactived_button)
        self.contrast_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.contrast_button.clicked.connect(self.handle_contrast)
        self.layout().addWidget(self.contrast_button)
        self.layout().addStretch()

    def handle_contrast(self):
        self.contrast_enabled = not self.contrast_enabled
        button_status = actived_button if self.contrast_enabled else unactived_button
        self.contrast_button.setStyleSheet(button_status)
        self.contrast_activated.emit(self.contrast_enabled)

    def handle_save_slice(self, event):
        self.save_slice_button.setStyleSheet(actived_button)
        self.parent.stop_live()
        image = self.parent.parent.variables['image']
        save_dir = self._get_file_path(self.image_dir)
        if save_dir != '':
            save_slice(image, self.parent.x_cross, self.parent.y_cross, file_path=save_dir)
        self.save_slice_button.setStyleSheet(unactived_button)
        self.parent.start_live()

    def handle_save_histogram(self, event):
        sender = self.sender()
        if sender == self.save_histo_button:
            self.save_histo_button.setStyleSheet(actived_button)
        elif sender == self.save_histo_zoom_button:
            self.save_histo_zoom_button.setStyleSheet(actived_button)

        self.parent.stop_live()
        image = self.parent.parent.variables['image']
        bits_depth = self.parent.parent.variables['bits_depth']
        bins = np.linspace(0, 2 ** bits_depth, 2 ** bits_depth + 1)
        if sender == self.save_histo_button:
            plot_hist, plot_bins_data = process_hist_from_array(image, bins, bits_depth=bits_depth)
        elif sender == self.save_histo_zoom_button:
            plot_hist, plot_bins_data = process_hist_from_array(image, bins, bits_depth=bits_depth, zoom=True)
        save_dir = self._get_file_path(self.image_dir)
        if save_dir != '':
            save_hist(image, plot_hist, plot_bins_data, file_path=save_dir)
        self.parent.start_live()
        self.save_histo_button.setStyleSheet(unactived_button)
        self.save_histo_zoom_button.setStyleSheet(unactived_button)

    def _get_file_path(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            translate('dialog_save_histoe'),
            default_dir,
            "Images (*.png)"
        )

        if file_path != '':
            print(f'Saving path {file_path}')
            return file_path
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return ''