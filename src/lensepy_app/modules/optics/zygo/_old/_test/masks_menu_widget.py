# -*- coding: utf-8 -*-
"""*masks_widget.py* file.

...

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QDialog,
    QLabel, QComboBox, QPushButton, QCheckBox, 
    QMessageBox, QTableView, QTableWidgetItem, QTableWidget
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QPoint, QAbstractTableModel
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QGuiApplication
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *
import cv2
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

if __name__ == '__main__':
    from combobox_bloc import ComboBoxBloc
else:
    from widgets.combobox_bloc import ComboBoxBloc

# %% Widget
class MasksMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        if self.parent is None:
            self.mask = None
            self.list_masks = []
            self.list_original_masks = []
            self.mask_unactived = None
        else:
            self.mask = self.parent.mask
            self.list_masks = self.parent.list_masks
            self.list_original_masks = self.parent.list_original_masks
            self.mask_unactived = self.parent.mask_unactived

            if hasattr(self.parent, 'image'):
                self.image = self.parent.image
        self.index_mask_selected = -1
         ### MOD


        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        
        self.label_title_masks_menu = QLabel("Gestion des masques")
        self.label_title_masks_menu.setStyleSheet(styleH1)
        
        self.subwidget_masks = QWidget()
        self.sublayout_masks = QHBoxLayout()

        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()
        
        self.button_circle_mask = QPushButton("Circulaire")
        self.button_circle_mask.setStyleSheet(unactived_button)
        self.button_circle_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_circle_mask.clicked.connect(self.selection_mask_circle)
        
        self.button_rectangle_mask = QPushButton("Rectangulaire")
        self.button_rectangle_mask.setStyleSheet(unactived_button)
        self.button_rectangle_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_rectangle_mask.clicked.connect(self.selection_mask_rectangle)
        
        self.button_polygon_mask = QPushButton("Polygonal")
        self.button_polygon_mask.setStyleSheet(unactived_button)
        self.button_polygon_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_polygon_mask.clicked.connect(self.selection_mask_polygon)

        self.combobox_select_mask = ComboBoxBloc("Masque sélectionné", map(str,list(range(1, len(self.list_masks)+1))))
        self.combobox_select_mask.currentIndexChanged.connect(self.combobox_mask_selected_changed)
        
        self.sublayout_left.addWidget(self.button_circle_mask)
        self.sublayout_left.addWidget(self.button_rectangle_mask)
        self.sublayout_left.addWidget(self.button_polygon_mask)
        self.sublayout_left.addWidget(self.combobox_select_mask)
        self.sublayout_left.addStretch()
        self.sublayout_left.setContentsMargins(0, 0, 0, 0)
        self.subwidget_left.setLayout(self.sublayout_left)
        
        # Second col
        # ----------
        self.subwidget_right = QWidget()
        self.sublayout_right = QVBoxLayout()
        
        self.button_erase_mask = QPushButton("Supprimer le masque")
        self.button_erase_mask.setStyleSheet(unactived_button)
        self.button_erase_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_erase_mask.clicked.connect(self.button_erase_mask_isClicked)

        self.button_erase_all_masks = QPushButton("Supprimer tous les masques")
        self.button_erase_all_masks.setStyleSheet(unactived_button)
        self.button_erase_all_masks.setFixedHeight(BUTTON_HEIGHT)
        self.button_erase_all_masks.clicked.connect(self.button_erase_all_masks_isClicked)

        self.checkbox_apply_mask = QCheckBox("Appliquer le masque")
        self.checkbox_apply_mask.setStyleSheet(styleCheckbox)
        self.checkbox_apply_mask.setChecked(True)
        self.checkbox_apply_mask.stateChanged.connect(self.checkbox_apply_mask_changed)

        self.checkbox_inverse_mask = QCheckBox("Inverser le masque")
        self.checkbox_inverse_mask.setStyleSheet(styleCheckbox)
        self.checkbox_inverse_mask.stateChanged.connect(self.checkbox_inverse_mask_changed)

        self.checkbox_inverse_merged_mask = QCheckBox("Inverser la fusion des masques")
        self.checkbox_inverse_merged_mask.setStyleSheet(styleCheckbox)
        self.checkbox_inverse_merged_mask.stateChanged.connect(self.checkbox_inverse_merged_mask_changed)
        
        # Create the table
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(3)  # Set number of rows
        self.tableWidget.setColumnCount(3)  # Set number of columns (Checkbox + Text)
        self.tableWidget.setHorizontalHeaderLabels(["Selection", "Inversion","Supprimer"])
        
        # Populate the table with checkboxes and items
        self.apply_checkbox_list = []
        self.inverse_checkbox_list = []
        self.button_list = []
        for row in range(len(self.list_masks)):
            # Create checkbox and set in the first column
            checkbox_item = QCheckBox()
            checkbox_item.setChecked(True)  # Set initial state to unchecked
            checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
            self.apply_checkbox_list.append(checkbox_item)
            self.tableWidget.setCellWidget(row, 0, checkbox_item)

            # Create checkbox in the second column
            checkbox_item = QCheckBox()
            checkbox_item.setChecked(False)  # Set initial state to unchecked
            checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
            self.inverse_checkbox_list.append(checkbox_item)
            self.tableWidget.setCellWidget(row, 1, checkbox_item)
            # Populate the table with checkboxes and items
            # Create checkbox in the second column
            button = QPushButton()
            button.clicked.connect(self.button_erase_mask_isClicked)
            self.button_list.append(button)
            self.tableWidget.setCellWidget(row, 2, button)

        # Resize columns to fit content
        self.tableWidget.resizeColumnsToContents()

        # Set the table widget as the central widget of the main window
        self.sublayout_right.addWidget(self.button_erase_mask)
        self.sublayout_right.addWidget(self.button_erase_all_masks)
        self.sublayout_right.addWidget(self.checkbox_apply_mask)
        self.sublayout_right.addWidget(self.checkbox_inverse_mask)
        self.sublayout_right.addWidget(self.checkbox_inverse_merged_mask)
        self.sublayout_right.addWidget(self.tableWidget)
        self.sublayout_right.addStretch()
        self.sublayout_right.setContentsMargins(0, 0, 0, 0)
        self.subwidget_right.setLayout(self.sublayout_right)
        

        # Combined
        # --------
        self.sublayout_masks.addWidget(self.subwidget_left)
        self.sublayout_masks.addWidget(self.subwidget_right)
        self.sublayout_masks.setContentsMargins(0, 0, 0, 0)
        self.subwidget_masks.setLayout(self.sublayout_masks)
        
        self.layout.addWidget(self.label_title_masks_menu)
        self.layout.addWidget(self.subwidget_masks)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def on_checkbox_state_changed(self, state):
        # Get the checkbox that triggered the state change
        checkbox = self.sender()  # This gives us the checkbox widget
        row = self.tableWidget.indexAt(checkbox.pos()).row()  # Get the row of the checkbox
        if state == Qt.CheckState.Checked:
            print(f"Checkbox in row {row + 1} checked")
        else:
            print(f"Checkbox in row {row + 1} unchecked")
    

    def checkbox_apply_mask_changed(self, state):
        checkbox = self.sender()
        index = -1
        for i in range (len(self.apply_checkbox_list)) :
            if checkbox == self.apply_checkbox_list[i]:
                index = i
        

        if index == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", "Veuillez sélectionner un masque.")
            self.checkbox_apply_mask.setChecked(True)
            return None
        try:
            if index is not None:
                if state == 0:
                    self.list_masks[index] = self.mask_unactived
                else:
                    self.list_masks[index] = self.list_original_masks[index]
            
        except Exception as e:
            print(f'Exception - checkbox_apply_mask_changed {e}')

        self.mask = np.logical_or.reduce(self.list_masks).astype(int)
        if np.all(self.mask == 0):
            self.mask = 1-self.mask

        self.update_display_mask()

        """import matplotlib.pyplot as plt

        plt.figure()
        plt.imshow(self.mask, cmap='RdYlGn')
        plt.colorbar()
        plt.show()"""

    def checkbox_inverse_mask_changed(self, state):
        checkbox = self.sender()
        index = -1
        for i in range (len(self.inverse_checkbox_list)) :
            if checkbox == self.inverse_checkbox_list[i]:
                index = i

        if index == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", "Veuillez sélectionner un masque.")
            self.checkbox_apply_mask.setChecked(False)
            return None
        #self.mask_selected = 1-self.mask_selected
        self.list_masks[index] = 1- self.list_masks[index]
        self.mask = np.logical_or.reduce(self.list_masks).astype(int)

        self.update_display_mask()

        """import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(self.mask, cmap='RdYlGn')
        plt.colorbar()
        plt.show()"""

    def checkbox_inverse_merged_mask_changed(self, state):
        self.mask = 1-self.mask

        self.update_display_mask()

        """import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(self.mask, cmap='RdYlGn')
        plt.colorbar()
        plt.show()"""

    def get_image(self) -> np.ndarray:
        self.parent.camera_thread.stop()
        self.parent.camera.init_camera()
        self.parent.camera.alloc_memory()
        self.parent.camera.start_acquisition()
        raw_array = self.parent.camera_widget.camera.get_image().copy()
        '''
        frame_width = self.parent.camera_widget.width()
        frame_height = self.parent.camera_widget.height()
        # Resize to the display size
        image_array_disp2 = resize_image_ratio(raw_array, frame_width, frame_height)
        # Convert the frame into an image
        image = array_to_qimage(image_array_disp2)
        # display it in the cameraDisplay
        self.camera_widget.camera_display.setPixmap(pmap)
        self.camera_widget.camera.stop_acquisition()
        self.camera_widget.camera.free_memory()
        '''
        self.parent.camera.stop_acquisition()
        self.parent.camera.free_memory()
        self.parent.camera_thread.start()

        self.image = raw_array
        return raw_array

    def selection_mask_circle(self):
        #msg
        msgbox=QMessageBox()
        msgbox.setWindowTitle("Masque circulaire")
        msgbox.setStyleSheet(styleH3)
        msgbox.setIcon(QMessageBox.Icon.Information)
        msgbox.setText("Veulliez choisir 3 points")
        msgbox.exec()

        if self.parent is not None:
            try:
                image = self.get_image()
                image_width = image.shape[1]
                image_height = image.shape[0]

                screen = QGuiApplication.primaryScreen()
                screen_size = screen.size()
                screen_width = screen_size.width()
                screen_height = screen_size.height()

                display_rate = 0.90*min(1, screen_width/image_width, screen_height/image_height)

                image = cv2.resize(image, (0, 0), fx = display_rate, fy = display_rate, interpolation=cv2.INTER_AREA)
                selection_window = SelectionMaskWindow(image, 'Circle')
                selection_window.exec()
                mask = selection_window.mask

                mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_CUBIC)

                self.list_masks.append(mask)
                self.list_original_masks.append(mask)

                self.combobox_select_mask.update_options(map(str,list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                if self.mask_unactived is None:
                    self.mask_unactived = np.zeros_like(self.mask)

                self.update_display_mask()
                # Populate the table with checkboxes and items
                self.apply_checkbox_list = []
                self.inverse_checkbox_list = []
                self.button_list=[]
                for row in range(len(self.list_masks)):
                    # Create checkbox and set in the first column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(True)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
                    self.apply_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 0, checkbox_item)

                    # Create checkbox in the second column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(False)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
                    self.inverse_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 1, checkbox_item)
                    # Populate the table with checkboxes and items
                    # Create checkbox in the second column
                    button = QPushButton()
                    button.clicked.connect(self.button_erase_mask_isClicked)
                    self.button_list.append(button)
                    self.tableWidget.setCellWidget(row, 2, button)

                """import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask, cmap='RdYlGn')
                plt.axis('equal')
                plt.show()"""

            except Exception as e:
                print(f'Exception - selection_mask_circle_isClicked {e}')

    def selection_mask_rectangle(self):
        #msg
        msgbox=QMessageBox()
        msgbox.setWindowTitle("Masque Rectangulaire")
        msgbox.setStyleSheet(styleH3)
        msgbox.setIcon(QMessageBox.Icon.Information)
        msgbox.setText("Veulliez choisir 2 points")
        msgbox.exec()
        
        if self.parent is not None:
            try:
                image = self.get_image()
                image_width = image.shape[1]
                image_height = image.shape[0]

                screen = QGuiApplication.primaryScreen()
                screen_size = screen.size()
                screen_width = screen_size.width()
                screen_height = screen_size.height()

                display_rate = 0.90*min(1, screen_width/image_width, screen_height/image_height)

                image = cv2.resize(image, (0, 0), fx = display_rate, fy = display_rate, interpolation=cv2.INTER_AREA)
                selection_window = SelectionMaskWindow(image, 'Rectangle')
                selection_window.exec()
                mask = selection_window.mask

                mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
                self.list_masks.append(mask)
                self.list_original_masks.append(mask)

                self.combobox_select_mask.update_options(map(str,list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                if self.mask_unactived is None:
                    self.mask_unactived = np.zeros_like(self.mask)

                self.update_display_mask()
                # Populate the table with checkboxes and items
                self.apply_checkbox_list = []
                self.inverse_checkbox_list = []
                self.button_list=[]
                for row in range(len(self.list_masks)):
                    # Create checkbox and set in the first column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(True)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
                    self.apply_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 0, checkbox_item)

                    # Create checkbox in the second column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(False)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
                    self.inverse_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 1, checkbox_item)
                    # Populate the table with checkboxes and items
                    # Create checkbox in the second column
                    button = QPushButton()
                    button.clicked.connect(self.button_erase_mask_isClicked)
                    self.button_list.append(button)
                    self.tableWidget.setCellWidget(row, 2, button)
                        

                """import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask)
                plt.show()"""
            except Exception as e:
                print(f'Exception - selection_mask_rectangle_isClicked {e}')

    def selection_mask_polygon(self):
        #msg
        msgbox=QMessageBox()
        msgbox.setWindowTitle("Masque polygonal")
        msgbox.setStyleSheet(styleH3)
        msgbox.setIcon(QMessageBox.Icon.Information)
        msgbox.setText("Veulliez choisir au moins 3 points. Recliquez sur le premier point")
        msgbox.exec()
        
        if self.parent is not None:
            try:
                image = self.get_image()
                image_width = image.shape[1]
                image_height = image.shape[0]

                screen = QGuiApplication.primaryScreen()
                screen_size = screen.size()
                screen_width = screen_size.width()
                screen_height = screen_size.height()

                display_rate = 0.90*min(1, screen_width/image_width, screen_height/image_height)

                image = cv2.resize(image, (0, 0), fx = display_rate, fy = display_rate, interpolation=cv2.INTER_AREA)
                selection_window = SelectionMaskWindow(image, 'Polygon')
                selection_window.exec()
                mask = selection_window.mask

                mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
                self.list_masks.append(mask)
                self.list_original_masks.append(mask)

                self.combobox_select_mask.update_options(map(str,list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                if self.mask_unactived is None:
                    self.mask_unactived = np.zeros_like(self.mask)

                """import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask, cmap='RdYlGn')
                plt.show()"""

                self.update_display_mask()
                # Populate the table with checkboxes and items
                self.apply_checkbox_list = []
                self.inverse_checkbox_list = []
                self.button_list=[]
                for row in range(len(self.list_masks)):
                    # Create checkbox and set in the first column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(True)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
                    self.apply_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 0, checkbox_item)

                    # Create checkbox in the second column
                    checkbox_item = QCheckBox()
                    checkbox_item.setChecked(False)  # Set initial state to unchecked
                    checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
                    self.inverse_checkbox_list.append(checkbox_item)
                    self.tableWidget.setCellWidget(row, 1, checkbox_item)
                    # Populate the table with checkboxes and items
                    # Create checkbox in the second column
                    button = QPushButton()
                    button.clicked.connect(self.button_erase_mask_isClicked)
                    self.button_list.append(button)
                    self.tableWidget.setCellWidget(row, 2, button)

            except Exception as e:
                print(f'Exception - selection_mask_polygon_isClicked {e}')

    def combobox_mask_selected_changed(self, index):
        self.index_mask_selected = index - 1
        if self.index_mask_selected >= 0 and self.index_mask_selected < len(self.list_masks):
            self.mask_selected = self.list_masks[self.index_mask_selected]

    def button_erase_mask_isClicked(self):
        button = self.sender()
        index = -1
        for i in range (len(self.button_list)) :
            if button == self.button_list[i]:
                index = i
        if index == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", "Veuillez sélectionner un masque.")
            self.button_erase_mask.setChecked(True)
            return None
        
        elif len(self.list_masks) > 0:
            reply = QMessageBox.question(self, "Suppression du masque", "Voulez-vous supprimer ce masque ?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                del self.list_masks[index]
                del self.list_original_masks[index]
                index -= 1

                self.combobox_select_mask.update_options(map(str,list(range(1, len(self.list_masks)+1))))
                self.mask = self.mask_unactived

                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.information(self, "Information", "Masque supprimé avec succès.")

            self.mask = 1-self.mask_unactived
            
            self.update_display_mask()

            self.apply_checkbox_list = []
            self.inverse_checkbox_list = []
            self.button_list=[]
            for row in range(len(self.list_masks)):
                # Create checkbox and set in the first column
                checkbox_item = QCheckBox()
                checkbox_item.setChecked(True)  # Set initial state to unchecked
                checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
                self.apply_checkbox_list.append(checkbox_item)
                self.tableWidget.setCellWidget(row, 0, checkbox_item)

                # Create checkbox in the second column
                checkbox_item = QCheckBox()
                checkbox_item.setChecked(False)  # Set initial state to unchecked
                checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
                self.inverse_checkbox_list.append(checkbox_item)
                self.tableWidget.setCellWidget(row, 1, checkbox_item)
                # Populate the table with checkboxes and items
                # Create checkbox in the second column
                button = QPushButton()
                button.clicked.connect(self.button_erase_mask_isClicked)
                self.button_list.append(button)
                self.tableWidget.setCellWidget(row, 2, button)

    def button_erase_all_masks_isClicked(self):
        reply = QMessageBox.question(self, "Suppression des masques", "Voulez-vous supprimer tous les masques ?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            #self.combobox_select_mask.setCursor(1)

            self.checkbox_apply_mask.setChecked(True)
            self.checkbox_inverse_mask.setChecked(False)
            self.checkbox_inverse_merged_mask.setChecked(False)

            self.list_masks.clear()
            self.list_original_masks.clear()
            self.index_mask_selected = -1

            self.combobox_select_mask.update_options(map(str,list(range(1, len(self.list_masks)+1))))
            self.mask = np.logical_or.reduce(self.list_masks).astype(int)

            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.information(self, "Information", "Masques supprimés avec succès.")

            self.mask = 1-self.mask_unactived
            self.update_display_mask()

            self.apply_checkbox_list = []
            self.inverse_checkbox_list = []
            self.button_list=[]
            for row in range(len(self.list_masks)):
                # Create checkbox and set in the first column
                checkbox_item = QCheckBox()
                checkbox_item.setChecked(True)  # Set initial state to unchecked
                checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
                self.apply_checkbox_list.append(checkbox_item)
                self.tableWidget.setCellWidget(row, 0, checkbox_item)

                # Create checkbox in the second column
                checkbox_item = QCheckBox()
                checkbox_item.setChecked(False)  # Set initial state to unchecked
                checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
                self.inverse_checkbox_list.append(checkbox_item)
                self.tableWidget.setCellWidget(row, 1, checkbox_item)
                # Populate the table with checkboxes and items
                # Create checkbox in the second column
                button = QPushButton()
                button.clicked.connect(self.button_erase_mask_isClicked)
                self.button_list.append(button)
                self.tableWidget.setCellWidget(row, 2, button)

    def update_display_mask(self):
        try:
            self.parent.display_mask_widget.set_image_data(np.squeeze(self.image), np.squeeze(self.mask)*255, colormap_name1='gray', colormap_name2='RdYlGn', alpha=0.4)
            self.parent.display_mask_widget
            
            
        except Exception as e:
            print(f"update_display_mask - {e}")
    

class SelectionMaskWindow(QDialog):
    def __init__(self, image, mask_type):
        super().__init__()

        # print(self.width(), self.height()) # Window size

        self.setWindowTitle('Enfoncez ENTRÉE pour valider le masque.')
        self.layout = QVBoxLayout()

        self.image = image

        self.qimage = QImage(self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        if mask_type == 'Circle':
            print('Circle')
            self.label.mousePressEvent = self.get_points_circle
        elif mask_type == 'Rectangle':
            print('Rectangle')
            self.label.mousePressEvent = self.get_points_rectangle
        elif mask_type == 'Polygon':
            print('Polygon')
            self.label.mousePressEvent = self.get_points_polygon

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.close_window()

    def get_points_circle(self, event):
        self.can_draw = True
        if self.can_draw and len(self.points) < 3:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 3:
                self.draw_circle()
                self.can_draw = False

    def get_points_rectangle(self, event):
        self.can_draw = True
        if self.can_draw and len(self.points) < 2:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 2:
                self.draw_rectangle()
                self.can_draw = False

    def get_points_polygon(self, event):
        limit = 10 # px

        self.can_draw = True
        if self.can_draw:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())

            if len(self.points)>1 and (self.points[-1][0] - self.points[0][0])**2+(self.points[-1][1] - self.points[0][1])**2 < limit**2:
                self.draw_polygon()
                self.can_draw = False

    def draw_point(self, x, y):
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.red, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Afficher la couche des points
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

    def find_circle_center(self, x0, y0, x1, y1, x2, y2):
        mid_x_01 = (x0 + x1) / 2
        mid_y_01 = (y0 + y1) / 2
        mid_x_02 = (x0 + x2) / 2
        mid_y_02 = (y0 + y2) / 2
        
        if x0 == x1:
            slope_perp_01 = None
            intercept_perp_01 = mid_x_01
        else:
            slope_perp_01 = -1 / ((y1 - y0) / (x1 - x0))
            intercept_perp_01 = mid_y_01 - slope_perp_01 * mid_x_01
            
        if x0 == x2:
            slope_perp_02 = None
            intercept_perp_02 = mid_x_02
        else:
            slope_perp_02 = -1 / ((y2 - y0) / (x2 - x0))
            intercept_perp_02 = mid_y_02 - slope_perp_02 * mid_x_02
        
        if slope_perp_01 is None or slope_perp_02 is None:
            if slope_perp_01 is None:
                X = mid_x_01
                Y = slope_perp_02 * X + intercept_perp_02
            else:
                X = mid_x_02
                Y = slope_perp_01 * X + intercept_perp_01
        else:
            X = (intercept_perp_02 - intercept_perp_01) / (slope_perp_01 - slope_perp_02)
            Y = slope_perp_01 * X + intercept_perp_01
        
        return X, Y

    def draw_circle(self):
        try:
            x0, y0 = self.points[-3]
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]

            x_center, y_center = self.find_circle_center(x0, y0, x1, y1, x2, y2)
            x_center = int(x_center)
            y_center = int(y_center)
            radius = int(np.sqrt((x_center-x0)**2+(y_center-y0)**2))

            """print(f"x0={x0}, y0={y0}")
            print(f"x1={x1}, y1={y1}")
            print(f"x2={x2}, y2={y2}")
            print(f"centre: ({x_center},{y_center})")
            print(f"dist P1-centre: {np.sqrt((x_center-x0)**2+(y_center-y0)**2)}")
            print(f"dist P2-centre: {np.sqrt((x_center-x1)**2+(y_center-y1)**2)}")
            print(f"dist P3-centre: {np.sqrt((x_center-x2)**2+(y_center-y2)**2)}")
            print(f"rayon: {radius}")"""

            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x_center, y_center), radius, radius)
            painter.end()

            # Afficher le cercle
            combined_pixmap = self.pixmap.copy()
            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, self.point_layer)
            painter.end()

            self.label.setPixmap(combined_pixmap)

            # Update mask
            self.mask = self.create_circular_mask(x_center, y_center, radius)
        except Exception as e:
            print(f'Exception - circle_mask_draw {e}')

    def draw_rectangle(self):
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

        """print(f"x1={x1}, y1={y1}")
        print(f"x2={x2}, y2={y2}")"""

        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(x1, y1, (x2-x1), (y2-y1))
        painter.end()

        # Afficher le cercle
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_rectangular_mask(x1, y1, x2, y2)

    def draw_polygon(self):
        points = [QPoint(self.points[i][0], self.points[i][1]) for i in range(len(self.points))]

        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawPolygon(points)
        painter.end()

        # Afficher le cercle
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_polygonal_mask()

    def create_circular_mask(self, x_center, y_center, radius):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]
        mask_area = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2
        mask[mask_area] = 1
        return mask
    
    def create_rectangular_mask(self, x1, y1, x2, y2):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        mask[y1:y2, x1:x2] = 1
        mask[y1:y2, x2:x1] = 1
        mask[y2:y1, x2:x1] = 1
        mask[y2:y1, x1:x2] = 1
        return mask
    
    def create_polygonal_mask(self):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(self.points)], 1)
        return mask
    
    def close_window(self):
        self.accept()

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}

            self.setWindowTitle(translate("window_title_masks_widget"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = MasksMenuWidget()
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
