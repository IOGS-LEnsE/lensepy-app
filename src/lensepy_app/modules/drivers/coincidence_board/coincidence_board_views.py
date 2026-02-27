import sys, time
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QGuiApplication
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton,
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QLabel, QFormLayout, QGroupBox, QProgressBar
)
from lensepy.pyqt6.widget_xy_chart import XYChartWidget

from lensepy import translate
from lensepy.utils import *
from lensepy.widgets import *

class NucleoParamsWidget(QWidget):

    board_connected = pyqtSignal(int)
    acq_started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent
        self.boards_list = None

        # Graphical objects
        layout = QVBoxLayout()

        layout.addWidget(make_hline())
        label = QLabel(translate('nucleo_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())
        self.boards_list_box = QComboBox()
        layout.addWidget(self.boards_list_box)
        self.board_connect_button = QPushButton(translate('nucleo_connect'))
        self.board_connect_button.setStyleSheet(disabled_button)
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        layout.addWidget(self.board_connect_button)
        self.board_connect_button.clicked.connect(self.handle_nucleo_connected)
        layout.addWidget(make_hline())
        self.acq_start_button = QPushButton(translate('nucleo_start_acq'))
        self.acq_start_button.setStyleSheet(disabled_button)
        self.acq_start_button.setEnabled(False)
        self.acq_start_button.setFixedHeight(BUTTON_HEIGHT)
        layout.addWidget(self.acq_start_button)
        layout.addWidget(make_hline())

        layout.addStretch()
        self.setLayout(layout)

        # Signal
        self.acq_start_button.clicked.connect(self.handle_acq_started)

    def handle_nucleo_connected(self):
        """Action performed when the piezo button is clicked."""
        board_number = self.boards_list_box.currentIndex()
        self.board_connected.emit(board_number)

    def handle_acq_started(self):
        """Action performed when the start acquisition button is clicked."""
        self.acq_started.emit()

    def set_boards_list(self, board_list):
        """Set the list of the serial port connected."""
        self.boards_list = board_list
        if len(board_list) != 0:
            self.boards_list_box.addItems(self.boards_list)
            self.board_connect_button.setStyleSheet(unactived_button)
            self.board_connect_button.setEnabled(True)
        self.update()

    def set_connected(self, version):
        """If a board is connected, disable connexion button.
        :param version:     Version of the hardware.
        """
        self.board_connect_button.setEnabled(False)
        self.board_connect_button.setStyleSheet(actived_button)
        self.board_connect_button.setText(f'{translate("nucleo_connected")} / V.{version}')
        self.boards_list_box.setEnabled(False)
        self.acq_start_button.setStyleSheet(unactived_button)
        self.acq_start_button.setEnabled(True)

    def set_acquisition(self, value = True):
        """Set acquisition mode."""
        if value:
            self.acq_start_button.setStyleSheet(actived_button)
            self.acq_start_button.setText(translate('stop_acq_button'))
        else:
            self.acq_start_button.setStyleSheet(unactived_button)
            self.acq_start_button.setText(translate('start_acq_button'))

class CoincidenceDisplayWidget(QWidget):
    """
    Widget to display image opening options.
    """

    rgb_changed = pyqtSignal()
    nucleo_connected = pyqtSignal(str)
    log_selected = pyqtSignal(bool)
    max_val_changed = pyqtSignal(int)
    time_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()
        # Graphical Elements
        layout.addWidget(make_hline())
        label = QLabel(translate('coincidence_params_title'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(make_hline())

        label_abc = QLabel(translate('A_B_C_values'))
        label_abc.setStyleSheet(styleH3)
        label_abc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_abc)
        layout.addWidget(make_hline())

        # Sliders for ABC
        abc_widget = QWidget()
        abc_layout = QHBoxLayout()
        abc_widget.setLayout(abc_layout)
        self.max_value = 100000
        # Screen size
        screen_resolution = QGuiApplication.primaryScreen().geometry()
        print(screen_resolution.width(), screen_resolution.height())
        ## A counter
        self.a_value = VerticalGauge(title='A', min_value=0, max_value=self.max_value)
        self.a_value.setMinimumHeight(screen_resolution.height()//3)
        abc_layout.addWidget(self.a_value)
        ## B counter
        self.b_value = VerticalGauge(title='B', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.b_value)
        ## C counter
        self.c_value = VerticalGauge(title='C', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.c_value)
        abc_layout.addWidget(make_vline())
        ## AB counter
        self.ab_value = VerticalGauge(title='AB', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.ab_value)
        ## AC counter
        self.ac_value = VerticalGauge(title='AC', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.ac_value)
        abc_layout.addWidget(make_vline())
        ## ABC counter
        self.abc_value = VerticalGauge(title='ABC', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.abc_value)
        layout.addWidget(abc_widget)
        # Charts range choice
        disp_widget = QWidget()
        disp_layout = QHBoxLayout()
        disp_widget.setLayout(disp_layout)
        self.max_values = ['100k', '10k', '1k', '100']
        self.max_values_int = [100000, 10000, 1000, 100]
        self.max_value_label = SelectWidget(translate('coincidence_max_value'), values=self.max_values)
        disp_layout.addWidget(self.max_value_label)
        self.log_display = QCheckBox(translate('log_display'))
        disp_layout.addWidget(self.log_display)

        layout.addWidget(make_hline())
        layout.addWidget(disp_widget)

        # Exposure time choice
        disp_widget = QWidget()
        disp_layout = QHBoxLayout()
        disp_widget.setLayout(disp_layout)
        self.time_values = ['0.1', '0.2', '0.5', '1.0', '2.0']
        self.time_value_label = SelectWidget(translate('coincidence_exposure_time'), values=self.time_values)
        disp_layout.addWidget(self.time_value_label)

        layout.addWidget(make_hline())
        layout.addWidget(disp_widget)
        layout.addWidget(make_hline())
        layout.addStretch()
        self.setLayout(layout)

        # Signals
        self.max_value_label.choice_selected.connect(self.handle_max_value_changed)
        self.time_value_label.choice_selected.connect(self.handle_time_changed)
        self.log_display.stateChanged.connect(self.handle_log_disp_changed)

    def set_a_b_c(self, a_cnt, b_cnt, c_cnt=0):
        """Update A B C gauges."""
        self.a_value.set_value(int(a_cnt))
        self.b_value.set_value(int(b_cnt))
        self.c_value.set_value(int(c_cnt))
        self.repaint()

    def set_ab_ac_abc(self, ab_cnt, ac_cnt, abc_cnt=0):
        """Update A B C gauges."""
        self.ab_value.set_value(int(ab_cnt))
        self.ac_value.set_value(int(ac_cnt))
        self.abc_value.set_value(int(abc_cnt))
        self.repaint()

    def set_max_values(self, value=100000):
        """Set maximum value of the gauges."""
        self.max_value = value
        self.a_value.set_min_max_values(0, self.max_value)
        self.b_value.set_min_max_values(0, self.max_value)
        self.c_value.set_min_max_values(0, self.max_value)
        self.ab_value.set_min_max_values(0, self.max_value)
        self.ac_value.set_min_max_values(0, self.max_value)
        self.abc_value.set_min_max_values(0, self.max_value)

    def init_max_value(self):
        """Return maximum value of the gauges."""
        return self.max_values_int[int(self.max_value_label.get_selected_index())]

    def handle_max_value_changed(self, value):
        """Action performed when max_value choice is changed."""
        choice = self.max_value_label.get_selected_index()
        self.max_val_changed.emit(self.max_values_int[choice])

    def handle_time_changed(self, value):
        """Action performed when integration time choice is changed."""
        choice = self.time_value_label.get_selected_index()
        self.time_changed.emit(float(self.time_values[choice]))

    def handle_log_disp_changed(self):
        """Action performed when log checkbox is changed."""
        log = self.log_display.isChecked()
        self.log_selected.emit(log)


class TimeChartCoincidenceWidget(QWidget):
    """
    Display 2 charts - 1 for A,B,C and 1 for AB, AC, ABC
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.chart_a_b_c = XYChartWidget()
        self.chart_ab_ac_abc = XYChartWidget()
        layout.addWidget(self.chart_a_b_c, 1)
        layout.addWidget(self.chart_ab_ac_abc, 1)

        # Setup charts
        self.chart_a_b_c.set_background('white')
        self.chart_a_b_c.set_title(translate('a_b_c_time_chart_title'))
        self.chart_ab_ac_abc.set_background('white')
        self.chart_ab_ac_abc.set_title(translate('ab_ac_abc_time_chart_title'))
        self.setLayout(layout)

    def set_range(self, min_val, max_val):
        """Set min and max value range of the charts."""
        self.chart_a_b_c.set_y_range(min_val, max_val)
        self.chart_ab_ac_abc.set_y_range(min_val, max_val)

    def set_data(self, x_axis, data):
        """Update charts data."""
        if len(data) == 6:
            self.chart_a_b_c.set_data(x_axis, data[0:2])
            self.chart_ab_ac_abc.set_data(x_axis, data[3:5])
            self.chart_a_b_c.refresh_chart()
            self.chart_ab_ac_abc.refresh_chart()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CoincidenceDisplayWidget()
    #w = VerticalGauge(title='Test', min_value=0, max_value=100)
    #w.set_value(76)
    w.resize(400, 400)
    w.show()
    sys.exit(app.exec())

