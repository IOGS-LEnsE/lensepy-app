import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports
from lensepy.modules.drivers.piezo_dmd.pycrafter.pycrafter6500 import dmd


class DMDWrapper:
    """
    Wrapper class for a DMD xxx.

    # DMD operating modes:
        - mode=0 for normal video mode
        - mode=1 for pre stored pattern mode
        - mode=2 for video pattern mode
        - mode=3 for pattern on the fly mode

    """

    def __init__(self, parent=None):
        self.image = [None]*3
        self.dmd_hardware = None

    def init_dmd(self):
        if self.dmd_hardware is None:
            self.dmd_hardware = dmd()
            self.dmd_hardware.init_dmd()
            print("DMD HW OK")
        if self.dmd_hardware.is_dmd():
            print("DMD reset OK")
            '''
            self.dmd_hardware.reset()
            time.sleep(0.5)
            '''
            self.dmd_hardware.stopsequence()
            self.dmd_hardware.changemode(3)
            return True
        return False

    def is_dmd_connected(self):
        """Test if the DMD is connected."""
        return self.dmd_hardware.checkforerrors()
        """
        if self.dmd_hardware is None:
            return False
        else:
            try:
                # Send Status command
                # .command('r',0xff,0x11,0x00,[])
                #         self.readreply()
                self.dmd_hardware.command('r', 0x00, 0x1a, 0x0a, [])
                ans_list = []
                for i in self.dmd_hardware.ans:
                    ans_list.append(i)
                    #print(hex(i))
                # Test Hardware Status Command :
                #   bit 0 = 0/Error-1/Success, bits 1/2/3 = 0/No Error
                if ans_list[0] and 0x0F == 0x01:
                    return True
                else:
                    print("Test DMD NONONO")
                    return False
            except Exception as e:
                print(f"Exception on DMD : {e}")
                return False
        """

    def set_image(self, image, number=1):
        """
        Set image to send to the DMD.
        :param image:   2D array containing the image to send to the DMD.
        :param number:   Number of the image to set.
        """
        self.image[number-1] = image

    def get_image(self, number):
        """Get an image with its number."""
        return self.image[number-1]

    def is_images_opened(self):
        """All images are opened"""
        images_cnt = 0
        for k in range(3):
            if self.image[k] is not None:
                images_cnt += 1
        return images_cnt == 3

    def display_image(self, images):
        """Display an image on the DMD."""
        pass
        #self.dmd_hardware.

        '''
        self.launchSequence([pattern_path])
        print(f"{self.getSmallText(pattern_path)} : loaded.\n")

        if self.DMDHardware is None:
            self.DMDHardware = pycrafter6500.dmd()

        images_disp = []

        for path in pattern:
            images.append((numpy.asarray(PIL.Image.open(path)) // 129))

        number_of_images = len(images)

        self.DMDHardware.stopsequence()

        self.DMDHardware.changemode(3)

        exposure = [1000000] * number_of_images
        dark_time = [0] * number_of_images
        trigger_in = [False] * number_of_images
        trigger_out = [1] * number_of_images

        """
        images: python list of numpy arrays, with size (1080,1920), dtype uint8, and filled with binary values (1 and 0 only)
        exposures: python list or numpy array with the exposure times in microseconds of each image. 
            Length must be equal to the images list.
        trigger in: python list or numpy array of boolean values determing wheter to wait for an external trigger before exposure. 
            Length must be equal to the images list.
        dark time: python list or numpy array with the dark times in microseconds after each image. 
            Length must be equal to the images list.
        trigger out: python list or numpy array of boolean values determing wheter to emit an external trigger after exposure. 
            Length must be equal to the images list.
        repetitions: number of repetitions of the sequence. set to 0 for infinite loop.
        """

        self.DMDHardware.defsequence(images, exposure, trigger_in, dark_time, trigger_out, 0)

        self.DMDHardware.startsequence()
        '''


