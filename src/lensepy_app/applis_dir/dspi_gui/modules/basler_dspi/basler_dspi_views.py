from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QLineEdit, QGridLayout, QPushButton, QMainWindow, QVBoxLayout, QLabel, QHBoxLayout

from lensepy_app import *
from lensepy_app.appli import *
from lensepy import translate
from lensepy.utils import is_integer

from typing import TYPE_CHECKING

from lensepy_app.widgets import LabelWidget
from lensepy_app.widgets.objects import SelectWidget

if TYPE_CHECKING:
    from .basler_dspi_controller import BaslerDSPIController
    from .basler_dspi_models import BaslerDSPICamera

class CameraInfosWidget(ModuleWidget):
    """
    Widget to display image infos.
    """
    color_mode_changed = pyqtSignal(str)
    roi_changed = pyqtSignal(list)
    roi_centered = pyqtSignal(list)
    roi_reset = pyqtSignal()
    roi_activated = pyqtSignal(bool)
    open_fft = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Attributes
        self.parent: BaslerDSPIController = parent  # BaslerDSPIController or any CameraController
        self.roi_activated_state = self.controller.get_variables("roi_activated")
        self.camera = self.controller.get_variables('camera')     # Camera connected to the Controller
        # Graphical objects
        layout = QVBoxLayout()

        label = QLabel(translate("Informations caméra - Camera infos"))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('Type - Name'), '',
                                      parent=self.controller)       # Camera Name
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('Numéro de série - Serial number'), '',
                                        parent=self.controller)   # Serial number of the camera
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('Taille du capteur - Camera size'), '', 'pixels')     # Dimensions of the camera
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = SelectWidget(translate('Couleur - Color format'), self.color_choice,
                                             parent=self.controller)   # Image format given by the camera
        self.label_color_mode.choice_selected.connect(self.handle_color_mode_changed)
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())

        self.roi_widget = CameraROIWidget(self.controller)  # Widget to the control the ROI on the camera
        self.roi_widget.roi_checked.connect(self.handle_roi_checked)
        self.roi_widget.roi_centered.connect(lambda coords: self.roi_centered.emit(coords))
        self.roi_widget.roi_reset.connect(lambda: self.roi_reset.emit())
        self.roi_widget.roi_changed.connect(lambda coords: self.roi_changed.emit(coords))
        layout.addWidget(self.roi_widget)

        self.activate_roi_button = QPushButton(translate("Valider la zone d'intérêt - Activate ROI"))    # Button to turn the ROI on
        self.activate_roi_button.setFixedHeight(BUTTON_HEIGHT[self.global_theme][self.global_mode])
        if self.roi_activated_state:
            self.activate_roi_button.setStyleSheet(ACTIVATED_BUTTON[self.global_theme][self.global_mode])
        else:
            self.activate_roi_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.activate_roi_button.clicked.connect(self.handle_roi_activated)
        layout.addWidget(self.activate_roi_button)

        self.open_button = QPushButton(translate("FFT"))  # Button to display the Fourier Transform of the image
        self.open_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.open_button.clicked.connect(self.handle_open_fft)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)
        self.update_infos()

    def set_enabled_roi_widget(self, value):
        """
        Activate ROI selection widget.
        :param value:   True to activate ROI selection widget.
        """
        self.roi_widget.set_enabled(value)

    def set_roi(self, coords: list):
        """
        Set new values for ROI.
        :param coords: x0, y0, x1, y1 coordinates of the ROI.
        """
        self.roi_widget.set_roi(coords)

    def handle_color_mode_changed(self, event):
        """
        Action performed when color mode is changed.
        """
        self.color_mode_changed.emit(event)

    def handle_roi_checked(self, value):
        self.activate_roi_button.setEnabled(value)
        button_mode = disabled_button if not value else unactived_button
        self.activate_roi_button.setStyleSheet(button_mode)
        self.roi_checked.emit(value)

    def handle_roi_activated(self):
        """
        Action performed when the ROI is activated
        """
        self.roi_activated_state = not self.roi_activated_state
        if self.roi_activated_state:
            self.activate_roi_button.setStyleSheet(actived_button)
        else:
            self.activate_roi_button.setStyleSheet(unactived_button)
        self.roi_activated.emit(self.roi_activated_state)

    def handle_open_fft(self):
        """
        Action performed when the FFT button is triggered
        """
        self.open_fft.emit()

    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera: BaslerDSPICamera = self.parent.get_variables()['camera']
        if self.parent.camera_connected:
            self.camera.open()
            self.label_name.set_value(self.camera.get_parameter('DeviceModelName'))
            self.label_serial.set_value(self.camera.get_parameter('DeviceSerialNumber'))
            w = str(self.camera.get_parameter('SensorWidth'))
            h = str(self.camera.get_parameter('SensorHeight'))
            self.label_size.set_value(f'WxH = {w} x {h}')
            self.camera.close()
        else:
            self.label_name.set_value(translate('no_camera'))
            self.label_serial.set_value(translate('no_camera'))
            self.label_size.set_value('')


