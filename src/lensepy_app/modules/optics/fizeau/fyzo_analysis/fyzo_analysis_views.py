from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from lensepy import translate

from lensepy.css import *
from lensepy_app.widgets.objects import *
from lensepy_app.widgets import ImageDisplayWidget
from lensepy_app.widgets.double_3d_view import Surface3DView


class FyzoAnalysisOptionsView(QWidget):

    display_changed = pyqtSignal(str)
    view_saved = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('fyzo_analysis_parameter_label'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # different display
        self.interfer_button = QPushButton(translate('interfer_display_button'))
        self.interfer_button.setStyleSheet(unactived_button)
        self.interfer_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.interfer_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.interfer_button)

        self.fft_button = QPushButton(translate('fft_display_button'))
        self.fft_button.setStyleSheet(unactived_button)
        self.fft_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_button)

        self.fft_masked_button = QPushButton(translate('fft_masked_display_button'))
        self.fft_masked_button.setStyleSheet(unactived_button)
        self.fft_masked_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_masked_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_masked_button)

        self.fft_centered_button = QPushButton(translate('fft_centered_display_button'))
        self.fft_centered_button.setStyleSheet(unactived_button)
        self.fft_centered_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.fft_centered_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.fft_centered_button)

        self.phase_button = QPushButton(translate('phase_display_button'))
        self.phase_button.setStyleSheet(unactived_button)
        self.phase_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.phase_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.phase_button)
        layout.addWidget(make_hline())
        self.surface_button = QPushButton(translate('surface_display_button'))
        self.surface_button.setStyleSheet(unactived_button)
        self.surface_button.setFixedHeight(BUTTON_HEIGHT)
        self.surface_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.surface_button)
        layout.addWidget(make_hline())

        self.surface_3D_button = QPushButton(translate('surface_3D_display_button'))
        self.surface_3D_button.setStyleSheet(unactived_button)
        self.surface_3D_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.surface_3D_button.clicked.connect(self.handle_display_changed)
        layout.addWidget(self.surface_3D_button)
        layout.addWidget(make_hline())
        layout.addStretch()
        self.saving_button = QPushButton(translate('saving_png_button'))
        self.saving_button.setStyleSheet(unactived_button)
        self.saving_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.saving_button.clicked.connect(self.handle_saving_png)
        layout.addWidget(self.saving_button)
        layout.addStretch()
        self.setLayout(layout)

    def activate_mode(self, value):
        if value == 'surface':
            self.surface_button.setStyleSheet(actived_button)
        if value == 'surface_3D':
            self.surface_3D_button.setStyleSheet(actived_button)
        elif value == 'interfer':
            self.interfer_button.setStyleSheet(actived_button)
        elif value == 'fft':
            self.fft_button.setStyleSheet(actived_button)
        elif value == 'fft_masked':
            self.fft_masked_button.setStyleSheet(actived_button)
        elif value == 'fft_centered':
            self.fft_centered_button.setStyleSheet(actived_button)
        elif value == 'phase':
            self.phase_button.setStyleSheet(actived_button)

    def _inactivate_buttons(self):
        self.fft_button.setStyleSheet(unactived_button)
        self.interfer_button.setStyleSheet(unactived_button)
        self.fft_masked_button.setStyleSheet(unactived_button)
        self.fft_centered_button.setStyleSheet(unactived_button)
        self.phase_button.setStyleSheet(unactived_button)
        self.surface_button.setStyleSheet(unactived_button)
        self.surface_3D_button.setStyleSheet(unactived_button)

    def handle_display_changed(self):
        sender = self.sender()
        self._inactivate_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.interfer_button:
            self.display_changed.emit('interfer')
        elif sender == self.fft_button:
            self.display_changed.emit('fft')
        elif sender == self.fft_masked_button:
            self.display_changed.emit('fft_masked')
        elif sender == self.fft_centered_button:
            self.display_changed.emit('fft_centered')
        elif sender == self.phase_button:
            self.display_changed.emit('phase')
        elif sender == self.surface_button:
            self.display_changed.emit('surface')
        elif sender == self.surface_3D_button:
            self.display_changed.emit('surface_3D')
        else:
            self.display_changed.emit('interfer')

    def handle_saving_png(self):
        file_dialog = QFileDialog()
        # default dir ?
        default_dir = self.parent.get_config('img_dir') or None
        # dialog box
        file_path, _ = file_dialog.getSaveFileName(self, translate('dialog_view_png_image'),
                                                   default_dir, "Images (*.png)")
        if file_path != '':
            self.view_saved.emit(file_path)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Saved")
            dlg.setText("No Image File was saved...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return


class Fyzo3DSurfaceView(QWidget):

    surface_3D_saved = pyqtSignal(str)

    def __init__(self, parent=None, surface=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        view_3D = Surface3DView()
        if surface is not None:
            x, y, w_s = view_3D.prepare_data_for_mesh(surface, undersampling=1)
            view_3D.create_mesh_surface(x, y, w_s)
            view_3D.showMaximized()

        layout.addWidget(view_3D)

        # Saving button
        self.save_button = QPushButton(translate('save_png_button'))
        self.save_button.setStyleSheet(unactived_button)
        self.save_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_button.clicked.connect(self.handle_saving_png)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def handle_saving_png(self):
        file_dialog = QFileDialog()
        # default dir ?
        default_dir = self.parent.get_config('img_dir') or None
        # dialog box
        file_path, _ = file_dialog.getSaveFileName(self, translate('dialog_view_png_image'),
                                                   default_dir, "Images (*.png)")
        if file_path != '':
            self.surface_3D_saved.emit(file_path)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Saved")
            dlg.setText("No Image File was saved...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return