class PiezoWrapper:
    """Class for controlling piezoelectric motion system,
	using an interface of type Nucleo-G431KB.

    This class uses PySerial library to communicate with Nucleo board.
	The baudrate is 115200 bds.


    """

    def __init__(self):
        """
        Initialize a piezo system
		"""
        self.connected = False
        self.serial_com = None
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
                    self.serial_link = serial.Serial(self.serial_com, baudrate=115200)
                    self.connected = True
                    return True
                except:
                    print('Cant connect')
                    self.connected = False
                    return False
        return False

    def is_connected(self):
        """
        Return if the hardware is connected.
        :return:    True if connection is done, else False.
        """
        if self.connected:
            try:
                self.serial_link.write(b'_C!')
            except:
                print('Error Sending')
                # Timeout
            for k in range(10):
                if self.serial_link.in_waiting == 4:
                    self.read_bytes = self.serial_link.read(4).decode('utf-8')
                    if self.read_bytes[2] == '1':
                        return True
                    else:
                        return False
                else:
                    time.sleep(0.02)
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

    def get_position(self):
        """
        Return the position of the piezo.
        :return:    position of the piezo. pos_um, pos_nm
        """
        if self.connected:
            try:
                self.serial_link.write(b'_G!')
            except:
                print('Error Sending - GetPosition')
                # Detection of acknowledgement value
            for k1 in range(10):
                if self.serial_link.in_waiting < 2:
                    self.read_bytes = self.serial_link.read(2).decode('utf-8')
                    # if position sended
                    if self.read_bytes[1] == 'G':
                        # Detection of acknowledgement value
                        for k2 in range(10):
                            if self.serial_link.in_waiting == 7:
                                self.read_bytes = self.serial_link.read(7).decode('utf-8')
                                pos_um = 0
                                pos_nm = 0
                                if self.read_bytes[0] != ' ':
                                    pos_um += (int(self.read_bytes[0])) * 10
                                if self.read_bytes[1] != ' ':
                                    pos_um += (int(self.read_bytes[1])) * 1

                                if self.read_bytes[3] != ' ':
                                    pos_nm += (int(self.read_bytes[3])) * 100
                                if self.read_bytes[4] != ' ':
                                    pos_nm += (int(self.read_bytes[4])) * 10
                                if self.read_bytes[5] != ' ':
                                    pos_nm += (int(self.read_bytes[5])) * 1

                                return pos_um, pos_nm
                            else:
                                time.sleep(0.1)
                    else:
                        pos_um = -1
                        pos_nm = -1
                        return pos_um, pos_nm
                else:
                    time.sleep(0.1)
        print('Enf of function')
        return -1, -1

    def get_hw_version(self):
        """
        Get hardware version.
        :return:    Hardware version.
        """
        if self.connected:
            try:
                self.serial_link.write(b'_V!')
            except:
                print('Error Sending - HW Version')
                # Timeout / 1 s
            for k in range(10):
                if self.serial_link.in_waiting == 5:
                    self.read_bytes = self.serial_link.read(5).decode('utf-8')
                    return self.read_bytes[2:3]
                else:
                    time.sleep(0.01)
        return -1

    def move_position(self, pos_um, pos_nm):
        """
        Move piezo to a specific position.
        :param pos_um:  Position in um
        :param pos_np:  Position in nm
        """
        if (pos_um < 0) or (pos_um > 10):
            return False
        if (pos_nm < 0) or (pos_nm > 999):
            return False

        data = '_M'
        if pos_um < 10:
            data += ' ' + str(pos_um) + '.'
        else:
            data += str(pos_um) + '.'

        if pos_nm < 10:
            data += '  ' + str(pos_nm) + '!'
        elif pos_nm < 100:
            data += ' ' + str(pos_nm) + '!'
        else:
            data += str(pos_nm) + '!'

        if self.connected:
            try:
                self.serial_link.write(data.encode())
            except:
                print('Error Sending - movePosition')
                # Timeout / 1 s
            for k in range(10):
                if self.serial_link.in_waiting == 4:
                    self.read_bytes = self.serial_link.read(4).decode('utf-8')
                    if self.read_bytes[2] == '1':
                        return True
                    else:
                        return False
                else:
                    time.sleep(0.02)
        return False


