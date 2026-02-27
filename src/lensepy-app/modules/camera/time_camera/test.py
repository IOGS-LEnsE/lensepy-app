import cv2
from PyQt6.QtWidgets import QApplication, QGridLayout, QMainWindow, QHBoxLayout
from lensepy.modules.time_camera.time_camera_controller import TimeCameraController
from lensepy.modules.basler.basler_models import BaslerCamera

if __name__ == '__main__':
    from lensepy.appli._app.app_utils import *
    from lensepy.appli._app.main_view import MainWindow

class MainManager:
    """
    Main widget/application manager.
    """
    def __init__(self, parent=None):
        self.parent: My_Application = parent    # Parent application
        self.controller = None
        # Variables initialization
        self.variables = {}
        self.variables['image'] = None
        self.variables['camera'] = BaslerCamera()
        find_cam = self.variables['camera'].find_first_camera()
        print(f'Find Cam ? {find_cam}')
        if find_cam:
            self.variables['camera'].set_parameter('ExposureTime', 1000)
            self.variables['camera'].set_parameter('PixelFormat', 'Mono12')
            self.variables['bits_depth'] = 12
            # Initialization
            self.xml_app: XMLFileConfig = XMLFileConfig('./test.xml')
            self.xml_module: XMLFileModule = XMLFileModule('./basler.xml')
            self.parent: My_Application = parent    # Parent application
            self.main_window: MainWindow = MainWindow(self)     # Main window management
            self.controller = TimeCameraController(self)

            # For test only
            self.main_window.menu_container.setStyleSheet("background-color:rgb(100,100,100);")
        else:
            return

    def init_controller(self):
        self.controller.init_view()


class My_Application(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.config = {'img_dir': '%USERPROFILE%\\Documents'}
        self.manager = MainManager(self)
        self.window = QMainWindow()
        if self.manager.controller is not None:
            self.manager.init_controller()
            self.window = self.manager.main_window
        else:
            return

    def show(self):
        # Display Main Window
        self.window.setWindowTitle(f'Test')
        self.window.showMaximized()


def main():
    app = My_Application(sys.argv)
    app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()