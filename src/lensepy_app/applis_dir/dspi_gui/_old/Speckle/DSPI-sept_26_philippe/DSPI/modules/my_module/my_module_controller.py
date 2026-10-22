import os
from pathlib import Path

from pypylon import pylon

import numpy as np
import cv2
import serial
import time
from serial.serialutil import SerialException
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QErrorMessage


from lensepy import translate
from lensepy.css import *
from lensepy.appli._app.template_controller import TemplateController, ImageLive
from .my_module_views import MyModuleTopRightWidget, CameraWindow
from lensepy.widgets import ImageDisplayWidget, ImageDisplayWithCrosshair, XYMultiChartWidget
from DSPI.camera_dspi_widget import *

class MyModuleController(TemplateController):
    """
    Class to manage the different image processings on the DSPI experiment
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Attributes initialization
        self.x_cross = None     # Coordinates of the cross for slice measurements
        self.y_cross = None
        self.img_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
        self.thread = None      # Thread to run parallel tasks (image grabbing)
        self.worker = None      # Worker to run on the parallel thread
        self.processing = None  # Type of processing to be run (Image Difference/Phase Shift , Deformation/Vibration)
        self.set_size = None    # Number of images to be grabbed for the current processing (ex: 5 for phase shift)
        self.current_images_set = None      # To stock the images grabbed for the processing
        self.sans_def = None    # Phase pattern before deformation (for phase shift)
        self.current_phase = None   # Phase pattern after deformation (for phase shift)
        self.processed_phase_shift = None   # Result of the phase shift processing
        self.tensionpi = None   # Tension value to be sent to the Nucleo board

        # changement Philippe
        self.Phase_VS_Amp = (1 + 1e-12) # choix de affichage phase (Phase_VS_Amp = 1) ou amplitude (Phase_VS_Amp = 0)
        self.sans_def_amplitude = None    # Phase pattern before deformation (for phase shift)
        self.current_phase_amplitude = None   # Phase pattern after deformation (for phase shift)
        self.processed_phase_shift_amplitude = None  # Result of the phase shift processing
        self.current_images_set_amplitude = None  # To stock the images grabbed for the processing

        # changement Philippe
        self.Iteration = None
        self.set_Iteration = None
        self.set_IterationMax = None

        # Widgets
        self.bot_left = XYMultiChartWidget()            # Widget to display the slice measurement graphs
        self.top_left = ImageDisplayWithCrosshair()     # Widget to display the processed image
        self.bot_right = CameraParamsWidget(self)       # Widget to display the parameters of the camera
        self.top_right = MyModuleTopRightWidget()       # Widget to select the type of processing
        self.new_window = CameraWindow(self)            # Additional window to display the live camera flux
        self.new_window.show()
        self.bot_left.set_background('white')

        # Bits depth
        bits_depth = int(self.parent.variables.get('bits_depth', 8))
        self.top_left.set_bits_depth(bits_depth)

        # Initial Image
        self.image_ref = self.parent.variables.get('image')
        if self.image_ref is not None:
            self.top_left.set_image_from_array(self.image_ref)
            self.update_slices(self.image_ref)
        # Camera infos
        camera = self.parent.variables['camera']
        if camera is not None:
            expo_init = camera.get_parameter('ExposureTime')
            self.bot_right.slider_expo.set_value(expo_init)

        # Connexion Nucléo (commande piezo)
        self.piezo = None
        try:
            self.piezo = serial.Serial('COM4', 115200, timeout=1)
            print("Port série COM4 initialisé avec succès.")
        except SerialException as e:
            print(f"Erreur à l'ouverture du port série COM4 : {e}")

        # Signals
        self.top_left.point_selected.connect(self.handle_xy_changed)
        self.top_right.enregistrer_image.connect(self.handle_enregistrer_image)
        self.top_right.diff_image.connect(self.handle_diff_image)
        self.top_right.diff_image_vibr.connect(self.handle_diff_image_vibr)
        self.top_right.phase_shift.connect(self.handle_phase_shift)
        # ajout philippe
        self.top_right.phase_shift_amplitude.connect(self.handle_phase_shift_amplitude)

        self.top_right.stop_processing.connect(self.handle_stop)
        # Start live acquisition
        self.start_live()

    def start_live(self):
        """
        Start live acquisition with camera.
        """
        self.thread = QThread()
        self.worker = ImageLive(self)
        self.worker.moveToThread(self.thread)       # Worker associated to the thread

        self.thread.started.connect(self.worker.run)        # Worker runs while the thread is active
        self.worker.image_ready.connect(self.handle_image_ready)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def stop_live(self):
        """
        Stop live acquisition.
        """
        if self.worker:
            # Stop the worker
            self.worker.stop()

            # Wait for the end of the thread
            if self.thread:
                self.thread.quit()
                self.thread.wait() # Blocks until the end

            # Delete the references
            self.worker = None
            self.thread = None

    def handle_image_ready(self, image: np.ndarray):
        """
        Thread-safe GUI updates
        :param image:   Numpy array containing new image.
        """
        # Update Image depending on the processing selected
        if self.processing is None:
            self.top_left.set_image_from_array(image)
            self.update_slices(image)
        elif self.processing == 'image_diff':   # Image difference for deformation
            diff_image = image.astype(np.float32)-self.image_ref
            processed = np.abs(diff_image - np.mean(diff_image))
            processed = cv2.blur(processed, (5, 5))
            processed = cv2.normalize(processed, None, 0, 255, cv2.NORM_MINMAX).astype(np.float32)
            self.top_left.set_image_from_array(processed)
            self.update_slices(processed)
        elif self.processing == 'image_diff_vibr': # Feature not tested

            # changement Philippe
            # set important variable
            self.set_Iteration = 0
            self.set_IterationMax = 100

            #Iteration = self.set_Iteration
            #while Iteration < self.set_IterationMax:

            self.top_left.set_image_from_array(self.processed_vibration)
            self.update_slices(self.processed_vibration)
            #Iteration += 1


            """
            camera = self.parent.variables["camera"]
            self.send_voltage(0)
            time.sleep(0.3)
            new_imagedephasage0 = camera.get_image()

            self.send_voltage(2300)
            time.sleep(0.3)
            new_imagedephasagePi = camera.get_image()

            diff_image = new_imagedephasagePi.astype(np.float32) - new_imagedephasage0.astype(np.float32)
            processed = np.abs(diff_image - np.mean(diff_image))
            processed = cv2.blur(processed, (5, 5))
            processed = cv2.normalize(processed, None, 0, 255, cv2.NORM_MINMAX).astype(np.float32)
            self.top_left.set_image_from_array(processed)
            self.update_slices(processed)


            
            if self.tensionpi == 2300:
                diff_image = image.astype(np.float32) - self.image_ref
                processed = np.abs(diff_image - np.mean(diff_image))
                processed = cv2.blur(processed, (5, 5))
                processed = cv2.normalize(processed, None, 0, 255, cv2.NORM_MINMAX).astype(np.float32)
                self.top_left.set_image_from_array(processed)
                self.image_ref = image.astype(np.float32).copy()
                self.tensionpi = 0
                self.send_voltage(self.tensionpi)
                time.sleep(3)
            else :
                self.image_ref = image.astype(np.float32).copy()
                self.tensionpi = 2300
                self.send_voltage(self.tensionpi)
                time.sleep(3)
            """

        elif self.processing == 'phase_shift': # Phase shift for deformation (done only once)
            self.top_left.set_image_from_array(self.processed_phase_shift)
            self.update_slices(self.processed_phase_shift)

        # ajout Philippe
        elif self.processing == 'phase_shift_amplitude':  # Phase shift for deformation (done only once)
            self.top_left.set_image_from_array(self.processed_phase_shift_amplitude)
            self.update_slices(self.processed_phase_shift_amplitude)

        # Update live image in the second window
        if self.new_window is not None:
            self.new_window.camera_widget.set_image_from_array(image)
        # Store new image.
        self.parent.variables['image'] = image.copy()

    def handle_xy_changed(self, x, y):
        """
        Action performed when a crosshair is selected.
        :param x: X coordinate.
        :param y: Y coordinate.
        """
        self.x_cross = x
        self.y_cross = y
        image = self.parent.variables.get('image')
        if image is not None:
            self.update_slices(image)

    def handle_exposure_changed(self, value):
        """
        Action performed when the color mode changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            camera.set_parameter('ExposureTime', value)
            camera.initial_params['ExposureTime'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    def handle_black_level_changed(self, value):
        """
        Action performed when the black level changed.
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Read available formats
            camera.set_parameter('BlackLevel', value)
            camera.initial_params['BlackLevel'] = value
            self.bot_right.update_infos()
            # Restart live
            camera.open()
            self.start_live()

    def handle_stop(self):
        """
        Action performed when the Stop Treatment button is pressed
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Reset processing mode
            self.processing = None
            # Restart live
            camera.open()
            self.start_live()

    def handle_diff_image(self):
        """
        Action performed when the Image Difference button is pressed
        """

        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Change processing mode
            self.processing = 'image_diff'
            # Grab the reference image
            self.image_ref = self.parent.variables['image'].astype(np.float32)
            # Restart live
            camera.open()
            self.start_live()

    def handle_diff_image_vibr(self):
        """
        Action performed when the Image Difference Vibration button is pressed
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Change processing mode
            self.processing = 'image_diff_vibr'
            """
            # Set tension value
            self.tensionpi = 0
            self.send_voltage(self.tensionpi)
            time.sleep(3)  # Wait to make sure the command is followed by the piezo
            # Grab reference image
            self.image_ref = self.parent.variables['image'].astype(np.uint8)
            # Set tension value
            self.tensionpi = 2300
            """
            # changement Philippe
            #set important variable
            #self.set_Iteration = 0
            #self.set_IterationMax = 100
            self.tensionPi = 2300

            # Check connection with the piezo
            if not self.piezo or not self.piezo.is_open:
                print("Traitement de déformation annulé : port série non disponible.")
                # Restart live
                self.processing = None
                camera.open()
                self.start_live()
                return

            #acquisition of the reference image and of the Pi image


            camera = self.parent.variables["camera"]
            self.stop_live()
            if camera is not None:
                # Acquisition of the 2 images
                camera.open()
                camera.camera_acquiring = True

                self.send_voltage(0)
                time.sleep(0.3)
                new_image0 = camera.get_image()
                time.sleep(0.1)

                self.send_voltage(self.tensionPi)
                time.sleep(0.3)
                new_imagePi = camera.get_image()
                time.sleep(0.1)

                diff =(new_imagePi - new_image0)

                # Image processing

                min_val = np.percentile(diff, 10)
                max_val = np.percentile(diff, 90)
                if abs(max_val - min_val) < 1e-6:
                    max_val = min_val + 1

                print("min_val:", min_val)
                print("max_val:", max_val)

                processed = np.clip((diff - min_val) / (max_val - min_val), 0, 1)
                processed = (processed * 255).astype(np.uint8)
                self.processed_vibration = cv2.applyColorMap(processed, cv2.COLORMAP_JET).astype(np.uint8)



            """
            # Send command to piezo
            self.send_voltage(self.tensionpi)
            time.sleep(3) # Wait to make sure the command is followed by the piezo
            self.image_def = self.parent.variables['image'].astype(np.uint8)
            """

            # Restart live
            camera.open()
            self.start_live()


    def handle_phase_shift(self):
        """
        Action performed when the Phase Shift Deformation button is pressed
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Change processing mode
            self.processing = 'phase_shift'
            # Set important variables
            self.set_size = 5
            self.current_images_set = []
            self.tensionpi = 2300
            # Check connection with the piezo
            if not self.piezo or not self.piezo.is_open:
                print("Traitement de déformation annulé : port série non disponible.")
                # Restart live
                self.processing = None
                camera.open()
                self.start_live()
                return

            # Acquisition of the reference image
            print("Capture de l'image de référence pour le phase-shift...")
            self.sans_def = self.phase_shift_acquisition()
            # Check if reference image has been processed correctly
            if self.sans_def is None:
                print("Échec de la capture de l'image de référence1.")
                # Restart live
                self.processing = None
                camera.open()
                self.start_live()
                return
            print("Image de référence capturée.")
            time.sleep(1)
            print("Appliquer la tension phase.")
            time.sleep(1)
            # Acquisition of the deformed image
            self.current_phase = self.phase_shift_acquisition()
            # Check if deformed image has been processed correctly
            if self.current_phase is not None:
                # Image processing
                #diff = np.abs(self.current_phase - self.sans_def)
                #diff = np.divide(self.current_phase, self.sans_def)

                # changement Philippe
                diff = np.abs (1 - self.Phase_VS_Amp) * np.divide(self.current_phase, self.sans_def) + (self.Phase_VS_Amp) * np.abs(self.current_phase - self.sans_def)


                min_val = np.percentile(diff, 10)
                max_val = np.percentile(diff, 90)

                print("min_val:",  min_val)
                print("max_val:", max_val)

                if abs(max_val - min_val) < 1e-6:
                    max_val = min_val + 1

                #processed = np.clip((diff - min_val) / (max_val - min_val), 0, 1)

                # changement Philippe
                processed = np.clip((diff), 0, 1)
                #processed = (diff)
                #processed = ((diff - min_val) / (max_val - min_val))
                #processed = (processed * 255)).astype(np.uint8)

                # changement Philippe
                processed =(np.abs(1 - self.Phase_VS_Amp) * (255 * processed) + (self.Phase_VS_Amp) * (255 * processed)).astype(np.uint8)

                #processed = ((diff) * 255).astype(np.uint8)
                self.processed_phase_shift = cv2.applyColorMap(processed, cv2.COLORMAP_JET).astype(np.uint8)

            # Restart Live
            camera.open()
            self.start_live()



    def phase_shift_acquisition(self, images_counter=0):
        """
        Recursive function for Phase Shift acquistion and algorithm
        :param images_counter: number of images already recorded.
        """
        # Set the successive voltages to send to piezo
        voltages = [0, self.tensionpi/2, self.tensionpi, 3*self.tensionpi/2, 2*self.tensionpi]
        camera = self.parent.variables["camera"]
        self.stop_live()
        if camera is not None :
            # Acquisition of the 5 images
            camera.open()
            camera.camera_acquiring = True
            if images_counter < self.set_size: # If there are still images to record
                self.send_voltage(voltages[images_counter])
                time.sleep(0.3)
                new_image = camera.get_image()
                if new_image is None:
                    print("Echec de l'acquisition")
                    return None
                self.current_images_set.append(new_image.astype(np.float32))
                images_counter += 1
                return self.phase_shift_acquisition(images_counter)
            else:     # Phase shift algorithm when all images have been recorded
                images_counter = 0
                camera.camera_acquiring = False
                camera.close()
                if len(self.current_images_set) < 5:
                    return None
                img0, imgpi2, imgpi, img3pi2, img2pi = self.current_images_set
                numerator = 2 * (img3pi2 - imgpi2)
                denominator = 2 * imgpi - img2pi - img0
                denominator[denominator == 0] = 1e-6
                self.current_images_set = []
                #return np.arctan2(numerator, denominator)

                # changement Philippe
                self.send_voltage(0) # remise à zéro de la tension appliquée au piezo
                # retour de la phase ou de l'amplitude suivant la valeur de Phase_VS_Amp
                # avec normalisation à pi de la phase pour avoir des images normalisee à 1 en theorie

                # test avec arctangente habituelle
                #return  ((self.Phase_VS_Amp) * np.arctan(np.divide(numerator, denominator)) / np.pi + np.abs(1 - self.Phase_VS_Amp) * np.sqrt(numerator**2 + denominator**2))

                return  ((self.Phase_VS_Amp) * np.arctan2(numerator, denominator) / np.pi + np.abs(1 - self.Phase_VS_Amp) * np.sqrt(numerator**2 + denominator**2))

    #ajout philippe
    def handle_phase_shift_amplitude(self):
        """
        Action performed when the Phase Shift Deformation button is pressed
        """
        camera = self.parent.variables["camera"]
        if camera is not None:
            # Stop live safely
            self.stop_live()
            # Close camera
            camera.close()
            # Change processing mode
            self.processing = 'phase_shift_amplitude'
            # Set important variables
            self.set_size = 5
            self.current_images_set_amplitude = []
            self.tensionpi = 2300
            # Check connection with the piezo
            if not self.piezo or not self.piezo.is_open:
                print("Traitement de déformation annulé : port série non disponible.")
                # Restart live
                self.processing = None
                camera.open()
                self.start_live()
                return

            # Acquisition of the reference image
            print("Capture de l'image de référence pour le phase-shift...")
            self.sans_def_amplitude = self.phase_shift_acquisition_amplitude()
            # Check if reference image has been processed correctly
            if self.sans_def_amplitude is None:
                print("Échec de la capture de l'image de référence1.")
                # Restart live
                self.processing = None
                camera.open()
                self.start_live()
                return
            print("Image de référence capturée.")
            time.sleep(1)
            print("Appliquer la tension amplitude.")
            time.sleep(1)
            # Acquisition of the deformed image
            self.current_phase_amplitude = self.phase_shift_acquisition_amplitude()
            # Check if deformed image has been processed correctly
            if self.current_phase_amplitude is not None:
                # Image processing
                # diff = np.abs(self.current_phase - self.sans_def)
                # diff = np.divide(self.current_phase, self.sans_def)

                # changement Philippe
                rapamp = np.divide(self.current_phase_amplitude, self.sans_def_amplitude)

                min_val = np.percentile(rapamp, 10)
                max_val = np.percentile(rapamp, 90)

                print("min_val:", min_val)
                print("max_val:", max_val)

                if abs(max_val - min_val) < 1e-6:
                    max_val = min_val + 1

                # processed = np.clip((diff - min_val) / (max_val - min_val), 0, 1)

                # changement Philippe
                processed_amplitude = np.clip((rapamp), 0, 1)
                # processed = (diff)
                # processed = ((diff - min_val) / (max_val - min_val))
                # processed = (processed * 255)).astype(np.uint8)

                # changement Philippe
                processed_amplitude = ((255 * processed_amplitude)).astype(np.uint8)

                # processed = ((diff) * 255).astype(np.uint8)
                self.processed_phase_shift_amplitude = cv2.applyColorMap(processed_amplitude, cv2.COLORMAP_JET).astype(np.uint8)

            # Restart Live
            camera.open()
            self.start_live()

    # ajout philippe
    def phase_shift_acquisition_amplitude(self, images_counter=0):
        """
        Recursive function for Phase Shift acquistion and algorithm
        :param images_counter: number of images already recorded.
        """
        # Set the successive voltages to send to piezo
        voltages = [0, self.tensionpi / 2, self.tensionpi, 3 * self.tensionpi / 2, 2 * self.tensionpi]
        camera = self.parent.variables["camera"]
        self.stop_live()
        if camera is not None:
            # Acquisition of the 5 images
            camera.open()
            camera.camera_acquiring = True
            if images_counter < self.set_size:  # If there are still images to record
                self.send_voltage(voltages[images_counter])
                time.sleep(0.3)
                new_image_amplitude = camera.get_image()
                if new_image_amplitude is None:
                    print("Echec de l'acquisition")
                    return None
                self.current_images_set_amplitude.append(new_image_amplitude.astype(np.float32))
                images_counter += 1
                return self.phase_shift_acquisition_amplitude(images_counter)
            else:  # Phase shift algorithm when all images have been recorded
                images_counter = 0
                camera.camera_acquiring = False
                camera.close()
                if len(self.current_images_set_amplitude) < 5:
                    return None
                img0_amplitude, imgpi2_amplitude, imgpi_amplitude, img3pi2_amplitude, img2pi_amplitude = self.current_images_set_amplitude
                numerator_amplitude = 2 * (img3pi2_amplitude - imgpi2_amplitude)
                denominator_amplitude = 2 * imgpi_amplitude - img2pi_amplitude - img0_amplitude
                denominator_amplitude[denominator_amplitude == 0] = 1e-6
                self.current_images_set_amplitude = []
                # return np.arctan2(numerator, denominator)

                # changement Philippe
                self.send_voltage(0)  # remise à zéro de la tension appliquée au piezo
                # retour de la phase ou de l'amplitude suivant la valeur de Phase_VS_Amp
                # avec normalisation à pi de la phase pour avoir des images normalisee à 1 en theorie

                # test avec arctangente habituelle
                # return  ((self.Phase_VS_Amp) * np.arctan(np.divide(numerator, denominator)) / np.pi + np.abs(1 - self.Phase_VS_Amp) * np.sqrt(numerator**2 + denominator**2))

                return  (np.sqrt(numerator_amplitude ** 2 + denominator_amplitude ** 2))

    def send_voltage(self, voltage_mV):
        """
        Action performed to send a command tension to the piezo mirror
        """
        if not self.piezo or not self.piezo.is_open:
            return False

        try:
            command = f'V{int(voltage_mV)};'
            self.piezo.reset_input_buffer()
            self.piezo.write(command.encode('ascii'))

            response = self.piezo.read_until(b';')
            print("Réponse carte:", response)

            return b'OK' in response

        except Exception as e:
            print(f"Erreur d'envoi série : {e}")
            return False

    # Slices
    def update_slices(self, image):
        """
        Update slice values from image.
        :param image:   Numpy array containing the new image.
        """
        if self.x_cross is None or self.y_cross is None or image is None:
            return
        # Image format detection : grayscale or RGB
        if image.ndim == 2:  # grayscale
            gray_image = image
        elif image.ndim == 3 and image.shape[2] == 3:  # RGB
            gray_image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            raise ValueError("Image format unsupported")
        x_idx, y_idx = int(self.x_cross), int(self.y_cross)
        x_data = gray_image[y_idx, :]
        y_data = gray_image[:, x_idx]

        # Utilise np.arange pour générer directement les positions
        xx = np.arange(1, x_data.size + 1)
        yy = np.arange(1, y_data.size + 1)

        # Structure plus compacte
        self.bot_left.set_data(
            [xx, yy],
            [x_data, y_data],
            y_names=[translate('horizontal'), translate('vertical')],
            x_label='position',
            y_label='intensity'
        )
        self.bot_left.refresh_chart()
        self.bot_left.set_information(
            f'Mean H = {np.mean(x_data):.1f} / Min = {np.min(x_data):.1f} / Max = {np.max(x_data):.1f} [] '
            f'Mean V = {np.mean(y_data):.1f} / Min = {np.min(y_data):.1f} / Max = {np.max(y_data):.1f}')



    def handle_enregistrer_image(self):
        """
        Action performed when the Enregistrer button is pressed
        Incomplete function : works only for the phase shift result for now
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        image = self.processed_phase_shift
        was_saved = False

        if image is not None:
            try:
                filename = f"C:/Users/TP67/PycharmProjects/lense_DSPI/lense_DSPI/image_phase_shift_{timestamp}.png"
                cv2.imwrite(filename, image)
                print(f"Image enregistrée : {filename}")
                was_saved = True
            except Exception as e:
                print(f"Erreur d'enregistrement de l'image brute : {e}")


        if not was_saved:
            print("Aucune image disponible à enregistrer.")



    def cleanup(self):
        """
        Stop the camera cleanly and release resources.
        """
        self.stop_live()
        camera = self.parent.variables["camera"]
        if camera is not None:
            if getattr(camera, "is_open", False):
                camera.close()
            camera.camera_acquiring = False
        self.new_window.close()
        self.new_window = None
        self.worker = None
        self.thread = None
        self.piezo.close()
        self.piezo = None


    def _get_image_dir(self, filepath):
        if filepath is None:
            return ''
        else:
            # Detect if % in filepath
            if '%USER' in filepath:
                new_filepath = filepath.split('%')
                new_filepath = f'{Path.home()}/{new_filepath[2]}'
                return new_filepath
            else:
                return filepath