import os
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from matplotlib import pyplot as plt

from lensepy import translate
from lensepy.css import *
from lensepy.widgets import HistoStatsWidget
from lensepy.appli._app.template_controller import TemplateController, ImageLive
from lensepy.widgets import XYMultiChartWidget, ImageDisplayWithPoints
from lensepy.modules.camera.time_camera.time_camera_views import TimeOptionsWidget, MultiHistoWidget
from lensepy.utils import make_hline, process_hist_from_array, save_hist, rgb255_to_float

NUMBER_OF_POINTS = 4
DISPLAY_NB_OF_PTS = 50

class TimeCameraController(TemplateController):
    """Controller for camera acquisition."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.thread = None
        self.worker = None

        # Data for time chart
        self.acquiring = False
        self.max_acquisition = 0
        self.nb_of_images = 0
        self.x_y_coords = []
        self.x_time = None
        self.point1_data = None
        self.point2_data = None
        self.point3_data = None
        self.point4_data = None

        # Widgets
        self.top_left = ImageDisplayWithPoints()
        self.bot_left = MultiHistoWidget()
        self.bot_right = TimeOptionsWidget()
        self.top_right = XYMultiChartWidget(multi_chart=False, allow_point_selection=False)
        self.bot_left.set_background('white')
        # Bits depth
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)

        # Initial Image
        initial_image = self.parent.variables.get('image')
        if initial_image is not None:
            self.top_left.set_image_from_array(initial_image)
            if initial_image.ndim == 2:
                self.bot_right.set_start_enabled()
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.set_exposure_time(expo_init)
            black_level = camera.get_parameter('BlackLevel')
            self.bot_right.set_black_level(black_level)
            fps_init = camera.get_parameter('BslResultingAcquisitionFrameRate')
            fps = np.round(fps_init, 2)
            self.bot_right.set_frame_rate(fps)
            self.top_right.set_title(translate('image_time_xy_title'))
        # Signals
        self.bot_right.acquisition_started.connect(self.start_acquisition)
        self.bot_right.save_data.connect(self.handle_save_data)
        # Start live acquisition
        self.start_live()

    def start_live(self):
        """Start live acquisition with camera."""
        self.thread = QThread()
        self.worker = ImageLive(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.handle_image_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def stop_live(self):
        """Stop live acquisition."""
        if self.worker:
            self.worker.stop()
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self.worker = None
            self.thread = None

    def start_acq_live(self):
        """Start live acquisition with camera."""
        self.thread = QThread()
        self.worker = ImageLive(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.handle_image_acq_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def start_acquisition(self, value: int):
        """Start acquisition of gray values for 4 random points."""
        if not self.acquiring:
            self.stop_live()
            self.acquiring = True
            self.nb_of_images = 0
            self.max_acquisition = value
            if self.parent.variables['time_points'] is None:
                # Get AOI size !!
                if self.parent.variables['roi_coords'] is not None:
                    x0, y0, x1, y1 = self.parent.variables['roi_coords']
                    min_x, min_y = 0, 0
                    max_x, max_y = x1-x0, y1-y0
                else:
                    min_x, min_y, max_x, max_y = 0, 0, 10, 10
                self.x_y_coords = self._random_points(min_x, max_x, min_y, max_y)
                self.parent.variables['time_points'] = self.x_y_coords.copy()
            else:
                self.x_y_coords = self.parent.variables['time_points']
            self.top_left.set_points(self.x_y_coords)
            # Initialize data
            self.x_time = np.linspace(0, self.max_acquisition-1, self.max_acquisition)
            self.point1_data = np.empty(self.max_acquisition)
            self.point2_data = np.empty(self.max_acquisition)
            self.point3_data = np.empty(self.max_acquisition)
            self.point4_data = np.empty(self.max_acquisition)
            self.start_acq_live()
        else:
            self.acquiring = False
            self.stop_live()
            self.bot_right.stop_acquisition()
            # Display statistics


    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        self.top_left.set_image_from_array(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_image_acq_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        if self.nb_of_images < self.max_acquisition:
            self.top_left.set_image_from_array(image)
            # Store new image.
            self.parent.variables['image'] = image.copy()
            self.nb_of_images += 1
            # Collect new points
            (y1, x1) = (self.x_y_coords[0][0], self.x_y_coords[0][1])
            self.point1_data[self.nb_of_images-1] = image[x1,y1]
            (y2, x2) = (self.x_y_coords[1][0], self.x_y_coords[1][1])
            self.point2_data[self.nb_of_images-1] = image[x2,y2]
            (y3, x3) = (self.x_y_coords[2][0], self.x_y_coords[2][1])
            self.point3_data[self.nb_of_images-1] = image[x3,y3]
            (y4, x4) = (self.x_y_coords[3][0], self.x_y_coords[3][1])
            self.point4_data[self.nb_of_images-1] = image[x4,y4]
            # Update time chart
            y_data = [self.point1_data[:self.nb_of_images],
                      self.point2_data[:self.nb_of_images],
                      self.point3_data[:self.nb_of_images],
                      self.point4_data[:self.nb_of_images]]
            y_names = [f'point1 ({x1},{y1})', f'point2 ({x2},{y2})',
                       f'point3 ({x3},{y3})', f'point4 ({x4},{y4})']
            self.top_right.set_data(self.x_time[:self.nb_of_images],y_data,
                                    x_label='Time', y_names=y_names)
            self.top_right.refresh_chart(last=DISPLAY_NB_OF_PTS)
            # Update histogram / Acq
            self.update_histogram(image)
        else:    # End of acquisition
            self.stop_live()
            self.acquiring = False
            self.bot_right.stop_acquisition()
            m1, s1, m2, s2, m3, s3, m4, s4 = self._process_stats()
            self.bot_right.set_stats(m1, s1, m2, s2, m3, s3, m4, s4)

    # Save data
    def handle_save_data(self, option):
        """Action performed when saving data button is pressed."""
        self.stop_live()
        datasets = [self.point1_data, self.point2_data,
                    self.point3_data, self.point4_data]
        (y1, x1) = (self.x_y_coords[0][0], self.x_y_coords[0][1])
        (y2, x2) = (self.x_y_coords[1][0], self.x_y_coords[1][1])
        (y3, x3) = (self.x_y_coords[2][0], self.x_y_coords[2][1])
        (y4, x4) = (self.x_y_coords[3][0], self.x_y_coords[3][1])
        m1, s1, m2, s2, m3, s3, m4, s4 = self._process_stats()
        titles = [f"P1 ({y1} / {x1}) - M={m1:.2f} / StD={s1:.2f}",
                  f"P2 ({y2} / {x2}) - M={m2:.2f} / StD={s2:.2f}",
                  f"P3 ({y3} / {x3}) - M={m3:.2f} / StD={s3:.2f}",
                  f"P4 ({y3} / {x4}) - M={m4:.2f} / StD={s4:.2f}"]

        if option == 'histo':
            fig, axes = plt.subplots(2, 2, figsize=(14, 12))
            for ax, data, title in zip(axes.flat, datasets, titles):
                ax.hist(data, bins=30, edgecolor=BLUE_IOGS, color=ORANGE_IOGS)
                ax.set_title(title)
            plt.tight_layout()
            # Dir
            save_dir = self._get_file_path(self.img_dir)
            if save_dir != '':
                plt.savefig(save_dir, dpi=300)
            self.bot_right.reinit_acquisition()
        elif option == 'time':
            base_colors = [BLUE_IOGS, ORANGE_IOGS,
                           rgb255_to_float(GREEN_IOGS), rgb255_to_float(RED_IOGS)]

            # Création du graphique
            plt.figure(figsize=(14, 12))
            datasets = [self.point1_data, self.point2_data,
                        self.point3_data, self.point4_data]
            max_number = len(self.point1_data)
            if max_number > 50:
                t = np.linspace(max_number-50, max_number, 50)
            else:
                t = np.linspace(1, max_number, max_number)

            for data, label, color in zip(datasets, titles, base_colors):
                if max_number > 50:
                    data = data[max_number-50:max_number]
                plt.plot(t, data, label=label, color=color, linewidth=2)

            plt.xlabel("Sample number")
            plt.ylabel("Values (DN)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            # Dir
            save_dir = self._get_file_path(self.img_dir)
            if save_dir != '':
                plt.savefig(save_dir, dpi=300)
            self.bot_right.reinit_acquisition()
        self.start_live()

    # Histogram
    def update_histogram(self, image):
        """
        Update histogram value from image.
        :param image:   Numpy array containing the new image.
        """
        bits_depth = self.parent.variables['bits_depth']
        self.bot_left.set_data(self.point1_data[:self.nb_of_images],
                               self.point2_data[:self.nb_of_images],
                               self.point3_data[:self.nb_of_images],
                               self.point4_data[:self.nb_of_images], bits_depth=bits_depth)

    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        self.stop_live()
        camera = self.parent.variables["camera"]
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False
        self.worker = None
        self.thread = None

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
            print(f'Saving path {file_path}')
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

    def _random_points(self, x_min, x_max, y_min, y_max, n: int=4):
        # All the possible points
        X = np.arange(x_min, x_max + 1)
        Y = np.arange(y_min, y_max + 1)
        couples = np.array(np.meshgrid(X, Y)).T.reshape(-1, 2)

        # Tirage sans répétition
        indices = np.random.choice(len(couples), size=n, replace=False)
        return couples[indices]

    def _process_stats(self):
        mean_1 = np.mean(self.point1_data)
        std_1 = np.std(self.point1_data)
        mean_2 = np.mean(self.point2_data)
        std_2 = np.std(self.point2_data)
        mean_3 = np.mean(self.point3_data)
        std_3 = np.std(self.point3_data)
        mean_4 = np.mean(self.point4_data)
        std_4 = np.std(self.point4_data)
        return mean_1, std_1, mean_2, std_2, mean_3, std_3, mean_4, std_4