if __name__ == "__main__":
    # Test DMD
    dmd_wrapper = DMDWrapper()
    ack = dmd_wrapper.init_dmd()
    print(f'DMD Init ? {ack}')
    print(f'DMD OK ? {dmd_wrapper.is_dmd_connected()}')

    path_img1 = f'./MiresDMD/Mire256_pix_lense.bmp'
    path_img2 = f'./MiresDMD/FTM.bmp'
    img_gray1 = cv2.imread(path_img1, cv2.IMREAD_GRAYSCALE)   # 8 bits
    img_binary1 = (img_gray1 >= 128).astype(np.uint8)         # Transform to 1 bit image
    img_gray2 = cv2.imread(path_img2, cv2.IMREAD_GRAYSCALE)   # 8 bits
    img_binary2 = (img_gray2 >= 128).astype(np.uint8)         # Transform to 1 bit image

    print(f'BMP Opened ? {img_binary1.shape} / {img_binary1.dtype}')
    plt.figure()
    plt.imshow(img_binary1, cmap='gray')
    #plt.show()

    if dmd_wrapper.dmd_hardware is not None:
        dmd_wrapper.dmd_hardware.changemode(3)  # Pattern On-The-Fly
        for i in range(100):
            dmd_wrapper.dmd_hardware.defsequence([img_binary1], [50000], [False], [0], [False], 0)
            dmd_wrapper.dmd_hardware.startsequence()
            time.sleep(0.1)
            dmd_wrapper.dmd_hardware.defsequence([img_binary2], [50000], [False], [0], [False], 0)
            dmd_wrapper.dmd_hardware.startsequence()
            time.sleep(0.1)


    # Test Piezo
    piezo_wrapper = PiezoWrapper()
    comList = piezo_wrapper.list_serial_hardware()
    print(comList)
    if len(comList) > 0:
        com_selected = 'COM'+input('COM ?')
        piezo_wrapper.set_serial_com(com_selected)
        piezo_wrapper.connect()

        if piezo_wrapper.is_connected():
            print(f'Piezo / HW V.{piezo_wrapper.get_hw_version()}')
            piezo_wrapper.movePosition(z_um, z_nm)


'''
Example image_k
===============


import numpy as np
import cv2
from pycrafter6500 import dmd

# -------------------------------------------------
# 1️⃣ Charger N images et les binariser
# -------------------------------------------------
image_paths = ["img1.png", "img2.png", "img3.png"]  # chemin vers tes images
images_binary = []

for path in image_paths:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img_resized = cv2.resize(img, (1920, 1080))
    img_bin = (img_resized >= 128).astype(np.uint8)  # seuil à 128
    images_binary.append(img_bin)

# -------------------------------------------------
# 2️⃣ Connexion au DMD
# -------------------------------------------------
controller = dmd()
controller.changemode(3)  # Pattern On-The-Fly

# -------------------------------------------------
# 3️⃣ Fonction pour afficher l'image k
# -------------------------------------------------
def display_image_k(k, exposure_us=50000):
    """
    Affiche l'image k sur le DMD.
    k : index de l'image dans images_binary (0 à N-1)
    exposure_us : temps d'affichage en microsecondes
    """
    img_to_show = images_binary[k]
    # on envoie uniquement cette image dans une séquence d'1 image
    controller.defsequence(
        [img_to_show],        # image unique
        [exposure_us],        # durée d'exposition
        [False],              # trigger_in
        [0],                  # dark_time
        [False],              # trigger_out
        0                     # répétition infinie
    )
    controller.startsequence()

# -------------------------------------------------
# 4️⃣ Exemple d'utilisation
# -------------------------------------------------
# Affiche la première image
display_image_k(0)

# Pour changer l'image affichée plus tard :
# display_image_k(2)  # affiche la 3ème image
'''