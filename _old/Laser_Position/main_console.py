
import time

from drivers.LaserPID import LaserPID

# Launching as main for tests
if __name__ == "__main__":
    # Create an object of type SerialConnect
    my_serial = LaserPID()
    # Get a list of available serial ports (STM board only connected on USB)
    serial_port_list = my_serial.get_serial_ports_list()
    # Print the list
    print('List of available ports / STMicroelectronics')
    for port in serial_port_list:
        print(f'\t{port.device} | {port.description}')

    port_av = input('Enter the name of the port (COMxx) : ')
    #
    my_serial.set_serial_port(port_av)
    # Setup the selected serial port
    print(my_serial.is_connected())

    # Open the serial communication
    print(f'Serial is open ? {my_serial.connect_to_hardware()}')

    # Test if data are waiting in the serial buffer
    number_data = my_serial.is_data_waiting()
    if number_data:
        print(f'Data are ready')
    else:
        print(f'No data')

    # Check if the board is connected and still alive...
    print(f'Connection is OK ? {my_serial.check_connection()}')

    # Step Response test
    my_serial.set_open_loop_steps(-0.1, -0.1, 0.1, 0.1)
    my_serial.set_sampling_freq(10000)
    my_serial.set_open_loop_samples(1000)
    if my_serial.start_open_loop_step(10000, 100):
        print('Step OK')

    '''
    time.sleep(5)
    my_serial.hardware_connection.send_data('F_!')

    data = my_serial.hardware_connection.serial_link.read()
    print(f'DD = {data}')
    time.sleep(0.2)
    nb_data = my_serial.hardware_connection.serial_link.inWaiting()
    data += my_serial.hardware_connection.serial_link.read(nb_data)
    print(f'DD2 = {data}')
    '''

    while my_serial.is_step_over() is False:
        pass

    print('ok')

    c, i, v = my_serial.get_open_loop_data_index(1, 'X')
    print(f'chan={c} / index={i} / value={v}')
    my_serial.reset_open_loop_step()

    '''
    while my_serial.is_step_over() is False:
        print('waiting')
        time.sleep(1)

    print('data ready')
    '''

    # Unlink the serial port (and close if necessary)
    my_serial.disconnect_hardware()