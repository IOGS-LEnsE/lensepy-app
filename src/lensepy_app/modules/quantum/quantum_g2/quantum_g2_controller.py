__all__ = ["QuantumG2Controller"]

import time
import numpy as np
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

from lensepy_app.modules.drivers.coincidence_board.coincidence_board_model import NucleoWrapper
from lensepy_app.modules.quantum.quantum_g2 import G2OptionsView
from lensepy_app.modules.quantum.quantum_g2.quantum_g2_views import (
    QuantumG2DisplayWidget, TimeChartQuantumG2Widget)
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets import ImageDisplayWidget
from lensepy_app.widgets.widget_xy_chart import XYChartWidget


class QuantumG2Controller(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent    # main manager
        self.acquiring = False
        self.thread = None
        self.worker = None
        self.log_display = False
        self.data_time_a = np.zeros(30)
        self.data_time_b = np.zeros(30)
        self.data_time_c = np.zeros(30)
        self.data_time_ab = np.zeros(30)
        self.data_time_ac = np.zeros(30)
        self.data_time_abc = np.zeros(30)
        self.data_time_g2_2 = np.zeros(30)
        self.data_time_g2_3 = np.zeros(30)
        self.x_axis = np.arange(0,30)
        self.exposure_time = 0
        # Nucleo wrapper
        self.nucleo_wrapper = self.parent.variables['nucleo_wrapper']
        self.connected = False
        #self.connected = self.nucleo_wrapper.is_connected()

        # Graphical layout
        self.top_left = QuantumG2DisplayWidget()
        self.bot_left = TimeChartQuantumG2Widget()
        self.top_right = XYChartWidget()
        self.bot_right = G2OptionsView()
        # Setup widgets
        self.top_left.set_max_values(self.top_left.init_max_value())
        self.bot_left.set_range(0, self.top_left.init_max_value())
        self.bot_left.set_data(self.x_axis,
                               [self.data_time_a, self.data_time_b, self.data_time_c,
                                self.data_time_ab, self.data_time_ac, self.data_time_abc])
        self.exposure_time = float(self.top_left.time_value_label.get_selected_value())
        if self.connected:
            self.nucleo_wrapper.set_sampling_period(self.exposure_time * 1000)
            ## List of piezo
            self.boards_list = self.nucleo_wrapper.list_serial_hardware()
        else:
            self.boards_list = []

        self.top_right.set_background('white')

        # Signals
        self.top_left.max_val_changed.connect(self.handle_max_value_changed)
        self.top_left.time_changed.connect(self.handle_time_changed)
        self.bot_right.acq_started.connect(self.handle_acq_started)
        self.bot_right.mean_value_changed.connect(self.handle_mean_changed)

        # Init view

    def handle_mean_changed(self, value):
        print(value)

    def handle_acq_started(self):
        """Action performed when acquisition is required."""
        if self.acquiring:
            self.stop_acq()
            self.data_time_a = np.zeros(30)
            self.data_time_b = np.zeros(30)
            self.data_time_c = np.zeros(30)
            self.data_time_ab = np.zeros(30)
            self.data_time_ac = np.zeros(30)
            self.data_time_abc = np.zeros(30)
            self.data_time_g2_2 = np.zeros(30)
            self.data_time_g2_3 = np.zeros(30)
            # self.nucleo_wrapper.stop_acq()
            self.acquiring = False
            self.bot_right.set_acquisition(False)
            self.top_left.set_acquisition(False)
        else:
            self.acquiring = True
            self.top_left.set_acquisition()
            self.bot_right.set_acquisition()
            self.start_acq()

    def handle_max_value_changed(self, value):
        """Action performed when max value is changed."""
        self.top_left.set_max_values(value)
        self.bot_left.set_range(0, value)

    def handle_time_changed(self, value):
        """Action performed when integration time value is changed."""
        if self.connected:
            self.exposure_time = value
            self.nucleo_wrapper.set_sampling_period(self.exposure_time * 1000)

    def handle_data_ready(self, data):
        """Action performed when data are ready to display."""
        if data is not None:
            if len(data) == 6:
                # Display in gauge
                self.top_left.set_ab_ac_abc(int(data[3]), int(data[4]), int(data[5]))
                # Display data in XY chart
                self._shift_data_g2(data)
                self.bot_left.set_data(self.x_axis, [self.data_time_a, self.data_time_b, self.data_time_c,
                                                     self.data_time_ab, self.data_time_ac, self.data_time_abc])
                self.top_right.set_data(self.x_axis, [self.data_time_g2_2, self.data_time_g2_3,])

    def _shift_data_g2(self, data):
        """Left shift of data."""
        if len(data) == 6:
            self.data_time_a[:-1] = self.data_time_a[1:]
            self.data_time_a[-1] = data[0]
            self.data_time_b[:-1] = self.data_time_b[1:]
            self.data_time_b[-1] = data[1]
            self.data_time_c[:-1] = self.data_time_c[1:]
            self.data_time_c[-1] = data[2]
            self.data_time_ab[:-1] = self.data_time_ab[1:]
            self.data_time_ab[-1] = data[3]
            self.data_time_ac[:-1] = self.data_time_ac[1:]
            self.data_time_ac[-1] = data[4]
            self.data_time_abc[:-1] = self.data_time_abc[1:]
            self.data_time_abc[-1] = data[5]

            g2_3det = self.data_time_abc[-1] * self.data_time_a[-1] / (self.data_time_ab[-1] * self.data_time_ac[-1])
            g2_2det = self.data_time_ab[-1] * self.data_time_a[-1] / self.data_time_b[-1]

            self.data_time_g2_2[:-1] = self.data_time_g2_2[1:]
            self.data_time_g2_2[-1] = g2_2det
            self.data_time_g2_3[:-1] = self.data_time_g2_2[1:]
            self.data_time_g2_3[-1] = g2_3det

    def start_acq(self):
        """
        Start live acquisition from board.
        """
        if self.nucleo_wrapper is not None:
            # Read Period
            sampling_period = self.top_left.get_time_value() * 1000 # s to ms
            self.nucleo_wrapper.set_sampling_period(sampling_period)
            # Start worker
            self.thread = QThread()
            self.worker = SerialReader(self)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.data_ready.connect(self.handle_data_ready)
            self.worker.finished.connect(self.thread.quit)

            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def stop_acq(self):
        """
        Stop live mode, i.e. continuous image acquisition.
        """
        if self.worker is not None:
            # Arrêter le worker
            self.worker._running = False

            # Attendre la fin du thread
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()  # bloque jusqu'à la fin

            # Supprimer les références
            self.worker = None
            self.thread = None


class SerialReader(QObject):
    """
    Worker for image acquisition.
    Based on threads.
    """
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._running = False


    def run(self):
        nucleo = self.controller.nucleo_wrapper
        if nucleo is None:
            return

        self._running = True
        # Test if nucleo OK ? Send Init ?

        while self._running:
            # Collect data
            data = self.controller.nucleo_wrapper.get_data()
            # Display data
            if data is not None:
                self.data_ready.emit(data)

        self.finished.emit()

    def _print_data(self, data):
        """
        Print data.
        :param data:    Data to be printed.
        """
        for k, d in enumerate(data):
            print(f'{k}: {d}')

    def stop(self):
        self._running = False
