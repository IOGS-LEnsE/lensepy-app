import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports


class NucleoWrapper:
    """Class for controlling piezoelectric motion system,
	using an interface of type Nucleo-G431KB.

    This class uses PySerial library to communicate with Nucleo board.
	The baudrate is 115200 bds.

	Protocol :
 		!T:val? --> !T;		Send Sampling Period to sample data - integer in ms
 		!D?		--> !D:v_a:v_b:v_c:v_ab:v_ac:v_abc;
 											Get data
 		!V?		--> !V:val;		Version of the Hardware
 		others 	-->	!E;		Error detected in transmission
    """

    def __init__(self, baudrate=115200):
        """
        Initialize a piezo system
		"""
        self.connected = False
        self.serial_com = None
        self.baudrate = baudrate
        self.serial_link = None
        self.com_list = None
        self.read_bytes = None

    def list_serial_hardware(self):
        com_list = serial.tools.list_ports.comports()
        self.com_list = []
        for p in com_list:
            info = {
                "device": p.device,
                "description": p.description,
                "manufacturer": p.manufacturer
            }
            if info['manufacturer'].startswith('STM'):
                self.com_list.append(info)
        return self.com_list

    def set_serial_com(self, value):
        """
        Set the serial port number.
        :param value: number of the communication port - COMxx for windows
        """
        self.serial_com = value

    def connect(self):
        """
        Connect to the hardware interface via a Serial connection
        :return:    True if connection is done, else False.
		"""
        if not self.connected:
            if self.serial_com is not None:
                try:
                    self.serial_link = serial.Serial(self.serial_com, baudrate=self.baudrate)
                    self.connected = True
                    return True
                except:
                    print('Cant connect')
                    self.connected = False
                    return False
        return False

    def _read_data(self, end_char=';'):
        """Read serial data until a specific character."""
        received_data = ""
        while True:
            byte = self.serial_link.read(1).decode('ascii')
            if byte == end_char:  # Check if byte is ending character
                break
            received_data += byte
        return received_data

    def stop_acq(self):
        """Stop acquisition."""
        if self.connected:
            try:
                self.serial_link.write(b'!S?')
            except:
                print('Error Sending')
        return False

    def is_connected(self):
        """
        Return if the hardware is connected.
        :return:    True if connection is done, else False.
        """
        if self.connected:
            try:
                self.serial_link.write(b'!V?')
            except:
                print('Error Sending')
            self.read_bytes = self._read_data()
            if self.read_bytes[1] == 'V':
                return True
            else:
                return False
        return False

    def disconnect(self):
        if self.connected:
            if self.is_connected():
                try:
                    self.serial_link.close()
                    self.connected = False
                    return True
                except:
                    print("Cant disconnect")
                    return False
        return False

    def get_hw_version(self, timeout=10):
        """
        Get hardware version.
        :param timeout: timeout in milliseconds.
        :return:    Hardware version.
        """
        if self.connected:
            try:
                self.serial_link.write(b'!V?')
            except:
                print('Error Sending - HW Version')
            # Timeout
            for k in range(timeout):
                if self.serial_link.in_waiting > 1:
                    self.read_bytes = self._read_data().split(':')[1]
                    return self.read_bytes
                else:
                    time.sleep(0.001)
        return -1

    def set_sampling_period(self, period, timeout=10):
        """
        Set the sampling period.
        :param period: sampling period in milliseconds.
        :param timeout: timeout in milliseconds.
        """
        s_data = f'!T:{period}?'
        try:
            self.serial_link.write(bytes(s_data, 'ascii'))
        except:
            print('Error Sending - Sampling period')
        # Timeout
        for k in range(timeout):
            if self.serial_link.in_waiting > 1:
                self.read_bytes = self._read_data().split(':')[1]
                return self.read_bytes
            else:
                time.sleep(0.001)
        return -1

    def get_data(self, timeout=10):
        """
        Get hardware version.
        :param timeout: timeout in milliseconds.
        :return:    Hardware version.
        """
        if self.connected:
            try:
                self.serial_link.write(b'!D?')
            except:
                print('Error Sending - Getting data')
            # Timeout
            for k in range(timeout):
                if self.serial_link.in_waiting > 1:
                    self.read_bytes = self._read_data().split(':')
                    self.read_bytes.pop(0)
                    return self.read_bytes
                else:
                    time.sleep(0.001)
        return None


if __name__ == "__main__":
    # Test Nucleo
    nucleo_wrapper = NucleoWrapper()
    comList = nucleo_wrapper.list_serial_hardware()
    print(comList)
    if len(comList) > 0:
        com_selected = 'COM' + input('COM ?')
        nucleo_wrapper.set_serial_com(com_selected)
        nucleo_wrapper.connect()

        if nucleo_wrapper.is_connected():
            print(f'Nucleo / HW V.{nucleo_wrapper.get_hw_version()}')
            print(f'Nucleo / Set S Period {nucleo_wrapper.set_sampling_period(100)}')
            data = nucleo_wrapper.get_data(timeout=100)
            print(data)
