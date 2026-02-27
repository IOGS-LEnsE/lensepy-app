# -*- coding: utf-8 -*-
"""
CameraWidget for CMOS Sensor Display

/!\ Only for IDS USB 2.0 CMOS camera
Based on pyueye library

--------------------------
(c) LEnsE - Institut d'Optique

Created on Sun Jul  2 09:30:45 2023

@author: Julien VILLEMEJANE
First work by Romain ETIENNE (June 2023 - Intern at LEnsE)
"""
# PEP257 / PEP8 // NOT OK



# Standard
import numpy as np
import cv2
import sys
from pyueye import ueye
import camera
import time

# Graphical interface
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QComboBox, QSlider, QLineEdit
    )
from PyQt6.QtGui import QPixmap, QImage
from pyqtgraph import PlotWidget, plot, mkPen


from PyQt6.QtWidgets import QMainWindow, QLabel, QComboBox, QWidget, QGroupBox
from PyQt6.QtCore import QTimer, Qt

#-----------------------------------------------------------------------------------------------

class CameraWidget(QWidget):
    """
    Widget used to show our camera.
    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    def __init__(self, colormode = "MONO8"):
        """
        Initialisation of our camera widget.
        """
        super().__init__(parent=None)

        self.setStyleSheet("background-color: #4472c4; border-radius: 10px;"
                           "border-color: black; border-width: 2px; font: bold 12px; padding: 20px;"
                           "border-style: solid;")

        # Camera
        self.camera = None
        self.max_width = 0
        self.max_height = 0
        self.colormode = colormode
        self.aoiTrueFalse = False
        self.nBitsPerPixel = 0

        # Graphical interface
        self.cameraInfo = QLabel("Camera Info")
        self.cameraListCombo = QComboBox()
        self.initListCamera()

        self.cameraDisplay = QLabel()
        
        # Center the camera widget
        self.cameraDisplay.setAlignment(Qt.AlignCenter)

        # Create a self.layout and add widgets
        self.layout = QGridLayout()

        self.layout.addWidget(self.cameraDisplay, 0, 0, 4, 4) # row = 0, column = 0, rowSpan = 4, columnSpan = 4
        
        self.setLayout(self.layout)

        # Other variables
        self.timerUpdate = QTimer()
        self.frameWidth = self.cameraDisplay.width()
        self.frameHeight = self.cameraDisplay.height()
        print(f'W={self.frameWidth} - H={self.frameHeight}')
        self.start = time.time()
  

    def refreshGraph(self):
        """
        Method used to refresh the graph for the image display.
        """
        self.start2 = time.time()
        print(f'FPS={self.camera.get_frame_rate()}')
        print(f'T1 = {self.start2 - self.start} s')
        self.cameraRawArray = self.camera.get_image()

        AOIX, AOIY, AOIWidth, AOIHeight = self.camera.get_aoi()

        # On teste combien d'octets par pixel
        if(self.bytes_per_pixel >= 2):
            # on créée une nouvelle matrice en 16 bits / C'est celle-ci qui compte pour les graphiques temporelles et les histogrammes
            self.cameraRawFrame = self.cameraRawArray.view(np.uint16)
            self.cameraFrame = np.reshape(self.cameraRawFrame, (AOIHeight, AOIWidth, -1))
            
            # on génère une nouvelle matrice spécifique à l'affichage.
            cameraFrame8b = self.cameraFrame / (2**(self.nBitsPerPixel-8))
            self.cameraArray = cameraFrame8b.astype(np.uint8)    
        else:
            self.cameraRawFrame = self.cameraRawArray.view(np.uint8)
            self.cameraArray = self.cameraRawFrame

        # Resize the Qpixmap at the great size
        widgetWidth, widgetHeight = self.widgetGeometry()
        
        # On retaille si besoin à la taille de la fenètre
        self.cameraDisp = np.reshape(self.cameraArray, (AOIHeight, AOIWidth, -1))
        self.cameraDisp = cv2.resize(self.cameraDisp, dsize=(self.frameWidth, self.frameHeight), interpolation=cv2.INTER_CUBIC)
        
        # Convert the frame into an image
        image = QImage(self.cameraDisp, self.cameraDisp.shape[1], self.cameraDisp.shape[0], self.cameraDisp.shape[1], QImage.Format_Indexed8)
        pmap = QPixmap(image)

        # display it in the cameraDisplay
        self.cameraDisplay.setPixmap(pmap)

        # "plot" it in the cameraDisplay
        self.cameraDisplay.setPixmap(pmap)        
        self.start = time.time()
        print(f'Tref = {self.start - self.start2} s')

    def check_second_element(self, arr):
        # Check if the second element of each [a, b] pair is equal to 0
        return arr[:, :, 1] == 0
    
    def check_all_true(self, arr):
        # Check if all elements in the array are True
        return np.all(arr)

    def initListCamera(self):
        """
        Method used to initialize the different cameras linked to the computer.
        """
        self.nb_cam = camera.get_nb_of_cam()
        self.cameraInfo.setText('Cam Nb = '+str(self.nb_cam))
        if(self.nb_cam > 0):
            self.cameraList = camera.get_cam_list() 
            self.cameraListCombo.clear()
            for i in range(self.nb_cam):
                cam = self.cameraList[i]
                self.cameraListCombo.addItem(f'{cam[2]} (SN : {cam[1]})')

    def widgetGeometry(self):
        """
        Method use to get the width and the height of the widget.

        Returns:
            int: widget's width and height.
        """
        geometry = self.geometry()
        widgetWidth = geometry.width()
        widgetHeight = geometry.height()
        return widgetWidth, widgetHeight

    def connectCamera(self):
        """
        Method used to connect the camera.
        """
        self.selectedCamera = self.cameraListCombo.currentIndex()
        self.camera = camera.uEyeCamera(self.selectedCamera)
        
        self.max_width = int(self.camera.get_sensor_max_width())
        self.max_height = int(self.camera.get_sensor_max_height())
        
        self.camera.set_frame_rate(10)
        self.min_expo, self.max_expo = self.camera.get_exposure_range()
        self.camera.set_exposure(self.max_expo / 2)
        
        if self.colormode == "MONO8":
            self.m_nColorMode = ueye.IS_CM_MONO8
            self.camera.set_colormode(self.m_nColorMode)

        elif self.colormode == "MONO10":
            self.m_nColorMode = ueye.IS_CM_MONO10
            self.camera.set_colormode(self.m_nColorMode)

        elif self.colormode == "MONO12":
            self.m_nColorMode = ueye.IS_CM_MONO12
            self.camera.set_colormode(self.m_nColorMode)

        else:
            try : 
                self.m_nColorMode = ueye.IS_CM_MONO12
                self.camera.set_colormode(self.m_nColorMode)

            except :
                print("MONO 12 unavailable.")

                try : 
                    self.m_nColorMode = ueye.IS_CM_MONO10
                    self.camera.set_colormode(self.m_nColorMode)

                except : 
                    print("MONO 10 unavailable.")
                    self.camera.set_colormode(self.m_nColorMode)

                    try : 
                        self.m_nColorMode = ueye.IS_CM_MONO8
                        self.camera.set_colormode(self.m_nColorMode)

                    except : 
                        print("MONO 8 unavailable.")
                        print("Camera unavailable.")

        self.nBitsPerPixel = self.camera.nBitsPerPixel
        self.bytes_per_pixel = int(np.ceil(self.nBitsPerPixel / 8))
        print("nBitsPerPixel:\t", self.nBitsPerPixel)
        print("BytesPerPixel:\t", self.bytes_per_pixel)
        
        self.camera.set_aoi(0, 0, self.max_width-1, self.max_height-1)

        # There is a way to set the initial minimumValue of the exposure as near as possible from the original minimumValue of the
        # camera, for any camera

        self.setLayout(self.layout)
        
    def startVideo(self):
        self.camera.alloc()
        self.camera.capture_video()
        self.refreshGraph()
    
    def generateExpositionRangeList(self, pointsNumber):
        """
        Method used to create a list of pointsNumber points in the range of the camera's exposition.

        Args:
            nombrePoints (int): number of points possible in the range.

        Returns:
            list: list of points in the range of the camera's exposure.
        """
        (expositionRangeMinimum, expositionRangeMaximum) = self.camera.get_exposure_range()
        return np.linspace(expositionRangeMinimum+0.01, expositionRangeMaximum, pointsNumber) 

    def getFPSRange(self):
        """
        Method used to get the mininimum and maximum value of FPS.

        Returns:
            int: minimum and maximum values of FPS' range.
        """
        minTimePerFrame, maxTimePerFrame, timePerFrameIntervals = self.camera.get_frame_time_range()
        return int(1 / maxTimePerFrame) + 1, int(1 / minTimePerFrame) + 1

    def closeApp(self):
        """
        Method used to close the App.
        """
        self.close()
        self.closeEvent(None)

    def closeEvent(self, event):
        """
        Method used to close an event.

        Args:
            event (_???_): ???
        """
        if self.camera != None:
            self.camera.stop_camera()
        QApplication.quit()

    def getGraphValues(self):
        """
        Method used to return the value of 4 points near the center of the frame.

        Returns:
            list: list of the value of the four points.
        """
        height, width, depth = self.cameraFrame.shape
        value1 = self.cameraFrame[width // 2 + 10][height // 2]
        value2 = self.cameraFrame[width // 2 - 10][height // 2]
        value3 = self.cameraFrame[width // 2][height // 2 + 10]
        value4 = self.cameraFrame[width // 2][height // 2 - 10]
        return [value1, value2, value3, value4]

    def launchAOI(self, AOIX, AOIY, AOIWidth, AOIHeight, type = None):
        """
        Method used to launch the AOI.
        I know it is not optimised, but that avoid a bug where the image is in black when students are changing the setting
        values without being in AOI mode.
        """
        if not self.aoiTrueFalse and type == "forced":
            pass
        else:
            # Do Forced / Do Unforced / Undo AOI Mode

            # "Pause" refresh
            self.timerUpdate.stop()

            # Stop video and un_alloc memory # Merci M Villemejane
            self.camera.stop_video()
            self.camera.un_alloc()

            if self.aoiTrueFalse and type == "forced":

                # Setting the AOI
                self.camera.set_aoi(AOIX, AOIY, AOIWidth, AOIHeight)

            elif not self.aoiTrueFalse and type == None:

                # Setting the AOI
                self.camera.set_aoi(AOIX, AOIY, AOIWidth, AOIHeight)
                self.aoiTrueFalse = True 
                print("--- AOI Active ---") 

            elif self.aoiTrueFalse and type == None:

                # Stop AOI
                self.camera.set_aoi(0, 0, self.max_width, self.max_height)
                self.aoiTrueFalse = False 
                print("--- Whole Camera ---")
                
            # Re-alloc memory and re-run video
            self.camera.alloc()
            self.camera.capture_video()

            # Restart the refresh
            self.timerUpdate.setInterval(int(self.camera.get_frame_rate()))
            self.timerUpdate.start()


# -----------------------------------------------------------------------------------------------

class MyWindow(QMainWindow):
    def __init__(self, colormode="MONO8"):
        super().__init__()
        
        self.timerUpdate = QTimer()

        self.setWindowTitle("Camera Window")
        self.setGeometry(100, 100, 800, 600)
        
        self.centralWid = QWidget()
        self.layout = QGridLayout()
        
        '''Camera'''
        self.widget = CameraWidget(colormode=colormode)
        self.widget.connectCamera()
        start = time.time()
        self.widget.startVideo()
        self.widget.refreshGraph()
        self.layout.addWidget(self.widget, 0, 0)
        
        '''Frame Histo'''
        self.plotFrameHistWidget = PlotWidget(title='Frame Histo')  
        self.plotFrameHist = self.plotFrameHistWidget.plot([0])
        self.layout.addWidget(self.plotFrameHistWidget, 1, 0)
        
        '''Pixels Histo'''
        self.plotPixelsHistWidget = PlotWidget(title='Pixels Histo') 
        self.plotPixelsHist = self.plotPixelsHistWidget.plot([0])
        self.layout.addWidget(self.plotPixelsHistWidget, 1, 1)
        self.bins = np.array([])
        
        '''Pixels Chart'''
        self.pixelsArr = np.array([])
        self.plotPixelsTimeWidget = PlotWidget(title='Pixels Time Chart') 
        self.plotPixelsTime = self.plotPixelsTimeWidget.plot([0])
        self.layout.addWidget(self.plotPixelsTimeWidget, 0, 1)
        
        '''Global'''
        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)
        
        self.launchVideo()

    def create_chart(self):
        '''Global Camera Histogram'''
        max_bins = 2**int(self.widget.nBitsPerPixel)
        self.bins = np.linspace(0, max_bins, max_bins+1)
        hist, bins = np.histogram(self.widget.cameraRawFrame, bins=self.bins)
        print(self.widget.cameraRawFrame.shape)
        print(f'H0={hist[0]}')
        print(f'H1={hist[1]}')
        print(f'MIN_cam={np.min(self.widget.cameraRawFrame)}')
        print(f'MAX_cam={np.max(self.widget.cameraRawFrame)}')
        self.plotFrameHistWidget.removeItem(self.plotFrameHist)
        self.plotFrameHist = self.plotFrameHistWidget.plot(bins[:max_bins], hist)
        
        '''Pixel Time Chart'''
        # TO DO : only on 100 last values ??? - update X axis
        vals = self.widget.getGraphValues()
        self.pixelsArr = np.append(self.pixelsArr, vals)
        
        self.plotPixelsTimeWidget.removeItem(self.plotPixelsTime)
        self.plotPixelsTime = self.plotPixelsTimeWidget.plot(self.pixelsArr)
        
        '''Pixel Histo'''

    def launchVideo(self):
        """
        Method used to launch the video.
        """
        self.timerUpdate.setInterval(100)
        self.timerUpdate.timeout.connect(self.refreshApp)
        self.timerUpdate.start()  
        
    def refreshApp(self):
        self.widget.refresh_graph()
        self.create_chart()


#---------------
'''
TO DO 
----------
- Adding {Start / Stop / Reset} charts
- Time charts only on 100 last values
- Pixels Charts/Hist : select between the center pixel and 3 more random pixels
- Display pixels on the screen ?
- Adding {Save Histo / Charts / Image}
- Adding {Snap image and do analysis} -> New window ?

- Create Class and File for Charts and Histo !!!
'''

#-----------------------------------------------------------------------------------------------

# Launching as main for tests
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow("MONO12")
    main.show()
    sys.exit(app.exec_())
