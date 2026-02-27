__all__ = ["CoincidenceBoardController"]

import time
import numpy as np
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

from lensepy.modules.drivers.coincidence_board.coincidence_board_model import NucleoWrapper
from lensepy.modules.drivers.coincidence_board.coincidence_board_views import (
    CoincidenceDisplayWidget, NucleoParamsWidget, TimeChartCoincidenceWidget)
from lensepy.appli._app.template_controller import TemplateController


class CoincidenceBoardController(TemplateController):
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
        self.x_axis = np.arange(0,30)
        self.exposure_time = 0
        # Nucleo wrapper
        self.nucleo_wrapper = NucleoWrapper()
        self.connected = False
        self.parent.variables['nucleo_wrapper'] = self.nucleo_wrapper
        # Graphical layout
        self.top_left = CoincidenceDisplayWidget()
        self.bot_left = TimeChartCoincidenceWidget()
        self.top_right = QWidget()
        self.bot_right = NucleoParamsWidget()
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
        ## If piezo
        if len(self.boards_list) != 0:
            boards_list_display = self._boards_list_display(self.boards_list)
            self.bot_right.set_boards_list(boards_list_display)

        # Signals
        self.bot_right.board_connected.connect(self.handle_board_connected)
        self.bot_right.acq_started.connect(self.handle_acq_started)
        self.top_left.max_val_changed.connect(self.handle_max_value_changed)
        self.top_left.time_changed.connect(self.handle_time_changed)
        self.top_left.log_selected.connect(self.handle_log_selected)

        # Init view

    def handle_board_connected(self, com):
        """Action performed when nucleo is connected."""
        comm_num = self.nucleo_wrapper.com_list[com]['device']
        self.nucleo_wrapper.set_serial_com(comm_num)
        self.connected = self.nucleo_wrapper.connect()
        if self.connected:
            hw_version = self.nucleo_wrapper.get_hw_version()
            self.bot_right.set_connected(hw_version)

    def handle_acq_started(self):
        """Action performed when acquisition is required."""
        if self.acquiring:
            self.stop_acq()
            self.data_time_a = np.zeros(30)
            self.data_time_b = np.zeros(30)
            self.nucleo_wrapper.stop_acq()
            self.acquiring = False
            self.bot_right.set_acquisition(False)
        else:
            self.acquiring = True
            self.bot_right.set_acquisition()
            self.start_acq()

    def handle_max_value_changed(self, value):
        """Action performed when max value is changed."""
        self.top_left.set_max_values(value)
        self.bot_left.set_y_range(0, value)

    def handle_time_changed(self, value):
        """Action performed when integration time value is changed."""
        if self.connected:
            self.exposure_time = value
            self.nucleo_wrapper.set_sampling_period(self.exposure_time * 1000)

    def handle_log_selected(self, value):
        """Action performed when log checkbox is selected."""
        self.log_display = value
        print(f'Log checkbox selected to {value}')

    def _boards_list_display(self, boards_list):
        """
        Prepare the board list for displaying in combobox.
        :boards_list: list of boards list (device, manufacturer, description)
        """
        list_disp = []
        if len(boards_list) != 0:
            for board in boards_list:
                text_disp = f'{board["device"]} | {board["manufacturer"]}'
                list_disp.append(text_disp)
        return list_disp

    def handle_data_ready(self, data):
        """Action performed when data are ready to display."""
        if data is not None:
            if len(data) == 6:
                # Display in gauge
                if not self.log_display:
                    self.top_left.set_a_b_c(int(data[0]), int(data[1]), int(data[2]))
                    self.top_left.set_ab_ac_abc(int(data[3]), int(data[4]), int(data[5]))
                else:
                    # NOT WORKING !
                    a_val = int(np.ceil(np.log(int(data[0])))) if int(data[0]) > 0 else 0
                    b_val = int(np.ceil(np.log(int(data[1])))) if int(data[1]) > 0 else 0
                    c_val = int(np.ceil(np.log(int(data[2])))) if int(data[2]) > 0 else 0
                    self.top_left.set_a_b_c(a_val, b_val, c_val)

                # Display data in XY chart
                self._shift_data(data)
                self.bot_left.set_data(self.x_axis, [self.data_time_a, self.data_time_b, self.data_time_c,
                                                     self.data_time_ab, self.data_time_ac, self.data_time_abc])

    def _shift_data(self, data):
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

    def start_acq(self):
        """
        Start live acquisition from board.
        """
        if self.nucleo_wrapper is not None:
            # Read Period
            sampling_period = 400
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
