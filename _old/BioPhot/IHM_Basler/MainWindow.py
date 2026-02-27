# Libraries to import
import sys
import os
import glob
from PIL import Image
import numpy as np
import cv2
import time

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QFileDialog, QPushButton
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QCursor
from widgets.CameraWidget import Camera_Widget
from widgets.SensorSettingsWidget import Sensor_Settings_Widget
from widgets.HardwareConnectionWidget import Hardware_Connection_Widget
from widgets.DMDSettingsWidget import DMD_Settings_Widget
from widgets.AutomaticModeWidget import Automatic_Mode_Widget
from widgets.PiezoControlWidget import Piezo_Control_Widget
from widgets.ModeWidget import Mode_Widget
from widgets.SaveToolbarWidget import Save_Widget

# -------------------------------------------------------------------------------------------------------

# Colors
"""
Colors :    Green  : #c5e0b4
            Blue   : #4472c4    ( 68, 114, 196)
             Light : #7fadff    (127, 173, 255)
            Orange : #c55a11    (197,  90,  17)
             Light : #ff8d3f    (255, 141,  63)
            Beige  : #fff2cc
            Grey1  : #f2f2f2
            Grey2  : #bfbfbf
"""


# -------------------------------------------------------------------------------------------------------

class Main_Widget(QWidget):
    """
    Main Widget of our Main Window.

    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    def __init__(self, mode="Automatic"):
        """
        Initialisation of the main Widget.
        """
        super().__init__()

        # Set some initialisation variables
        self.setStyleSheet("background: #f2f2f2;")
        self.mode = mode
        self.path = None
        self.scanFolderPath = os.path.expanduser( '~' )
        self.default_mires_path = '../MiresDMD/'

        # Create the several widgets for the MainWidget
        self.cameraWidget = Camera_Widget()
        self.sensorSettingsWidget = Sensor_Settings_Widget()
        self.hardwareConnectionWidget = Hardware_Connection_Widget()
        self.DMDSettingsWidget = DMD_Settings_Widget()
        self.automaticModeWidget = Automatic_Mode_Widget()
        self.piezoControlWidget = Piezo_Control_Widget()
        # Setting the move function in manual mode
        self.piezoControlWidget.updated.connect(lambda: self.movePiezo())

        # Create the several widgets for the Toolbar
        self.saveWidget = Save_Widget()

        # Setting the save function and directory between the saveButton and the cameraWidget
        self.saveWidget.directoryPushButton.clicked.connect(lambda: self.directory_save())
        self.saveWidget.savePushButton.clicked.connect(
            lambda: self.saveWidget.saveImage(self.cameraWidget.get_frame()))

        # Setting the save function and the folder function between the saveButton and the parameters window
        self.automaticModeWidget.parametersAutoModeWindow.directoryPushButton.clicked.connect(
            lambda: self.directory_save())
        self.automaticModeWidget.parametersAutoModeWindow.saveParametersPushButton.clicked.connect(
            lambda: self.saveParameters())

        # Setting the automatic start button 
        self.automaticModeWidget.startButton.clicked.connect(
            lambda: self.launchScan())

        '''
        # Setting a reset DMD button
        self.resetDMDPushButton = QPushButton("Reset DMD")
        self.resetDMDPushButton.clicked.connect(lambda: self.DMDSettingsWidget.resetDMD())

        # Setting the utilisation mode of the application and launching the next updates
        self.modeWidget.toggle.stateChanged.connect(lambda: self.changeMode())
        '''
        self.setMode()
        # Create and add the widgets into the layout
        layoutMain = QGridLayout()

        layoutMain.addWidget(self.cameraWidget, 0, 0, 4, 4)  # row = 0, column = 0, rowSpan = 4, columnSpan = 4
        layoutMain.addWidget(self.sensorSettingsWidget, 4, 0, 3, 4)  # row = 4, column = 0, rowSpan = 3, columnSpan = 4
        layoutMain.addWidget(self.hardwareConnectionWidget, 0, 5, 1,
                             4)  # row = 0, column = 5, rowSpan = 1, columnSpan = 4
        layoutMain.addWidget(self.DMDSettingsWidget, 1, 5, 2, 4)  # row = 1, column = 5, rowSpan = 2, columnSpan = 4
        layoutMain.addWidget(self.automaticModeWidget, 3, 5, 1, 4)  # row = 3, column = 5, rowSpan = 1, columnSpan = 4
        layoutMain.addWidget(self.piezoControlWidget, 4, 5, 3, 4)  # row = 4, column = 5, rowSpan = 3, columnSpan = 4

        self.setLayout(layoutMain)

        self.cameraWidget.connectCamera()
        self.initSettings()
        self.cameraWidget.launchVideo()
        self.timer = QTimer(self)

        # Internal parameters / automatic mode
        self.z_init = 0
        self.z_final = 0
        self.z_step = 0
        self.zs_list = []
        self.cam_expo = 0
        self.cam_FPS = 0
        self.cam_blacklevel = 0
        self.patterns = []

        # automatic mode progression parameters
        self.scan_index = 0
        self.mire_index = 0

    # General methods used by the interface
    def initSettings(self):
        """
        Method used to setup the settings.
        """
        # Initialisation of the FPS setting
        minFPS, maxFPS = self.cameraWidget.getFPSRange()
        self.sensorSettingsWidget.FPS.slider.setMinimum(minFPS)
        self.sensorSettingsWidget.FPS.slider.setMaximum(maxFPS)
        self.sensorSettingsWidget.FPS.slider.setValue(maxFPS)
        self.cameraWidget.camera.set_frame_rate(self.sensorSettingsWidget.FPS.getValue())

        self.sensorSettingsWidget.FPS.slider.valueChanged.connect(
            lambda: self.cameraWidget.camera.set_frame_rate(self.sensorSettingsWidget.FPS.getValue()))
        self.sensorSettingsWidget.FPS.setValue(self.sensorSettingsWidget.FPS.getValue())

        # Initialisation of the exposure setting (in ms but given in us by Basler methods)
        self.sensorSettingsWidget.exposureTime.floatListToSelect = self.cameraWidget.generateExpositionRangeList(1000)

        self.sensorSettingsWidget.exposureTime.slider.setRange(1, 1000)
        self.sensorSettingsWidget.exposureTime.setValue(200)

        self.sensorSettingsWidget.exposureTime.slider.valueChanged.connect(
            lambda: self.cameraWidget.camera.set_exposure(self.sensorSettingsWidget.exposureTime.value * 1000))

        self.cameraWidget.camera.set_exposure(200*1000)

        # Initialisation of the BlackLevel setting
        # TO ADAPT TO THE BITS SIZE OF THE CAMERA
        self.sensorSettingsWidget.blackLevel.slider.setMinimum(0)
        self.sensorSettingsWidget.blackLevel.slider.setMaximum(4095)
        self.sensorSettingsWidget.blackLevel.setValue(
            int(self.cameraWidget.camera.get_black_level()))  # camera's blacklevel

        self.sensorSettingsWidget.blackLevel.slider.valueChanged.connect(
            lambda: self.cameraWidget.camera.set_black_level(self.sensorSettingsWidget.blackLevel.getValue()))

    def setMode(self):
        """
        Method used to set the utilization mode of the application.
        """
        if self.mode == "Manual":
            self.sensorSettingsWidget.setEnabled(True)
            self.hardwareConnectionWidget.setEnabled(True)
            self.DMDSettingsWidget.setEnabled(True)
            self.automaticModeWidget.setEnabled(True)  # False ??
            self.piezoControlWidget.setEnabled(True)
            self.cameraWidget.setColor("blue")
            self.saveWidget.setMode(self.mode)
            self.automaticModeWidget.parametersAutoModeWindow.setEnabled(True)  # False ??
            self.DMDSettingsWidget.patternChoiceWindowWidget1.setEnabled(True)
            self.DMDSettingsWidget.patternChoiceWindowWidget2.setEnabled(True)
            self.DMDSettingsWidget.patternChoiceWindowWidget3.setEnabled(True)
            # self.resetDMDPushButton.setStyleSheet("background: #ff8d3f; color: black; border-width: 1px;")
        elif self.mode == "Automatic":
            self.sensorSettingsWidget.setEnabled(False)
            self.hardwareConnectionWidget.setEnabled(False)
            self.DMDSettingsWidget.setEnabled(False)
            self.automaticModeWidget.setEnabled(True)
            self.piezoControlWidget.setEnabled(False)
            self.cameraWidget.setColor("blue")
            self.saveWidget.setMode(self.mode)
            self.automaticModeWidget.parametersAutoModeWindow.setEnabled(True)
            self.DMDSettingsWidget.patternChoiceWindowWidget1.setEnabled(False)
            self.DMDSettingsWidget.patternChoiceWindowWidget2.setEnabled(False)
            self.DMDSettingsWidget.patternChoiceWindowWidget3.setEnabled(False)
            # self.resetDMDPushButton.setStyleSheet("background: #7fadff; color: black; border-width: 1px;")

    def changeMode(self):
        """
        Method used to change the utilisation mode of the application.
        """
        if self.mode == "Automatic":
            self.mode = "Manual"
            self.setMode()

        elif self.mode == "Manual":
            self.mode = "Automatic"
            self.setMode()

    # Methods less used by the interface
    def movePiezo(self):
        """
        Method used to move the piezo in manual mode.
        """
        if self.hardwareConnectionWidget.piezoConnected:
            value = self.piezoControlWidget.get_value()
            value_um = int(value)
            value_nm = int((value-value_um)*1000)
            self.hardwareConnectionWidget.piezo.movePosition(value_um, value_nm)

    def directory_save(self):
        """
        Method used to select a directory to save the parameters and the images into.
        """
        dialog = QFileDialog()
        dialog.setDirectory(self.scanFolderPath)
        self.path = dialog.getExistingDirectory(None, "Select Folder")
        self.saveWidget.path = self.path
        self.automaticModeWidget.parametersAutoModeWindow.path = self.path
        self.saveWidget.directoryPushButton.setText('Directory : ' + self.getSmallText())
        self.automaticModeWidget.parametersAutoModeWindow.directoryPushButton.setText(
            'Directory : ' + self.getSmallText())

    def getSmallText(self):
        """
        Method used to show the directory where the pictures are saved.

        Returns:
            str: the string that must be on the directory push button.
        """
        if self.path == None or self.path == '':
            return 'Here'

            # Split the string by '/'
        end = self.path.split('/')
        # Return the last part of the split
        return end[-1]

    # Method used to launch the scan and its sub-methods
    def launchScan(self):
        """
        Method used to scan in automatic mode.
        """
        # Read the parameters and get the Z Displacement and the Z Step
        try:
            parameters = self.readParameters()
        except FileNotFoundError:
            return print("'parameters.txt' required : use 'Parameters' button in 'Automatic Mode'")
        except ValueError:
            return print("Some values in 'parameters.txt' are not correct.\nAcquisition impossible.")

        if not self.hardwareConnectionWidget.piezo.isConnected():
            self.hardwareConnectionWidget.connection()
            if not self.hardwareConnectionWidget.piezo.isConnected():
                return print("The HardWare for the Piezo is not connected : you must connect it first.")

        self.z_init, self.z_final, self.z_step = parameters['Z Init'], parameters['Z Final'], parameters['Z Step']

        # Set the camera with the values of the parameter file
        self.cam_expo = parameters['Exposure time']
        self.cam_FPS = parameters['FPS']
        self.cam_blacklevel = parameters['BlackLevel']
        print(f'Expo Time = {self.cam_expo}')
        self.sensorSettingsWidget.exposureTime.setValue(int(self.cam_expo))
        self.sensorSettingsWidget.FPS.setValue(self.cam_FPS)

        # Take the list of the Zs
        self.zs_list = self.calculateZs(self.z_init, self.z_final, self.z_step)

        # Create a folder to save the scans
        scan_dir = self.createScanFolder()

        self.patterns = parameters['Patterns']
        print(self.patterns)

        self.mode = "Automatic"
        self.setMode()
        self.scan_index = 0
        self.mire_index = 0
        self.automaticModeWidget.progressionBar.setValue(0)

        self.timer.setInterval(2500)
        self.timer.timeout.connect(self.update_scan_data)
        self.timer.start()


    def saveParameters(self):
        """
        Method used to save the data into the right folder.
        """
        if self.path is None:
            filename = "parameters.txt"
        else:
            filename = self.path + "/parameters.txt"

        # Intern save
        self.z_init = self.automaticModeWidget.parametersAutoModeWindow.z_init.get_real_value()
        self.z_final = self.automaticModeWidget.parametersAutoModeWindow.z_final.get_real_value()
        if self.z_init > self.z_final:
            self.z_final, self.z_init = self.z_init, self.z_final
        self.z_step = self.automaticModeWidget.parametersAutoModeWindow.z_step.get_real_value()

        self.cam_expo = self.sensorSettingsWidget.exposureTime.value
        self.cam_FPS = self.sensorSettingsWidget.FPS.getValue()
        self.cam_blacklevel = self.sensorSettingsWidget.blackLevel.getValue()
        self.patterns = [self.DMDSettingsWidget.patternChoiceWindowWidget1.path,
                         self.DMDSettingsWidget.patternChoiceWindowWidget2.path,
                         self.DMDSettingsWidget.patternChoiceWindowWidget3.path]

        # File save
        with open(filename, "w") as file:
            file.write(
                f"Z Init (um) = {self.z_init}\n")
            file.write(
                f"Z Final (um) = {self.z_final}\n")
            file.write(f"Z Step (nm) = {self.z_step}\n")
            file.write("\n")
            file.write("Camera settings :\n")
            file.write(f"Exposure time = {self.cam_expo}\n")
            file.write(f"FPS = {self.cam_FPS}\n")
            file.write(f"BlackLevel = {self.cam_blacklevel}\n")
            file.write("\n")
            file.write("Patterns loaded :\n")
            file.write(f"Pattern 1 = {self.patterns[0]}\n")
            file.write(f"Pattern 2 = {self.patterns[1]}\n")
            file.write(f"Pattern 3 = {self.patterns[2]}\n")

        self.automaticModeWidget.parametersAutoModeWindow.hide()

    def readParameters(self):
        """
        A method used to read the different parameters.

        Args:
            file_path (str): path to the parameters file.

        Returns:
            dict: dictionary of parameters.
        """
        parameters = {'Patterns': []}
        if self.path is None or self.path == "":
            file_path = "parameters.txt"
        else:
            file_path = self.path + "/parameters.txt"

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('Z Init'):
                    z_init = float(line.split('=')[1].strip())
                    parameters['Z Init'] = z_init
                elif line.startswith('Z Final'):
                    z_final = float(line.split('=')[1].strip())
                    parameters['Z Final'] = z_final
                elif line.startswith('Z Step'):
                    z_step = float(line.split('=')[1].strip())
                    parameters['Z Step'] = z_step
                elif line.startswith('Exposure time'):
                    exposure_time = float(line.split('=')[1].strip())
                    parameters['Exposure time'] = exposure_time
                elif line.startswith('FPS'):
                    fps = int(line.split('=')[1].strip())
                    parameters['FPS'] = fps
                elif line.startswith('BlackLevel'):
                    black_level = int(line.split('=')[1].strip())
                    parameters['BlackLevel'] = black_level
                elif line.startswith('Pattern '):
                    pattern_parts = line.split('=')
                    pattern_number = int(pattern_parts[0].split()[-1])
                    pattern_path = pattern_parts[1].strip()
                    parameters['Patterns'].append({'Pattern Number': pattern_number, 'Pattern Path': pattern_path})
        return parameters

    def calculateZs(self, z_init, z_final, z_step):
        """
        A method used to set up the different values that will set the piezo.

        Args:
            z_init (float): Z Init in um.
            z_final (float) : Z Final in um.
            z_step (float): Z Step in nm.

        Returns:
            list of tuples: list of the Z Displacement and Z Step in um and nm.
        """
        zs_axis = []
        fine_zs = []
        current_z = z_init

        while current_z < z_final:
            z_axis = int(current_z)
            fine_z = int((current_z - z_axis) * 1000)
            zs_axis.append(z_axis)
            fine_zs.append(fine_z)

            current_z += z_step * 10 ** -3

            '''
            if current_z > z_final:
                z_axis = int(z_displacement)
                fine_z = int((z_displacement - z_axis) * 1000)
                zs_axis.append(z_axis)
                fine_zs.append(fine_z)
                break
            '''

        combined_zs = [[zs_axis[i], fine_zs[i]] for i in range(len(zs_axis) - 1)]
        return combined_zs

    def createScanFolder(self):
        """
        Method used to create a new folder to save our scans.
        """
        if self.path is None or self.path == "":
            self.path = os.getcwd()
            self.saveWidget.directoryPushButton.setText('Directory : ' + self.getSmallText())
            self.automaticModeWidget.parametersAutoModeWindow.directoryPushButton.setText(
                'Directory : ' + self.getSmallText())

        base_foldername = self.path + "/Scan_"
        print(base_foldername)

        scan_number = 1

        while os.path.exists(f"{base_foldername}{scan_number}"):
            scan_number += 1

        self.scanFolderPath = f"{base_foldername}{scan_number}"
        os.makedirs(self.scanFolderPath)
        return self.scanFolderPath

    def saveImage(self, pattern_number, index):
        """
        Method used to save an array in .tiff in a folder with an incrementing filename.

        Args:
            patternNumber (int): Pattern number for the image.
        """
        # Set the beginningFilename according to the path set by the directory method
        beginning_filename = self.scanFolderPath + '\Snap_*_*.tiff'

        # Get the number of existing image files in the folder
        image_files = glob.glob(os.path.join(self.scanFolderPath, beginning_filename))
        num_images = len(image_files)

        # Format the image file name
        image_filename = f"Snap_{index:02d}_{pattern_number}.tiff"

        # Create a PIL Image object from the array
        image_array = self.cameraWidget.get_frame()

        # Set the endingFilename according to the path set by the directory method
        if self.path is None or self.path == '':
            ending_filename = image_filename
        else:
            ending_filename = os.path.join(self.scanFolderPath, image_filename)

        # Save the image as a TIFF file
        cv2.imwrite(ending_filename, image_array)

        print(f"Array saved as : {ending_filename}\n")

    def update_scan_data(self):
        """
        Method used to update data of an entire scan
        """
        if self.mode == "Automatic":
            if self.scan_index < len(self.zs_list):
                z_um, z_nm = self.zs_list[self.scan_index]
                print(f'UM= {z_um} / NM = {z_nm}')
                self.hardwareConnectionWidget.piezo.movePosition(z_um, z_nm)

                actual_pattern = self.patterns[self.mire_index]
                actual_pattern_path = actual_pattern['Pattern Path']
                self.DMDSettingsWidget.PatternLoad(actual_pattern_path)
                time.sleep(1.2)
                self.cameraWidget.refreshGraph()
                self.saveImage(self.mire_index, self.scan_index)

                self.mire_index += 1
                if self.mire_index == 3:
                    self.mire_index = 0
                    self.scan_index += 1

                # Update progression bar
                progression = 100 * (self.scan_index*3 + self.mire_index) // (3*len(self.zs_list))
                self.automaticModeWidget.progressionBar.setValue(progression)

            else:
                self.mode = "Manual"
                self.setMode()
                self.timer.stop()

                '''
                # COPY parameters.txt to SCAN_XX/parameters.txt
                if self.path is None:
                    filename = "parameters.txt"
                    destination_name = scan_dir + '/' + "parameters.txt"
                else:
                    filename = self.path + "/parameters.txt"
                    destination_name = self.path + scan_dir + '/' + "parameters.txt"
                # os.system('copy '+filename+' '+destination_name)
                '''

    def wheelEvent(self,event):
        mouse_point = QCursor().pos()
        print(f'Xm={mouse_point.x()} / Ym={mouse_point.y()}')
        numPixels = event.pixelDelta();
        numDegrees = event.angleDelta() / 8;
        print(f'X={numPixels.x()} / Y={numPixels.y()}')
        print(numDegrees)

# -------------------------------------------------------------------------------------------------------

class Main_Window(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self, mode="Manual"):
        """
        Initialisation of the main Window.
        """
        super(Main_Window, self).__init__()

        # Variable
        self.mode = mode

        # Define Window title and logo
        self.setWindowTitle("TP : Microscope à illumination structurée")
        self.setWindowIcon(QIcon("./images/IOGSLogo.jpg"))
        tl, bl, tr, br = self.screen().availableGeometry().getCoords() # QRect
        self.setGeometry(5, bl+30, tr-5, br-50)

        # Set the widget as the central widget of the window
        self.mainWidget = Main_Widget(mode=self.mode)
        self.setCentralWidget(self.mainWidget)

        # Creating the toolbar
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.setStyleSheet("background-color: #bfbfbf; border-radius: 10px; border-width: 1px;"
                                   "border-color: black; padding: 6px; font: bold 12px; color: white;"
                                   "text-align: center; border-style: solid;")

        # Connecting the modeWidget to the Toolbar
        self.setMode()
        # self.mainWidget.modeWidget.toggle.stateChanged.connect(lambda: self.setMode())

        # Adding Widgets to the Toolbar
        self.toolbar.addWidget(self.mainWidget.saveWidget)
        # self.toolbar.addWidget(self.mainWidget.resetDMDPushButton)

        self.show()


    def setMode(self):
        """
        Method used to set the utilization mode of the application.
        """
        if self.mainWidget.mode == "Manual":
            self.toolbar.setStyleSheet("background-color: #c55a11; border-radius: 10px; border-width: 2px;"
                                       "border-color: black; padding: 6px; font: bold 12px; color: white;"
                                       "text-align: center; border-style: solid;")

        elif self.mainWidget.mode == "Automatic":
            self.toolbar.setStyleSheet("background-color: #4472c4; border-radius: 10px; border-width: 2px;"
                                       "border-color: black; padding: 6px; font: bold 12px; color: white;"
                                       "text-align: center; border-style: solid;")


# -------------------------------------------------------------------------------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Main_Window()
    window.show()

    sys.exit(app.exec())
