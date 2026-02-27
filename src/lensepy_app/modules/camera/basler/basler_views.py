from PyQt6.QtWidgets import QLineEdit, QSlider, QGridLayout, QPushButton

from lensepy import translate
from lensepy.utils import is_integer
from lensepy.utils.pyqt6 import make_hline
from lensepy.widgets import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.modules.basler.basler_controller import BaslerController

class CameraInfosWidget(QWidget):
    """
    Widget to display image infos.
    """
    color_mode_changed = pyqtSignal(str)
    roi_changed = pyqtSignal(list)
    roi_centered = pyqtSignal(list)
    roi_reset = pyqtSignal()
    roi_activated = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(None)
        # Attributes
        self.parent: BaslerController = parent  # BaslerController or any CameraController
        self.roi_activated_state = self.parent.parent.variables["roi_activated"]
        self.camera = self.parent.get_variables()['camera']
        # Graphical objects
        layout = QVBoxLayout()

        label = QLabel(translate('basler_infos_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        self.label_name = LabelWidget(translate('basler_infos_name'), '')
        layout.addWidget(self.label_name)
        self.label_serial = LabelWidget(translate('basler_infos_serial'), '')
        layout.addWidget(self.label_serial)
        layout.addWidget(make_hline())

        self.label_size = LabelWidget(translate('basler_infos_size'), '', 'pixels')
        layout.addWidget(self.label_size)
        self.color_choice = self.parent.colormode
        self.label_color_mode = SelectWidget(translate('basler_infos_color_mode'), self.color_choice)
        self.label_color_mode.choice_selected.connect(self.handle_color_mode_changed)
        layout.addWidget(self.label_color_mode)
        layout.addWidget(make_hline())

        self.roi_widget = CameraROIWidget(self.parent)
        self.roi_widget.roi_checked.connect(self.handle_roi_checked)
        self.roi_widget.roi_centered.connect(lambda coords: self.roi_centered.emit(coords))
        self.roi_widget.roi_reset.connect(lambda: self.roi_reset.emit())
        self.roi_widget.roi_changed.connect(lambda coords: self.roi_changed.emit(coords))
        layout.addWidget(self.roi_widget)

        self.activate_roi_button = QPushButton(translate('activate_roi_button'))
        self.activate_roi_button.setFixedHeight(BUTTON_HEIGHT)
        if self.roi_activated_state:
            self.activate_roi_button.setStyleSheet(actived_button)
        else:
            self.activate_roi_button.setStyleSheet(unactived_button)
        self.activate_roi_button.clicked.connect(self.handle_roi_activated)
        layout.addWidget(self.activate_roi_button)

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
        self.roi_activated_state = not self.roi_activated_state
        if self.roi_activated_state:
            self.activate_roi_button.setStyleSheet(actived_button)
        else:
            self.activate_roi_button.setStyleSheet(unactived_button)
        self.roi_activated.emit(self.roi_activated_state)

    def update_infos(self):
        """
        Update information from camera.
        """
        self.camera: BaslerCamera = self.parent.get_variables()['camera']
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


class CameraROIWidget(QWidget):
    """
    Widget to select ROI of an image.
    """
    roi_checked = pyqtSignal(bool)
    roi_changed = pyqtSignal(list)
    roi_centered = pyqtSignal(list)
    roi_reset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent: BaslerController = parent
        # Attributes
        self.coords = [0, 0, 0, 0]   # x0, y0, x1, y1
        # Graphical objects
        layout = QVBoxLayout()
        self.setLayout(layout)
        label = QLabel(translate('camera_roi_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        # X0, Y0, X1, Y1, W, H widget
        self.roi_select = ROISelectWidget()
        self.roi_select.roi_changed.connect(self.handle_roi_changed)
        layout.addWidget(self.roi_select)
        if self.parent.parent.variables["roi_coords"] is not None:
            self.roi_select.set_values(self.parent.parent.variables["roi_coords"])
        else:
            self.roi_select.set_values([0, 0, 0, 0])
        self.center_roi_button = QPushButton(translate('roi_center_button'))
        self.center_roi_button.setStyleSheet(unactived_button)
        self.center_roi_button.setFixedHeight(BUTTON_HEIGHT)
        self.center_roi_button.clicked.connect(self.handle_roi_centered)
        layout.addWidget(self.center_roi_button)
        self.reset_roi_button = QPushButton(translate('roi_reset_button'))
        self.reset_roi_button.setStyleSheet(unactived_button)
        self.reset_roi_button.setFixedHeight(BUTTON_HEIGHT)
        self.reset_roi_button.clicked.connect(self.handle_roi_reset)
        layout.addWidget(self.reset_roi_button)

    def handle_roi_centered(self):
        """Recalculate ROI position to centering it."""
        coords = self.roi_select.get_values()
        self.roi_centered.emit(coords)

    def handle_roi_reset(self):
        """Reset ROI to the maximum range of the camera."""
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
        button_status = disabled_button if not value else unactived_button
        self.center_roi_button.setStyleSheet(button_status)
        self.reset_roi_button.setStyleSheet(button_status)


class ROISelectWidget(QWidget):
    roi_changed = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(None)
        layout = QGridLayout()
        self.setLayout(layout)
        self.x0_label = LineEditWidget(translate('roi_x0'), value='')
        self.x0_label.setStyleSheet(styleH2)
        self.y0_label = LineEditWidget(translate('roi_y0'), value='')
        self.y0_label.setStyleSheet(styleH2)
        self.x1_label = LineEditWidget(translate('roi_x1'), value='')
        self.x1_label.setStyleSheet(styleH2)
        self.y1_label = LineEditWidget(translate('roi_y1'), value='')
        self.y1_label.setStyleSheet(styleH2)
        # Width and Height
        self.w_label = LineEditWidget(translate('roi_w'), value='')
        self.w_label.setStyleSheet(styleH2)
        self.h_label = LineEditWidget(translate('roi_h'), value='')
        self.h_label.setStyleSheet(styleH2)
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
        """Get ROI coordinates."""
        return self.coords

    def update_values(self):
        """Update graphical objects with new values."""
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


class LineEditWidget(QWidget):
    """
    Widget for line edit, including a title.
    """
    edit_changed = pyqtSignal(str)
    def __init__(self, title:str='', value='', parent=None):
        super().__init__(None)
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

