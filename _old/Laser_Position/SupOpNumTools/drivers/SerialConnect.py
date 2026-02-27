# -*- coding: utf-8 -*-
"""
Hardware serial connection to a STMicroelectronics Nucleo board.

----------------------------------------------------------------------------
Co-Author : Julien VILLEMEJANE
Laboratoire d Enseignement Experimental - Institut d Optique Graduate School
Version : 1.0 - 2023-08-31
"""

import serial
import serial.tools.list_ports

class SerialConnect:
    """
    Class for control hardware interface
    Based on STM Nucleo L476RG

    """

    def __init__(self, baudrate=115200):
        """
        Initialization of the serial connection object

        Args:
            baudrate: int
                Value of the data transmission baudrate

        Returns:
            Nothing
        """
        self.selected_port = None
        self.serial_link = None
        self.baudrate = baudrate
        self.port_list = None

    def get_serial_port_list(self):
        """
        Get a list of available serial ports (STM board connected)
        Returns:

        """
        self.port_list = serial.tools.list_ports.grep('STM', include_links=False)
        #self.port_list = serial.tools.list_ports.comports(include_links=False)
        return self.port_list

    def print_serial_port_list(self):
        """
        Display a list of available serial ports (STM board connected)

        Returns:
            List of serial ports in the Python shell
        """
        print('List of available ports / STMicroelectronics')
        for port in self.port_list:
            print(f'\t{port.device} | {port.description}')

    def set_serial_port(self, port):
        """
        Set the serial port to use

        Args:
            port: string
                Name of the serial port to use
                COMxx on windows
                /dev/ttyXX on Linux / Mac OS
        """
        self.selected_port = port

    def connect(self):
        """

        Returns:
            True if connection is established
            False if not
        """
        if self.selected_port is not None and self.serial_link is None:
            self.serial_link = serial.Serial(self.selected_port, self.baudrate)
            return True
        else:
            if self.selected_port is None :
                print('Port name is not valid or not set')
            else:
                print('Serial Port already set up')
            return False

    def disconnect(self):
        """
        Delete the serial link

        Returns:
            True if serial link is disconnected
            False if not
        """
        if self.serial_link is not None:
            if self.serial_link.isOpen():
                self.serial_link.close()
            self.serial_link = None
            return True
        else:
            print('No Connection to disconnect')
            return False

    def get_baudrate(self):
        """
        Get the baudrate of the transmission

        Returns:
            baudrate : int
                baudrate of the data transmission (in bds)
        """
        return self.baudrate

    def set_baudrate(self, bd):
        """
        Set the baudrate of the transmission

        Args:
            bd: int
                baudrate of the data transmission (in bds)

        Returns:
            Nothing
        """
        self.baudrate = bd

    def open_serial(self):
        """
        Open the communication between the interface and the hardware

        Returns:
            True if the communication is established
            False if not
        """
        if self.serial_link is not None and self.serial_link.isOpen() is False:
            self.serial_link.open()
            return True
        elif self.serial_link.isOpen() :
            return True
        else :
            return False

    def is_serial_open(self):
        """
        Check if the serial port is open

        Returns:
            True if the port is open
            False if not
        """
        return self.serial_link.isOpen()

    def is_data_waiting(self):
        """
        Get the state of the serial buffer

        Returns:
            True if data are ready
            False if not
        """
        if self.serial_link.isOpen():
            number = self.serial_link.inWaiting()
            if number == 0:
                return False
            else:
                return True
        else:
            return False

    def get_nb_data_waiting(self):
        """
        Get the number of data in the serial buffer

        Returns:
            integer corresponding to the amount of bytes in the serial buffer
        """
        if self.is_data_waiting():
            return self.serial_link.inWaiting()
        else:
            return 0

    def send_data(self, data):
        """
        Send data to the serial port

        Args:
            data: str
                string (or bytes) to send

        Returns:
            True if data are sent
            False if not
        """
        if self.serial_link.isOpen():
            data_to_send = data + '\r\n'
            data_bytes = bytes(data_to_send, 'ascii')
            self.serial_link.write(data_bytes)
            return True
        else:
            return False

    def read_data(self, nb):
        return self.serial_link.read(nb)


# Launching as main for tests
if __name__ == "__main__":
    # Create an object of type SerialConnect
    my_serial = SerialConnect()
    # Get a list of available serial ports (STM board only connected on USB)
    serial_port_list = my_serial.get_serial_port_list()
    # Print the list
    my_serial.print_serial_port_list()

    port_av = input('Enter the name of the port (COMxx) : ')
    #
    my_serial.set_serial_port(port_av)
    # Setup the selected serial port
    print(my_serial.connect())

    # Open the serial communication
    print(f'Serial is open ? {my_serial.is_serial_open()}')

    # Test if data are waiting in the serial buffer
    number_data = my_serial.is_data_waiting()
    if number_data:
        print(f'Data are ready')
    else:
        print(f'No data')

    # Check if the board is connected and still alive...
    print(f'Connection is OK ? {my_serial.check_connection()}')

    # Unlink the serial port (and close if necessary)
    my_serial.disconnect()