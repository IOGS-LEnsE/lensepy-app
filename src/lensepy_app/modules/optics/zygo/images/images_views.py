import importlib
import os

import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
from lensepy_app.widgets.objects import make_hline
from lensepy import translate
from lensepy.utils import imread_rgb
from lensepy.css import *


class ImagesOpeningWidget(QWidget):
    """
    Widget to display image opening options.
    """

    image_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent    # Controller
        layout = QVBoxLayout()

        layout.addWidget(make_hline())

        label = QLabel(translate('image_opening_dialog'))
        label.setStyleSheet(styleH2)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.open_button = QPushButton(translate('image_opening_button'))
        self.open_button.setStyleSheet(unactived_button)
        self.open_button.setFixedHeight(BUTTON_HEIGHT)
        self.open_button.clicked.connect(self.handle_opening)
        layout.addWidget(self.open_button)

        layout.addStretch()
        self.setLayout(layout)

    def handle_opening(self):
        sender = self.sender()
        if sender == self.open_button:
            self.open_button.setStyleSheet(actived_button)
            # Check if for a default directory for images.
            module_path = self.parent.parent.xml_app.get_parameter_xml('img_dir')
            image_filepath = self.open_image(module_path)
            self.image_opened.emit(image_filepath)
            self.open_button.setStyleSheet(unactived_button)

    def open_image(self, default_dir: str = '') -> str:
        """
        Open an image from a file.
        :return:    Filepath of the file.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_dir, "Zygo Images (*.mat)")
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


class ImagesChoiceView(QWidget):
    """Images Choice."""

    images_changed = pyqtSignal(int, int)

    def __init__(self, parent) -> None:
        super().__init__()
        self.controller = parent
        self.data_set = None

        # valeurs par défaut safe
        self.number_of_images_per_set = 0
        self.sets_of_images_number = 0
        self.selected_set = 1

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ---- Title ----
        self.label_images_choice_title = QLabel(translate("label_images_choice_title"))
        self.label_images_choice_title.setStyleSheet(styleH1)
        self.label_images_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- Labels ----
        self.label_set_of_images = QLabel("No dataset loaded")
        self.label_set_of_images.setStyleSheet(styleH2)
        self.label_set_of_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_images = QLabel("No Image")
        self.label_status_images.setStyleSheet(styleH2)
        self.label_status_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_masks = QLabel("No Mask")
        self.label_status_masks.setStyleSheet(styleH2)
        self.label_status_masks.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- Images widget ----
        self.images_select_widget = QWidget()
        self.layout_images = QHBoxLayout()
        self.images_select_widget.setLayout(self.layout_images)
        self.images_button_select = []

        # ---- Masks widget ----
        self.masks_select_widget = QWidget()
        self.layout_masks = QHBoxLayout()
        self.masks_select_widget.setLayout(self.layout_masks)
        self.masks_button_select = []

        # ---- Sets widget ----
        self.sets_of_images_widget = QWidget()
        self.layout_set = QHBoxLayout()
        self.sets_of_images_widget.setLayout(self.layout_set)
        self.sets_button_list = []

        # ---- Layout ----
        self.layout.addWidget(self.label_images_choice_title)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.label_set_of_images)
        self.layout.addWidget(self.sets_of_images_widget)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_images)
        self.layout.addWidget(make_hline())
        self.layout.addWidget(self.label_status_masks)
        self.layout.addWidget(self.masks_select_widget)

    def update_dataset(self, data_set):
        """Call this when dataset becomes available."""
        self.data_set = data_set
        # Init values
        self.number_of_images_per_set = self.data_set.set_size
        self.sets_of_images_number = self.data_set.images_sets.get_number_of_sets()
        self.selected_set = 1

        self.build_sets_buttons()
        self.build_images_buttons()
        self.set_images_status(True, 1)
        self.set_masks_status(True, self.data_set.masks_sets.get_masks_number())

    # =========================================================
    def reset_view(self):
        """UI when no dataset"""
        self.label_set_of_images.setText("No dataset loaded")
        self.label_status_images.setText("No Image")
        self.label_status_masks.setText("No Mask")

        self.clear_layout(self.layout_images)
        self.clear_layout(self.layout_masks)
        self.clear_layout(self.layout_set)

    # =========================================================
    def build_images_buttons(self):
        self.clear_layout(self.layout_images)
        self.images_button_select = []

        for i in range(self.number_of_images_per_set):
            button = QPushButton(str(i + 1))
            button.setFixedWidth(40)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.display_image)
            self.images_button_select.append(button)
            self.layout_images.addWidget(button)

    def build_sets_buttons(self):
        self.clear_layout(self.layout_set)
        self.sets_button_list = []

        if self.sets_of_images_number <= 1:
            self.label_set_of_images.setText("1 set")
            return

        self.label_set_of_images.setText(f"{self.sets_of_images_number} sets")

        for i in range(self.sets_of_images_number):
            button = QPushButton(f"S{i + 1}")
            button.setFixedWidth(40)
            button.setStyleSheet(actived_button if i == 0 else unactived_button)
            button.clicked.connect(self.select_set)
            self.sets_button_list.append(button)
            self.layout_set.addWidget(button)

    # =========================================================
    def set_images_status(self, value: bool, index: int = 1):
        if not value or not self.data_set:
            self.label_status_images.setText("No Image")
            return

        self.label_status_images.setText("Display image ?")

        if self.images_button_select:
            self.images_button_select[index - 1].setStyleSheet(actived_button)

    def set_masks_status(self, value: bool, number: int = 0):
        self.clear_layout(self.layout_masks)
        self.masks_button_select = []

        if not value or not self.data_set:
            self.label_status_masks.setText("No Mask")
            return

        self.label_status_masks.setText(f"{number} Mask(s) / Display ?")

        for i in range(number):
            button = QPushButton(str(i + 1))
            button.setFixedWidth(40)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.display_mask)
            self.masks_button_select.append(button)
            self.layout_masks.addWidget(button)

    # =========================================================
    def display_image(self, event):
        if not self.data_set:
            return

        try:
            self.inactivate_buttons()
            sender = self.sender()
            sender.setStyleSheet(actived_button)

            for i in range(self.number_of_images_per_set):
                if sender == self.images_button_select[i]:
                    self.images_changed.emit(i + 1, self.selected_set)
        except Exception as e:
            print(f"display : {e}")

    def display_mask(self, event):
        if not self.data_set:
            return

        try:
            self.inactivate_buttons()
            sender = self.sender()
            sender.setStyleSheet(actived_button)

            mask_number = self.data_set.masks_sets.get_masks_number()
            for i in range(mask_number):
                if sender == self.masks_button_select[i]:
                    image = self.data_set.images_sets.get_image_from_set(1, self.selected_set)
                    mask, _ = self.data_set.masks_sets.get_mask(i + 1)
                    image_disp = (mask * image).astype(np.uint8)
                    self.controller.top_left_widget.set_image_from_array(image_disp)
        except Exception as e:
            print(f"display_masks : {e}")

    # =========================================================
    def inactivate_buttons(self):
        for btn in self.images_button_select:
            btn.setStyleSheet(unactived_button)
        for btn in self.masks_button_select:
            btn.setStyleSheet(unactived_button)

    def select_set(self):
        sender = self.sender()

        for i, btn in enumerate(self.sets_button_list):
            if btn == sender:
                self.selected_set = i + 1
                btn.setStyleSheet(actived_button)
            else:
                btn.setStyleSheet(unactived_button)

    # =========================================================
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()