# -*- coding: utf-8 -*-
"""
2D Laser Position Control with PID controller.

Control with Nucleo L476RG

----------------------------------------------------------------------------
Co-Author : Julien VILLEMEJANE
Laboratoire d Enseignement Experimental - Institut d Optique Graduate School
Version : 1.0 - 2023-07-24
"""

import time
import numpy

from SupOpNumTools.drivers.SerialConnect import SerialConnect


class LaserPID:
    """
    Class for Laser PID Control hardware interface
    Based on STM Nucleo L476RG

    List of commands
    ----------------
        Stop / Init
            O_!\r\n
            No return

        Alignment position
            A_!\r\n
            A_Xvalue_Yvalue_!\r\n   Xvalue and Yvalue are double values  (x2 for each channel)

        Servomotor position
            M_Xpos_Ypos_!\r\n

    """

    def __init__(self, baudrate=115200):
        """

        Args:
            baudrate:
        """
        self.hardware_connection = SerialConnect(baudrate)
        self.connected = False
        self.serial_port = None
        self.scan_x = 0
        self.scan_y = 0
        self.phd_x = 0
        self.phd_y = 0
        self.sampling_freq = 10000
        self.samples = 100
        # Scanner limits for step response
        self.x_limit_min = 0
        self.x_limit_max = 0
        self.y_limit_min = 0
        self.y_limit_max = 0
        # Step Response
        self.x_data = None      # Array of data for step response
        self.y_data = None      # Array of data for step response
        self.step_data = None   # Array of data for step response
        self.step_acq = False   # Acquisition in process
        # PID parameters
        self.K_X = 0
        self.K_Y = 0
        self.I_X = 0
        self.I_Y = 0
        self.D_X = 0
        self.D_Y = 0

    def set_serial_port(self, value):
        self.serial_port = value
        self.hardware_connection.set_serial_port(self.serial_port)

    def get_serial_ports_list(self):
        return self.hardware_connection.get_serial_port_list()

    def connect_to_hardware(self):
        self.connected = self.hardware_connection.connect()
        return self.connected

    def disconnect_hardware(self):
        self.hardware_connection.disconnect()
        self.connected = False
        return self.connected

    def is_connected(self):
        return self.connected

    def is_data_waiting(self):
        return self.hardware_connection.is_data_waiting()

    def clear_buffer(self):
        if self.is_data_waiting():
            nb_data = self.hardware_connection.get_nb_data_waiting()
            data = self.hardware_connection.read_data(nb_data)
            print(f'ERASED DATA = {data}')
        else:
            print('Nothing to clear')

    def get_phd_xy(self):
        self.hardware_connection.send_data('A_!')
        while self.hardware_connection.is_data_waiting() is False:
            pass
        nb_data = self.hardware_connection.get_nb_data_waiting()
        data = self.hardware_connection.read_data(nb_data).decode('ascii')
        data_split = data.split('_')
        if len(data_split) == 4:
            self.phd_x = float(data_split[1])
            self.phd_y = float(data_split[2])
        else:
            self.phd_x = None
            self.phd_y = None
        return self.phd_x, self.phd_y

    def set_scan_xy(self, x, y):
        self.scan_x = x
        self.scan_y = y
        data = 'M_' + str(x) + '_' + str(y) + '_!'
        self.hardware_connection.send_data(data)
        timeout_value = 0
        while timeout_value < 10 and self.hardware_connection.is_data_waiting() is False:
            timeout_value += 1
            time.sleep(0.01)
        if timeout_value == 10:
            print('TimeOut Scan')
            return None, None
        else:
            nb_data = self.hardware_connection.get_nb_data_waiting()
            data = self.hardware_connection.read_data(nb_data).decode('ascii')
            data_split = data.split('_')
            if len(data_split) == 6:
                self.phd_x = float(data_split[3])
                self.phd_y = float(data_split[4])
            else:
                self.phd_x = None
                self.phd_y = None
            return self.phd_x, self.phd_y

    def get_scan_xy(self):
        return self.scan_x, self.scan_y

    def get_sampling_freq(self):
        return self.sampling_freq

    def set_sampling_freq(self, fs):
        self.sampling_freq = fs

    def set_open_loop_steps(self, x1, y1, x2, y2):
        self.x_limit_min = x1
        self.x_limit_max = x2
        self.y_limit_min = y1
        self.y_limit_max = y2

    def set_open_loop_samples(self, n):
        # Not yet implemented in Hardware
        self.samples = n

    def get_open_loop_samples(self):
        return self.samples

    def start_open_loop_step(self, fs, ns):
        self.sampling_freq = fs
        self.samples = ns
        self.step_acq = True
        data = 'S_'+str(self.x_limit_min)+'_'+str(self.x_limit_max)+'_'
        data += str(self.y_limit_min)+'_'+str(self.y_limit_max)+'_'
        data += str(self.sampling_freq)+'_'+str(self.samples)+'_!'
        self.hardware_connection.send_data(data)
        # Acknowledgment waiting
        timeout_value = 0
        while timeout_value < 100 and self.hardware_connection.is_data_waiting() is False:
            timeout_value += 1
            time.sleep(0.01)
        if timeout_value == 100:
            print('TimeOut Step')
            return False
        else:
            data = self.hardware_connection.read_data(self.hardware_connection.get_nb_data_waiting())
            data = data.decode('ascii')
            if len(data) == 7:
                if data == 'S_OK!\r\n':
                    return True
                elif data == 'S_NK!\r\n':
                    self.reset_open_loop_step()
                    return False
                else:
                    self.reset_open_loop_step()
                    return False
            else:
                self.reset_open_loop_step()
                return False

    def is_step_over(self):
        self.hardware_connection.send_data('F_!')
        time.sleep(0.1)
        # Acknowledgment waiting
        while self.hardware_connection.is_data_waiting() is False:
            pass
        time.sleep(0.2)
        data = self.hardware_connection.read_data(self.hardware_connection.get_nb_data_waiting())
        data = data.decode('ascii')
        data = data.split('_')
        if data[1] == '1':
            return True
        else:
            return False

    def reset_open_loop_step(self):
        data = 'R_!'
        self.hardware_connection.send_data(data)

    def get_open_loop_data_index(self, index, channel):
        data = 'T_'+channel+'_' + str(index) + '_!'
        self.hardware_connection.send_data(data)
        while self.hardware_connection.is_data_waiting() is False:
            pass
        time.sleep(0.005)
        nb_data = self.hardware_connection.get_nb_data_waiting()
        value = self.hardware_connection.read_data(nb_data).decode('ascii')
        value = value.split('_')
        return value[3]

    def get_open_loop_data(self):
        self.x_data = numpy.zeros(self.samples)
        self.y_data = numpy.zeros(self.samples)
        self.s_data = numpy.zeros(self.samples)
        for k in range(self.samples):
            self.x_data[k] = self.get_open_loop_data_index(k, 'X')
            self.y_data[k] = self.get_open_loop_data_index(k, 'Y')
            self.s_data[k] = self.get_open_loop_data_index(k, 'S')
        return self.x_data, self.y_data, self.s_data

    def set_PID_params(self, Kx, Ky, Ix=0, Iy=0, Dx=0, Dy=0, sampling=10000):
        changed = False
        if sampling != self.sampling_freq:
            changed = True
            self.sampling_freq = sampling

        if self.K_X != Kx:
            changed = True
            self.K_X = Kx
        if self.K_Y != Ky:
            changed = True
            self.K_Y = Ky

        if self.I_X != Ix:
            changed = True
            self.I_X = Ix
        if self.I_Y != Iy:
            changed = True
            self.I_Y = Iy

        if self.D_X != Dx:
            changed = True
            self.D_X = Dx
        if self.D_Y != Dy:
            changed = True
            self.D_Y = Dy
        if changed:
            data = 'D_'+str(Kx)+'_'+str(Ky)+'_'+str(Ix)+'_'+str(Iy)
            data += '_'+str(Dx)+'_'+str(Dy)+'_'+str(sampling)+'_!'
            self.hardware_connection.send_data(data)
        # Tets ACK ??

    def start_PID_control(self):
        pass

    def stop_PID_control(self):
        pass

    def send_stop(self):
        self.hardware_connection.send_data('O_!')

    def reset_scan(self):
        pass

    def check_connection(self):
        # Sending data to check the connection
        self.hardware_connection.send_data('C')
        cpt_time = 0
        while cpt_time < 10 and self.hardware_connection.is_data_waiting() is False:
            time.sleep(0.1)
            cpt_time += 1
        if self.hardware_connection.is_data_waiting() != 0:
            nb_data = self.hardware_connection.get_nb_data_waiting()
            data_received = self.hardware_connection.read_data(nb_data).decode('ascii')
            if data_received[0] == 'C':
                return True
            else:
                return False
        else:
            return False
