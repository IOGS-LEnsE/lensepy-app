import sys, time
from lensepy import translate
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QGuiApplication
from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QComboBox, QRadioButton,
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QLabel, QFormLayout, QGroupBox, QProgressBar
)
from lensepy_app.pyqt6.widget_xy_chart import XYChartWidget
from lensepy.utils import *
from lensepy_app.widgets import *

BLUE_LITE = '#4FC3F7'
GREEN_LITE = '#2ED8A7'

class QuantumG2DisplayWidget(QWidget):
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
        self.max_value = 1
        # Screen size
        screen_resolution = QGuiApplication.primaryScreen().geometry()
        ## AB counter
        self.ab_value = VerticalGauge(title='AB', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.ab_value)
        #self.ab_value.setMinimumHeight(screen_resolution.height()//3)
        self.ab_value.set_colors(BLUE_IOGS, ORANGE_IOGS)
        ## AC counter
        self.ac_value = VerticalGauge(title='AC', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.ac_value)
        self.ac_value.set_colors(BLUE_IOGS, BLUE_LITE)
        abc_layout.addWidget(make_vline())
        ## ABC counter
        self.abc_value = VerticalGauge(title='ABC', min_value=0, max_value=self.max_value)
        abc_layout.addWidget(self.abc_value)
        self.abc_value.set_colors(BLUE_IOGS, GREEN_LITE)
        layout.addWidget(abc_widget)
        # Charts range choice
        disp_widget = QWidget()
        disp_layout = QHBoxLayout()
        disp_widget.setLayout(disp_layout)
        self.max_values = ['100', '1k', '10k', '100k']
        self.max_values_int = [100, 1000, 10000, 100000]
        self.max_value_label = SelectWidget(translate('coincidence_max_value'), values=self.max_values)
        disp_layout.addWidget(self.max_value_label)

        layout.addWidget(make_hline())
        layout.addWidget(disp_widget)

        # Exposure time choice
        self.time_values = ['0.5', '1.0', '2.0', '5.0', '10.0', '20.0']
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

    def set_ab_ac_abc(self, ab_cnt, ac_cnt, abc_cnt=0):
        """Update A B C gauges."""
        self.ab_value.set_value(int(ab_cnt))
        self.ac_value.set_value(int(ac_cnt))
        self.abc_value.set_value(int(abc_cnt))
        self.repaint()

    def set_max_values(self, value=100000):
        """Set maximum value of the gauges."""
        self.max_value = value
        self.ab_value.set_min_max_values(0, self.max_value//10)
        self.ac_value.set_min_max_values(0, self.max_value//10)
        self.abc_value.set_min_max_values(0, self.max_value//100)

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

    def set_acquisition(self, value=True):
        """Set acquisition mode."""
        self.time_value_label.set_enabled(not value)

    def get_time_value(self):
        """Return current time value."""
        return float(self.time_values[self.time_value_label.get_selected_index()])


class TimeChartQuantumG2Widget(QWidget):
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
        self.chart_a_b_c.set_colors([ORANGE_IOGS, BLUE_LITE, GREEN_LITE])
        self.chart_ab_ac_abc.set_colors([ORANGE_IOGS, BLUE_LITE, GREEN_LITE])

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
            self.chart_a_b_c.set_data(x_axis, data[0:3], y_label=translate('coinc_numbers'))
            self.chart_ab_ac_abc.set_data(x_axis, data[3:6], y_label=translate('coinc_numbers'))
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

