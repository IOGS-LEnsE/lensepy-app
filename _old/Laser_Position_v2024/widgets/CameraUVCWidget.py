# -*- coding: utf-8 -*-
"""Laser Position Control Interface

Camera insert

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/10/03


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python CameraUVCWidget.py
"""

# Libraries to import
import sys
import cv2

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap


class CameraUVCWidget(QWidget):
    """
        Widget used to display 4-quadrants photodiode information.
        Children of QWidget - QWidget can be put in another widget and / or window
        ---
    """

    def __init__(self):
        """

        """
        super().__init__()

        self.camera_index = 0
        self.camera_cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)
        self.camera_nb = 1 #self.test_nb_cam()

        
        # Elements for displaying camera
        self.camera_display = QLabel()
        self.frame_width = self.width()-30
        self.frame_height = self.height()-20

        self.layout = QGridLayout()
        self.layout.addWidget(self.camera_display, 0, 0, 2, 0)
        
        self.prev_cam = QPushButton('Previous Cam')
        self.next_cam = QPushButton('Next Cam')
        self.prev_cam.clicked.connect(self.prev_cam_action)
        self.next_cam.clicked.connect(self.next_cam_action)
        
        self.layout.addWidget(self.prev_cam, 1, 0)
        self.layout.addWidget(self.next_cam, 1, 1)
        
        self.setLayout(self.layout)
        
    def prev_cam_action(self):
        print(f'-- Actual={self.camera_index} / Last={self.camera_nb}')
        if self.camera_index > 0:
            self.camera_index -= 1
            self.camera_cap.release()
            self.camera_cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)
        
    def next_cam_action(self):
        print(f'++ Actual={self.camera_index} / Last={self.camera_nb}')
        if self.camera_index < self.camera_nb :
            print('CHANGING !!')
            self.camera_index += 1
            self.camera_cap.release()
            self.camera_cap = cv2.VideoCapture(self.camera_index, cv2.CAP_MSMF)
        
        
    def test_nb_cam(self):
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            cap.release()
            index += 1
        return index

    def get_nb_cam(self):
        return self.camera_nb

    def refresh(self):
        # Reshape of the frame to adapt it to the widget
        ret, self.camera_array = self.camera_cap.read()
        self.frame_width = self.width()-30
        self.frame_height = self.height()-20
        self.camera_disp2 = cv2.resize(self.camera_array,
                                     dsize=(self.frame_width, 
                                            self.frame_height), 
                                     interpolation=cv2.INTER_CUBIC)
        
        h, w, ch = self.camera_disp2.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(self.camera_disp2.data, w, h, 
                                      bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.frame_width, self.frame_height, 
                                        Qt.AspectRatioMode.KeepAspectRatio)
        pmap = QPixmap.fromImage(p)
        
        self.camera_display.setPixmap(pmap)
    
    def inc_camera_index(self):
        

        
        self.camera_index += 1

# -------------------------------

class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()
        self.intro = CameraUVCWidget()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.intro)
        self.setCentralWidget(self.widget)


# -------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    
    window.intro.refresh()

    sys.exit(app.exec())
