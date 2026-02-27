__all__ = ["PiezoDMDController"]

import time
from PyQt6.QtWidgets import QWidget
from lensepy.widgets import ImageDisplayWidget

from lensepy.modules.drivers.piezo_dmd.piezo_dmd_views import *
from lensepy.modules.drivers.piezo_dmd.piezo_dmd_model import DMDWrapper, PiezoWrapper
from lensepy.modules.camera.basler.basler_views import *
from lensepy.appli._app.template_controller import TemplateController


class PiezoDMDController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent    # main manager
        # DMD wrapper
        self.DMD_wrapper = DMDWrapper()
        self.parent.variables['dmd_wrapper'] = self.DMD_wrapper
        # Piezo-Nucleo wrapper
        self.piezo_wrapper = PiezoWrapper()
        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = CameraParamsWidget(self)
        self.top_right = DMDParamsView(self)
        self.bot_right = PiezoParamsWidget(self)
        # Setup widgets
        ## List of piezo
        self.boards_list = self.piezo_wrapper.list_serial_hardware()
        ## If piezo
        if len(self.boards_list) != 0:
            boards_list_display = self._boards_list_display(self.boards_list)
            self.bot_right.set_boards_list(boards_list_display)
        ## DMD
        dmd_connected = self.DMD_wrapper.init_dmd()
        print(f'DMD ? {dmd_connected}')

        ## Camera infos
        self.camera = self.parent.variables['camera']
        if self.camera is not None:
            expo_init = self.camera.get_parameter('ExposureTime')
            self.bot_left.set_exposure_time(expo_init)
            black_level = self.camera.get_parameter('BlackLevel')
            self.bot_left.set_black_level(black_level)
            fps_init = self.camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_left.label_fps.set_value(str(fps))
        '''
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)
        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.top_left.set_image_from_array(initial_image)
        '''
        # Signals
        #self.top_left.arduino_connected.connect(self.handle_arduino_connected)
        self.top_right.image_set.connect(self.handle_image_set)
        self.top_right.image_view.connect(self.handle_image_view)
        self.top_right.image_sent.connect(self.handle_image_sent)
        self.bot_right.board_connected.connect(self.handle_board_connected)

        # Init view
        self.top_right.no_image()

    def handle_board_connected(self, com):
        """Action performed when nucleo is connected."""
        comm_num = self.piezo_wrapper.com_list[com]['device']
        self.piezo_wrapper.set_serial_com(comm_num)
        connected = self.piezo_wrapper.connect()
        if connected:
            self.bot_right.set_connected()

    def handle_image_set(self, number):
        """Action performed when an image is set (opened)."""
        # Open
        config = self.parent.parent.config
        image_ok = False
        if 'img_dir' in config:
            if config['img_dir'] is not None:
                image_path = self._open_image(default_dir=config['img_dir'])
                if image_path is not None:
                    image_array, bits_depth = imread_rgb(image_path)
                    image_ok = True

        # Test if image OK then update view/send button
        if image_ok:
            self.top_right.set_enabled(number)
            self.top_right.set_image_opened(number)
            self.top_right.set_path_to_image(number, image_path)
            image = np.random.randint(0, 256, (300, 700), dtype=np.uint8)
            self.DMD_wrapper.set_image(image_array, int(number))

    def handle_image_view(self, number):
        """Action performed when an image has to be displayed."""
        image = self.DMD_wrapper.get_image(int(number))
        self.top_left.set_image_from_array(image)
        self.top_left.repaint()

    def handle_image_sent(self, number):
        """Action performed when an image has to be sent."""
        image = self.DMD_wrapper.get_image(int(number))
        # Sending...
        self.top_left.set_image_from_array(image)
        self.top_left.repaint()

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


    def _open_image(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, translate('dialog_open_image'),
                                                   default_dir, "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path != '':
            return file_path
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return None