class CameraROIWidget(ModuleWidget):
    """
    Interaction widget to select ROI of an image.
    """
    roi_checked = pyqtSignal(bool)
    roi_changed = pyqtSignal(list)
    roi_centered = pyqtSignal(list)
    roi_reset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent: BaslerDSPIController = parent   #BaslerDSPIController (see basler_dspi_controller)
        # Attributes
        self.coords = [0, 0, 0, 0]   # x0, y0, x1, y1
        # Graphical objects
        layout = QVBoxLayout()
        self.setLayout(layout)
        label = QLabel(translate("Zone d'intérêt - ROI"))
        label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        # X0, Y0, X1, Y1, W, H widget
        self.roi_select = ROISelectWidget(self.controller)
        self.roi_select.roi_changed.connect(self.handle_roi_changed)
        layout.addWidget(self.roi_select)
        if self.controller.get_variables("roi_coords") is not None:
            self.roi_select.set_values(self.controller.get_variables("roi_coords"))
        else:
            self.roi_select.set_values([0, 0, 0, 0])
        # Button to center the ROI
        self.center_roi_button = QPushButton(translate("Centrer la zone d'intérêt - ROI center"))
        self.center_roi_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.center_roi_button.setFixedHeight(BUTTON_HEIGHT[self.global_theme][self.global_mode])
        self.center_roi_button.clicked.connect(self.handle_roi_centered)
        layout.addWidget(self.center_roi_button)
        # Button to reset the ROI to the whole size of the camera
        self.reset_roi_button = QPushButton(translate("Image complète - ROI reset"))
        self.reset_roi_button.setStyleSheet(INACTIVATED_BUTTON[self.global_theme][self.global_mode])
        self.reset_roi_button.setFixedHeight(BUTTON_HEIGHT[self.global_theme][self.global_mode])
        self.reset_roi_button.clicked.connect(self.handle_roi_reset)
        layout.addWidget(self.reset_roi_button)

    def handle_roi_centered(self):
        """
        Recalculate ROI position to center it
        """
        coords = self.roi_select.get_values()
        self.roi_centered.emit(coords)

    def handle_roi_reset(self):
        """
        Reset ROI to the maximum range of the camera
        """
        self.roi_reset.emit()

    def handle_roi_changed(self, coords):
        """
        Action performed when ROI is selected.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        self.roi_changed.emit(coords)

    def set_roi(self, coords):
        """
        Set values for ROI.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        self.roi_select.set_values(coords)

    def set_enabled(self, value):
        """
        Enable/disable ROI widget.
        :param value:   True to enable, False to disable.
        """
        self.center_roi_button.setEnabled(value)
        self.reset_roi_button.setEnabled(value)
        self.roi_select.set_enabled(value)
        button_status = DISABLED_BUTTON[self.global_theme][self.global_mode] if not value \
            else INACTIVATED_BUTTON[self.global_theme][self.global_mode]
        self.center_roi_button.setStyleSheet(button_status)
        self.reset_roi_button.setStyleSheet(button_status)


