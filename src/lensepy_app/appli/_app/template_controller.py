import time
from pathlib import Path
import numpy as np
from PyQt6 import sip
from PyQt6.QtCore import pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog, QApplication


class TemplateController(QObject):
    """

    """

    controller_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent   # MainManager
        self.top_left = QWidget()
        self.top_right = QWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.bot_zernike = QWidget()
        self.destroyed.connect(self.on_destroy)

    def init_view(self):
        self.parent.main_window.top_left_container.deleteLater()
        self.parent.main_window.top_right_container.deleteLater()
        self.parent.main_window.bot_left_container.deleteLater()
        self.parent.main_window.bot_right_container.deleteLater()
        self.parent.main_window.bot_zernike_container.deleteLater()
        # Update new containers
        self.parent.main_window.top_left_container = self.top_left
        self.parent.main_window.bot_left_container = self.bot_left
        self.parent.main_window.top_right_container = self.top_right
        self.parent.main_window.bot_right_container = self.bot_right
        self.parent.main_window.bot_zernike_container = self.bot_zernike
        self.update_view()

    def update_view(self):
        # Display mode value in XML
        mode = self.parent.xml_module.get_parameter_xml('display')
        if mode == 'MODE2':
            self.parent.main_window.set_mode2()
        elif mode == 'MODE1':
            self.parent.main_window.set_mode1()
        elif mode == 'ZERNIKE':
            self.parent.main_window.set_mode_zernike()
        else:
            self.parent.main_window.set_mode3()
        # Update display mode
        self.parent.main_window.update_containers()

    def update(self):
        self.parent.main_window.repaint()
        QApplication.processEvents()

    def _replace_top_left_widget(self, new_widget):
        self.top_left = new_widget
        self.parent.main_window.top_left_container.deleteLater()
        self.parent.main_window.top_left_container = self.top_left
        self.update_view()

    def _replace_bot_left_widget(self, new_widget):
        self.bot_left = new_widget
        self.parent.main_window.bot_left_container = self.bot_left
        self.update_view()

    def _replace_top_right_widget(self, new_widget):
        self.top_right = new_widget
        self.parent.main_window.top_right_container = self.top_right
        self.update_view()

    def _replace_bot_right_widget(self, new_widget):
        self.bot_right = new_widget
        self.parent.main_window.bot_right_container = self.bot_right
        self.update_view()

    def _replace_zernike_widget(self, new_widget):
        self.bot_zernike = new_widget
        self.parent.main_window.bot_zernike_container = self.bot_zernike
        self.update_view()

    def handle_controller(self, event):
        """
        Action performed when the controller changed.
        :param event:
        """
        self.controller_changed.emit(event)

    def get_variables(self, index=''):
        """
        Get variables dictionary from the main manager.
        :return:
        """
        if index == '':
            return self.parent.get_variables()
        else:
            return self.parent.get_variable(index)

    def is_variable(self, var_name):
        """
        Check if variable name exists.
        """
        return var_name in self.parent.variables

    def set_variables(self, var_name, value):
        """Update a variable in the variables' dictionary.
        :param var_name:    Key of the variable.
        :param value:       Value of the variable.
        """
        self.parent.variables[var_name] = value

    def get_config(self, name=''):
        """Return the config dictionary from the main manager."""
        return self.parent.get_config(name)

    def get_initial_params(self, name=''):
        """Return the initial value of the parameters from
        the main manager init_params dictionary."""
        return self.parent.get_initial_params(name)

    def _get_image_dir(self, filepath):
        if filepath is None:
            return ''
        else:
            # Detect if % in filepath
            if '%USER' in filepath:
                new_filepath = filepath.split('%')
                new_filepath = f'{Path.home()}/{new_filepath[2]}'
                return new_filepath
            else:
                return filepath

    def _get_file_path(self, default_dir: str = '') -> bool:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        file_path, _ = QFileDialog.getSaveFileName(
            self.bot_right,
            translate('dialog_save_histoe'),
            default_dir,
            "Images (*.png)"
        )

        if file_path != '':
            return file_path
        else:
            dlg = QMessageBox(self.bot_right)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return ''

    def on_destroy(self):
        """Action performed when the object is destroyed"""
        self.cleanup()

    def cleanup(self):
        pass

    def worker_calculation_error(self, exception):
        """Errors management."""
        print("ERRORS :", exception)
        self.thread = None
        self.worker = None


class ImageLive(QObject):
    """
    Worker for image acquisition.
    Based on threads.
    """
    image_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._running = False

    def run(self):
        camera = self.controller.parent.variables.get("camera")
        if camera is None:
            return

        self._running = True
        camera.camera_acquiring = True

        while self._running:
            image = camera.get_image()
            if image is not None and not sip.isdeleted(self):
                self.image_ready.emit(image)
            time.sleep(0.01)

        camera.camera_acquiring = False
        self.finished.emit()

    '''
    def run(self):
        camera = self.controller.parent.variables.get("camera")
        if camera is None:
            return

        self._running = True
        camera.open()
        camera.camera_acquiring = True

        while self._running:
            if not camera.is_open:
                QThread.msleep(1)
                continue
            image = camera.get_image()
            if image is not None and not sip.isdeleted(self):
                self.image_ready.emit(image)
            QThread.msleep(1)

        camera.camera_acquiring = False
        if camera.is_open:
            camera.close()
        self.finished.emit()
    '''

    def stop(self):
        self._running = False


class Worker(QObject):
    """
    Base for a process running in a thread.
    Process has to be implemented in the run() method.
    """

    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def run(self):
        """
        Method called in the worker thread.
        Must be surcharged.
        """
        raise NotImplementedError

    def emit_progress(self, step: int):
        """Emit a signal to the worker thread after a new step."""
        self.progress.emit(step)
