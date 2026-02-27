

"""
Example KPC101_pythonnet.py
Example Date of Creation: 2024-04-17
Example Date of Last Modification on Github: 2024-04-17
Version of Python used for Testing: 3.9
==================
Example Description: This example controls the KPC101 in open and closed loop
"""
import os
import time
import sys
import clr
import numpy as np


clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericPiezoCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoStrainGaugeCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericPiezoCLI import *
from Thorlabs.MotionControl.KCube.PiezoStrainGaugeCLI import *
from System import Decimal  # necessary for real world units

class control_piezo:

    def __init__(self):
        DeviceManagerCLI.BuildDeviceList()
        # create new device
        self.serial_no = "113250597"  # Replace this line with your device's serial number
        print(self.serial_no)
        # Connect, begin polling, and enable
        self.device = KCubePiezoStrainGauge.CreateKCubePiezoStrainGauge(self.serial_no)

        self.device.Connect(self.serial_no)
        print(self.device)
        # Get Device Information and display description
        device_info = self.device.GetDeviceInfo()
        print(device_info.Description)

        # Start polling and enable
        self.device.StartPolling(250)  #250ms polling rate
        time.sleep(0.25)
        self.device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        # Load the device configuration
        device_config = self.device.GetPiezoConfiguration(self.serial_no)

        # This shows how to obtain the device settings
        device_settings = self.device.PiezoDeviceSettings

        # Set the Zero point of the device
        print("Setting Zero Point")
        self.device.SetZero()
        time.sleep(5)

    def set_zero(self):
        print("Setting Zero Point")
        self.device.SetZero()
        time.sleep(5)
    def GoToDistance(self, consigne):
        # consigne en um
        mode = self.device.GetPositionControlMode()
        # Closed loop control
        self.device.SetPositionControlMode(mode.CloseLoop)
        # Get the maximum voltage output of the KPZ
        max_travel = self.device.GetMaxTravel()  # This is stored as a .NET decimal

        # Go to a voltage
        dev_travel = Decimal(float(consigne))
        print(f'Going to {dev_travel}um')

        if dev_travel > Decimal(0) and dev_travel <= max_travel:
            self.device.SetPosition(dev_travel)
            time.sleep(0.5)

            print(f'Moved to Position: {self.device.GetPosition()}um')
        else:
            print(f'Voltage must be between 0 and {max_travel}')

    def close(self):
        # Stop Polling and Disconnect
        self.device.StopPolling()
        self.device.Disconnect()

