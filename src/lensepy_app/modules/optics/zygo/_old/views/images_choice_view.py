# -*- coding: utf-8 -*-
"""*images_choice_view.py* file.

./views/images_choice_view.py contains ImagesChoiceView class to display an image selection manager.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt

class ImagesChoiceView(QWidget):
    """Images Choice."""

    def __init__(self, controller) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__()
        self.controller = controller
        self.data_set = self.controller.data_set
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_images_choice_title = QLabel(translate("label_images_choice_title"))
        self.label_images_choice_title.setStyleSheet(styleH1)
        self.label_images_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ## Other graphical elements of the widget
        self.label_set_of_images = QLabel()
        self.label_set_of_images.setStyleSheet(styleH2)
        self.label_set_of_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_images = QLabel(translate("label_status_images"))
        self.label_status_images.setStyleSheet(styleH2)
        self.label_status_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_masks = QLabel(translate("label_status_masks"))
        self.label_status_masks.setStyleSheet(styleH2)
        self.label_status_masks.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget set of images
        self.number_of_images_per_set = self.data_set.set_size
        self.sets_of_images_number = self.data_set.get_images_sets()
        self.sets_of_images_widget = QWidget()
        self.layout_set = QHBoxLayout()
        self.sets_of_images_widget.setLayout(self.layout_set)
        self.sets_button_list = []
        self.selected_set = 0

        # Widget images selection
        self.images_select_widget = QWidget()
        self.layout_images = QHBoxLayout()
        self.images_select_widget.setLayout(self.layout_images)
        self.images_button_select = []
        for i in range(self.number_of_images_per_set):
            button = QPushButton(str(i + 1))
            button.setFixedWidth(40)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.display_image)
            self.images_button_select.append(button)

        # Widget masks selection
        self.masks_select_widget = QWidget()
        self.layout_masks = QHBoxLayout()
        self.masks_select_widget.setLayout(self.layout_masks)
        self.masks_button_select = []

        # Add graphical elements in the layout
        self.layout.addWidget(self.label_images_choice_title)
        self.layout.addWidget(self.label_set_of_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_masks)
        self.layout.addWidget(self.masks_select_widget)

        if self.data_set.is_data_ready():
            self.set_images_status(True, 1)
            self.set_masks_status(True, 1)

    def set_images_status(self, value: bool, index: int = 1):
        """Update images status.
        :param value: True if images are opened.
        :param index: Index of the image selected for display. Default 1.
        """
        if value:
            self.sets_of_images_number = self.data_set.images_sets.get_number_of_sets()
            if self.sets_of_images_number > 1:
                self.label_set_of_images.setText(f'{self.sets_of_images_number} set(s) of images')
                for i in range(self.sets_of_images_number):
                    button = QPushButton(f'S{i + 1}')
                    button.setFixedWidth(40)
                    if i == 0:
                        button.setStyleSheet(actived_button)
                    else:
                        button.setStyleSheet(unactived_button)
                    button.clicked.connect(self.select_set)
                    self.sets_button_list.append(button)
                    self.layout_set.addWidget(self.sets_button_list[i])
            self.label_status_images.setText('Display image ?')
            for i in range(self.number_of_images_per_set):
                self.layout_images.addWidget(self.images_button_select[i])
            self.images_button_select[index - 1].setStyleSheet(actived_button)
        else:
            self.label_status_images.setText('No Image')

    def set_masks_status(self, value: bool, number: int = 0):
        """Update masks status.
        :param value: True if there is only one mask.
        :param number: Number of potential masks.
        """
        if value:
            self.label_status_masks.setText(f'{number} Mask(s) / Display ?')
            self.selected_set = 1
            for i in range(number):
                button = QPushButton(str(i + 1))
                button.setFixedWidth(40)
                button.setStyleSheet(unactived_button)
                button.clicked.connect(self.display_mask)
                self.masks_button_select.append(button)
                self.layout_masks.addWidget(self.masks_button_select[i])
        else:
            self.label_status_masks.setText('No Mask')

    def inactivate_buttons(self):
        """Set unactivated all the buttons."""
        for i in range(self.number_of_images_per_set):
            self.images_button_select[i].setStyleSheet(unactived_button)
        mask_number = self.data_set.masks_sets.get_masks_number()
        for i in range(mask_number):
            self.masks_button_select[i].setStyleSheet(unactived_button)

    def select_set(self, event):
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        for i in range(self.sets_of_images_number):
            if sender == self.sets_button_list[i]:
                self.selected_set = i + 1

    def display_image(self, event):
        """Action performed when an image is selected to be displayed."""
        try:
            self.inactivate_buttons()
            sender = self.sender()
            sender.setStyleSheet(actived_button)
            for i in range(self.number_of_images_per_set):
                if sender == self.images_button_select[i]:
                    image = self.data_set.images_sets.get_image_from_set(i + 1, self.selected_set)
                    image_disp = image.copy().astype(np.uint8)
                    self.controller.top_left_widget.set_image_from_array(image_disp)
                    '''
                    if i != 5:

                    else:
                        set_of_images = self.parent.parent.images.get_images_set(self.selected_set)
                        image = generate_images_grid(set_of_images)
                        self.parent.top_left_widget.set_image_from_array(image)
                    '''
        except Exception as e:
            print(f'display : {e}')

    def display_mask(self, event):
        """Action performed when an image is selected to be displayed."""
        self.inactivate_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        try:
            mask_number = self.data_set.masks_sets.get_masks_number()
            for i in range(mask_number):
                if sender == self.masks_button_select[i]:
                    image = self.data_set.images_sets.get_image_from_set(1, self.selected_set)
                    mask, _ = self.data_set.masks_sets.get_mask(i + 1)
                    image_disp = (mask * image).copy().astype(np.uint8)
                    self.controller.top_left_widget.set_image_from_array(image_disp)
        except Exception as e:
            print(f'display_masks : {e}')

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)


