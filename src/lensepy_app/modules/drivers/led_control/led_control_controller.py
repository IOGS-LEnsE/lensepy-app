__all__ = ["LedControlController"]

import time

from PyQt6.QtWidgets import QWidget

from lensepy.modules.drivers.led_control.led_control_views import RGBLedControlWidget, MatrixWidget
from lensepy.modules.drivers.led_control.led_control_model import *
from lensepy.appli._app.template_controller import TemplateController


class LedControlController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        # LED wrapper
        self.wrapper = RGBLedWrapper()
        # Graphical layout
        self.top_left = RGBLedControlWidget(self)
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = MatrixWidget()
        # Setup widgets

        # Signals
        self.top_left.rgb_changed.connect(self.handle_rgb_changed)
        self.top_left.arduino_connected.connect(self.handle_arduino_connected)

    def handle_rgb_changed(self):
        """Action performed when RGB sliders changed."""
        r, g, b = self.top_left.get_rgb()
        w1, w2 = self.top_left.get_w12()
        ard_sending = f'{r} {g} {b} {w1} {w2}\n'
        self.wrapper.send_arduino(ard_sending)
        time.sleep(0.05)

    def handle_arduino_connected(self, com):
        """Action performed when arduino is connected."""
        self.wrapper.connect_arduino(com)



