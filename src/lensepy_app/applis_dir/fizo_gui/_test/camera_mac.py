# %%
import sys

# pip install PyQt5
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from pypylon import pylon


class SettingsDialog(QDialog):
    """
    Classe pour les réglages des paramètre de la caméra
    """

    def __init__(self, camera_getter):
        super().__init__()
        self.camera = camera_getter.camera
        self.setWindowTitle("Camera Settings")

        # Create a QHBoxLayout instance
        self.layout = QGridLayout()

        # exposure time slider
        self.label_t, self.slider_t, self.input_t = self.generate_slider(
            f"T (µs)", 20, 10_000
        )
        self.slider_t.setTickInterval(20)
        self.slider_t.setSingleStep(20)
        self.add_slider(self.label_t, self.slider_t, self.input_t, 0)
        self.slider_t.setValue(100)

        # gain slider
        self.label_g, self.slider_g, self.input_g = self.generate_slider(
            f"Gain", 0, 100
        )
        self.slider_g.setValue(1)
        self.add_slider(self.label_g, self.slider_g, self.input_g, 1)

        # button_reset_scale = QPushButton("Reset scale")
        # button_reset_scale.clicked.connect()
        # self.layout.addWidget(button_reset_scale, 2, 1)
        # Set the layout of the SettingsDialog instance to the QHBoxLayout instance
        self.setLayout(self.layout)

    def generate_slider(self, name, min_value, max_value):
        label = QLabel(name)
        # Create a QSlider instance
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_value)  # Set the minimum value
        slider.setMaximum(max_value)  # Set the maximum value
        slider.setFixedWidth(400)

        # Create a QLineEdit instance
        input = QSpinBox()
        input.setFixedWidth(80)
        input.setMinimum(min_value)
        input.setMaximum(max_value)
        input.setSingleStep(5)

        slider.valueChanged.connect(lambda value, input=input: input.setValue(value))
        input.textChanged.connect(
            lambda text, slider=slider: self.slider_update(text, slider)
        )
        return label, slider, input

    def add_slider(self, label, slider, input, row):
        self.layout.addWidget(label, row, 0)
        self.layout.addWidget(slider, row, 1)
        self.layout.addWidget(input, row, 2)

    def slider_update(self, text, slider):
        try:
            slider.setValue(int(text))
            self.update_camera_setting()
        except:
            pass

    def update_camera_setting(self):
        self.camera.ExposureTime.Value = self.slider_t.value()
        self.camera.Gain.Value = self.slider_g.value()


class App(QWidget):
    w_default_image, h_default_image = 500, 500

    def __init__(self):
        super().__init__()
        self.title = "Basler Camera"
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        # Create a QVBoxLayout instance
        layout = QVBoxLayout()

        # Create a QLabel instance for the image
        self.label = QLabel(self)

        # Create a QPushButton instance for opening the settings dialog
        button = QPushButton("Open Settings", self)
        button.clicked.connect(self.open_settings_dialog)

        # Add the QLabel and QPushButton instances to the QVBoxLayout instance
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button)

        self.cam_feed = CameraGetter()
        self.cam_feed.start()
        self.cam_feed.ImageUpdate.connect(self.ImageUpdateSlot)

        # Set the layout of the App instance to the QVBoxLayout instance
        self.setLayout(layout)

    def open_settings_dialog(self):
        if not hasattr(self, "settings_dialog"):
            self.settings_dialog = SettingsDialog(self.cam_feed)

        self.settings_dialog.exec()

    def resizeEvent(self, event):
        w, h = self.width(), self.height()
        self.w_default_image, self.h_default_image = int(w * 0.75), int(h * 0.75)

    def ImageUpdateSlot(self, Image):
        pic = Image.scaled(
            self.w_default_image, self.h_default_image, Qt.AspectRatioMode.KeepAspectRatio
        )
        self.pixmap = QPixmap.fromImage(pic)
        self.label.setPixmap(self.pixmap)

    def CancelFeed(self):
        self.cam_feed.stop()


class CameraGetter(QThread):
    ImageUpdate = pyqtSignal(QImage)
    image_default_size = 500

    def run(self):
        self.ThreadActive = True

        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )

        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        converter = pylon.ImageFormatConverter()
        self.camera.AcquisitionFrameRateEnable.Value = True
        self.camera.AcquisitionFrameRate.Value = 30.0

        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        while self.ThreadActive and self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )
            image = converter.Convert(grabResult)
            arr = image.GetArray()
            ConvertToQtFormat = QImage(
                arr,
                arr.shape[1],
                arr.shape[0],
                QImage.Format.Format_BGR888,
            )
            pic = ConvertToQtFormat.scaled(
                self.image_default_size, self.image_default_size, Qt.AspectRatioMode.KeepAspectRatio
            )
            self.ImageUpdate.emit(pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.showMaximized()
    sys.exit(app.exec())