class ROISelectWidget(ModuleWidget):
    """
    Widget to manage the selection of a ROI for an image
    """
    roi_changed = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QGridLayout()
        self.setLayout(layout)
        # Corners of the ROI
        self.x0_label = LineEditWidget(translate("Position horizontale x0"), value='',
                                       parent=self.controller)
        self.x0_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        self.y0_label = LineEditWidget(translate("Position verticale y0 "), value='',
                                       parent=self.controller)
        self.y0_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        self.x1_label = LineEditWidget(translate("Position horizontale x1"), value='',
                                       parent=self.controller)
        self.x1_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        self.y1_label = LineEditWidget(translate("Position horizontale y1"), value='',
                                       parent=self.controller)
        self.y1_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        # Width and Height of the ROI
        self.w_label = LineEditWidget(translate("Largeur (x1-x0)" ), value='',
                                       parent=self.controller)
        self.w_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        self.h_label = LineEditWidget(translate("Hauteur (y1-y0)"), value='',
                                       parent=self.controller)
        self.h_label.setStyleSheet(STYLE_H2[self.global_theme][self.global_mode])
        # All enabled
        self.set_enabled(True)
        self.coords = None
        self.width_old = 0
        self.height_old = 0

        layout.addWidget(self.x0_label, 0, 0)
        layout.addWidget(self.y0_label, 0, 1)
        layout.addWidget(self.x1_label, 1, 0)
        layout.addWidget(self.y1_label, 1, 1)
        layout.addWidget(self.w_label, 2, 0)
        layout.addWidget(self.h_label, 2, 1)

        # Signals
        self.x0_label.edit_changed.connect(self.handle_edit_changed)
        self.y0_label.edit_changed.connect(self.handle_edit_changed)
        self.x1_label.edit_changed.connect(self.handle_edit_changed)
        self.y1_label.edit_changed.connect(self.handle_edit_changed)
        self.w_label.edit_changed.connect(self.handle_edit_changed)
        self.h_label.edit_changed.connect(self.handle_edit_changed)

    def set_values(self, coords: list):
        """
        Set initial values for ROI.
        :param coords:  x0, y0, x1, y1 coordinates.
        """
        self.coords = coords
        self.width_old = self.coords[2] - self.coords[0]
        self.height_old = self.coords[3] - self.coords[1]
        self.update_values()

    def get_values(self):
        """
        Get ROI coordinates
        """
        return self.coords

    def update_values(self):
        """
        Update graphical objects with new values
        """
        self.x0_label.set_value(str(self.coords[0]))
        self.y0_label.set_value(str(self.coords[1]))
        self.x1_label.set_value(str(self.coords[2]))
        self.y1_label.set_value(str(self.coords[3]))
        self.h_label.set_value(str(self.height_old))
        self.w_label.set_value(str(self.width_old))

    def handle_edit_changed(self, value):
        """
        Action performed when ROI is edited.
        This function checks whether the value is an integer before storing it.
        It then checks which parameter has been modified
        :param value:   New ROI value.
        """
        sender = self.sender()
        if is_integer(value):
            if sender == self.x0_label:
                self.coords[0] = int(value)
            elif sender == self.y0_label:
                self.coords[1] = int(value)
            elif sender == self.x1_label:
                self.coords[2] = int(value)
            elif sender == self.y1_label:
                self.coords[3] = int(value)
            elif sender == self.w_label:
                # Width changed
                self.width_old = int(value)
                self.coords[2] = self.coords[0] + self.width_old
            elif sender == self.h_label:
                self.height_old = int(value)
                self.coords[3] = self.coords[1] + self.height_old
            self.roi_changed.emit(self.coords)
        else:
            if sender == self.x0_label:
                self.x0_label.line_edit.setText(str(self.coords[0]))
            elif sender == self.y0_label:
                self.y0_label.line_edit.setText(str(self.coords[1]))
            elif sender == self.x1_label:
                self.x1_label.line_edit.setText(str(self.coords[2]))
            elif sender == self.y1_label:
                self.y1_label.line_edit.setText(str(self.coords[3]))

    def set_enabled(self, value: bool=True):
        """
        Set the widget enabled.
        :param value:   True or False.
        """
        self.x0_label.set_enabled(value)
        self.y0_label.set_enabled(value)
        self.x1_label.set_enabled(value)
        self.y1_label.set_enabled(value)
        self.w_label.set_enabled(value)
        self.h_label.set_enabled(value)


class LineEditWidget(ModuleWidget):
    """
    Widget for line edit, including a title.
    """
    edit_changed = pyqtSignal(str)
    def __init__(self, title:str='', value='', parent=None):
        super().__init__(parent=parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.value = value

        # Label
        self.label = QLabel(title)
        layout.addWidget(self.label, 1)
        # Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setText(value)
        self.line_edit.editingFinished.connect(lambda: self.edit_changed.emit(self.line_edit.text()))
        layout.addWidget(self.line_edit, 2)

    def set_value(self, value):
        """
        Set the widget value in the line edit object.
        :param value:   Value to set.
        """
        self.line_edit.setText(value)

    def set_enabled(self, value: bool=True):
        """
        Set the widget enabled.
        :param value:   True or False.
        """
        self.line_edit.setEnabled(value)


class FFTWindow(QMainWindow):
    """
    Window to display the Fourier Transform of an image
    """
    close_fft = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__()
        self.parent: BaslerDSPIController = parent
        # Main widget to display image
        self.fft_widget = ImageDisplayWidget()
        self.setCentralWidget(self.fft_widget)
        # Closing Button
        """The button doesn't work yet (isn't displayed on the window)"""
        layout = QVBoxLayout()
        label = QLabel(translate('FFT'))
        layout.addWidget(label)
        self.open_button = QPushButton(translate("Stop FFT"))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.clicked.connect(self.handle_close_fft)
        layout.addWidget(self.open_button)
        #Bit depth
        bits_depth = int(self.parent.parent.variables.get('bits_depth', 8))
        self.fft_widget.set_bits_depth(bits_depth)
        #Initial Image
        self.initial_image = self.parent.parent.variables.get('image')
        if self.initial_image is not None:
            self.fft_widget.set_image_from_array(self.initial_image)

    def handle_close_fft(self):
        """
        Action performed when the closing button is triggered
        """
        self.close_fft.emit()