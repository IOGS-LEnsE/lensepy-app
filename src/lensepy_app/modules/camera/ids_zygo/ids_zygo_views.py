from PyQt6.QtWidgets import QLineEdit, QSlider, QGridLayout, QPushButton

from lensepy import translate
from lensepy.utils import is_integer
from lensepy_app.widgets import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy_app.modules.camera.ids_zygo.ids_zygo_controller import IDSZygoController

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
        self.parent: IDSZygoController = parent  # IDSZygoController or any CameraController
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

        layout.addStretch()
        self.setLayout(layout)
        self.update_infos()

    def set_enabled_roi_widget(self, value):
        """
        Activate ROI selection widget.
        :param value:   True to activate ROI selection widget.
        """
        self.roi_widget.set_enabled(value)

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
        self.camera: IDSZygoCamera = self.parent.get_variables()['camera']
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

