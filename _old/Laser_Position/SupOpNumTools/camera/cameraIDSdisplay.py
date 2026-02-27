# -*- coding: utf-8 -*-
"""IDS Camera Widget library.

/!\ Only for IDS USB 2.0 CMOS camera
Based on pyueye library

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/01/01


Authors
-------
    Julien VILLEMEJANE

Use
---
    >>> python cameraIDSdisplay.py
"""
# Standard Libraries
import numpy as np
import cv2

# Third pary imports
from threading import Timer
from PyQt6.QtWidgets import QWidget, QComboBox, QPushButton
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

# Local libraries
import SupOpNumTools as sont
import SupOpNumTools.camera.cameraIDS as camIDS


class cameraIDSdisplay(QWidget):
    
    connectedSignal = pyqtSignal(str)
    
    def __init__(self, cam = None):
        super().__init__() 
        
        # Camera
        self.camera = cam
        self.max_width = -1
        self.max_height = -1
        self.exposureTime = 20.0
        self.cameraConnected = False
        
        print(f'Init {self.camera}')
        
        self.mainLayout = QGridLayout()
        
        # Elements for List of camera        
        self.labelNoCam = QLabel('NO CAMERA')
        self.cbListCam = QComboBox()
        self.btConnect = QPushButton('Connect')
        self.btConnect.clicked.connect(self.connectCam)
        self.btRefresh = QPushButton('Refresh')
        self.btRefresh.clicked.connect(self.refreshList)
        
        
        # Elements for displaying camera
        self.cameraDisplay = QLabel()
        
        # Display list or camera
        self.displayCam(self.camera)
        
        # Graphical interface
        self.setLayout(self.mainLayout)
        
        # Other variables
        self.frameWidth = self.cameraDisplay.width()
        self.frameHeight = self.cameraDisplay.height()

    
    def clearLayout(self):
        for i in reversed(range(self.mainLayout.count())):
            # print(self.mainLayout.itemAt(i))
            self.mainLayout.removeItem(self.mainLayout.itemAt(i))


    def displayCam(self, camera):
        # Detect if camera is connected or display a list
        if(camera == None):
            if(self.cameraConnected):
                self.camera.stop_camera()     
                self.cameraConnected = False
                
            self.clearLayout()
            print('No Cam')
            
            self.mainLayout.addWidget(self.labelNoCam, 0, 0)
            self.mainLayout.addWidget(self.cbListCam, 1, 0)
            self.mainLayout.addWidget(self.btConnect, 2, 0, 2, 1)
            self.mainLayout.addWidget(self.btRefresh, 4, 0)
            
            
            self.setLayout(self.mainLayout)
            self.nb_cam = camIDS.get_nb_of_cam()
            if(self.nb_cam > 0):
                self.cameraList = camIDS.get_cam_list() 
                self.cbListCam.clear()
                for i in range(self.nb_cam):
                    cameraT = self.cameraList[i]
                    self.cbListCam.addItem(f'{cameraT[2]} (SN : {cameraT[1]})')
            
        else:
            print('Camera OK')
    
    def refreshList(self):
        self.clearLayout()
        self.displayCam(None)
        
    def connectCam(self):
        '''
        Event link to the connect button of the GUI.

        Returns
        -------
        None.

        '''
        print('Connect Cam')        
        self.selectedCamera = self.cbListCam.currentIndex()
        self.camera = camIDS.uEyeCamera(self.selectedCamera)
        self.cameraConnected = True
        
        self.max_width = self.camera.get_sensor_max_width()
        print(f'MAX = {self.max_width} - {type(self.max_width)}')
        self.max_height = self.camera.get_sensor_max_height()
        self.camera.set_exposure(self.exposureTime)
        self.camera.set_colormode(camIDS.ueye.IS_CM_MONO8)
        self.camera.set_aoi(0, 0, self.max_width, self.max_height)
        self.camera.alloc()
        self.camera.capture_video()
        self.clearLayout()
        self.refresh()
        self.connectedSignal.emit('C')
        
    
    def refresh(self):
        '''
        Refresh the displaying image from camera.

        Returns
        -------
        None.
        '''
        
        if(self.cameraConnected):
            self.clearLayout()
            self.mainLayout.addWidget(self.cameraDisplay, 0, 0)
            self.frameWidth = self.cameraDisplay.width()
            self.frameHeight = self.cameraDisplay.height()
            
            array = self.camera.get_image()
            X, Y, W, H = self.camera.get_aoi()
            frame = np.reshape(array,(H, W, -1))
            frame = cv2.resize(frame, dsize=(self.frameWidth, self.frameHeight), interpolation=cv2.INTER_CUBIC)
            image = QImage(frame, frame.shape[1],frame.shape[0], frame.shape[1], QImage.Format_Grayscale8)
            pmap = QPixmap(image)
            self.cameraDisplay.setPixmap(pmap)
            
            Timer(0.2, self.refresh).start()
        else:
            print('No Camera')

    def disconnect(self):
        if(self.cameraConnected):
            self.camera.stop_camera()
            self.cameraConnected = False
            
    def getCamera(self):
        return self.camera

    def isCameraConnected(self):
        return self.cameraConnected

        
'''
CameraIDSmainParams class
Update main parameters of an IDS Camera (exposure time, AOI...)
'''
class cameraIDSmainParams(QWidget):
    
    expoSignal = pyqtSignal(str)
    fpsSignal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__() 
        
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        
        # Elements of the widget
        self.fpsBl = sont.sliderBlock()
        self.fpsBl.setUnits('fps')  
        self.fpsBl.setName('FramePerSec')  
        self.fpsBl.asignal.connect(self.sendSignalFPS)
        self.mainLayout.addWidget(self.fpsBl, 0, 0)
        
        self.exposureTimeBl = sont.sliderBlock()
        self.exposureTimeBl.setUnits('ms')  
        self.exposureTimeBl.setName('Exposure Time')  
        self.exposureTimeBl.asignal.connect(self.sendSignalExpoTime)
        self.mainLayout.addWidget(self.exposureTimeBl, 1, 0)
        
        
    def update(self):
        print('update Params IDS')
        
    def setExposureTimeRange(self, expoMin, expoMax):
        self.exposureTimeBl.setMinMaxSlider(expoMin, expoMax)
        
    def getExposureTime(self):
        return self.exposureTimeBl.getRealValue()
    
    def setExposureTime(self, value):
        return self.exposureTimeBl.setValue(value)
    
    def setFPSRange(self, fpsMin, fpsMax):
        self.fpsBl.setMinMaxSlider(fpsMin, fpsMax)
        
    def getFPS(self):
        return self.fpsBl.getRealValue()
    
    def setFPS(self, value):
        return self.fpsBl.setValue(value)

    def sendSignalExpoTime(self):
        self.expoSignal.emit('S')  

    def sendSignalFPS(self):
        self.fpsSignal.emit('F')  