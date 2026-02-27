from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont, QIcon
import pyqtgraph as pg
from serial import Serial, SerialException
import serial
import serial.tools.list_ports
import struct
import time
import random as rd
import interface_main

class SerialWorker(QtCore.QThread):
        data_received = QtCore.pyqtSignal(float)
        counters_received = QtCore.pyqtSignal(int, int, int, int, int, int)
        data_counterA = QtCore.pyqtSignal(int)

        def __init__(self, serial_port):
                super().__init__()
                self.serial_port = serial_port
                self.running = True
                self.tau = 26*10**(-9)


        def run(self):
                while self.running:
                        try:
                                counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C, counter_AB_corrige, counter_AC_corrige = self.read_counters()

                                if counter_A is not None:
                                        # Afficher les résultats
                                        print(f"Counter A: {counter_A}") 
                                        print(f"Counter AB: {counter_AB}")
                                        print(f"Counter AC: {counter_AC}")
                                        print(f"Counter ABC: {counter_ABC}")
                                        print(f"Counter B: {counter_B}")
                                        print(f"Counter C: {counter_C}")
                                        print(f"Counter AB corrigé: {counter_AB_corrige}")
                                        print(f"Counter AC corrigé: {counter_AC_corrige}")

                                self.counters_received.emit(counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C)
                                try :
                                        self.g2_3detect = counter_ABC * counter_A / (counter_AB * counter_AC)
                                        print(f"La valeur du g2 à trois détecteurs est : {self.g2_3detect}")
                                except :
                                        self.g2_3detect = 0
                                        print("Erreur : Division par 0 dans le calcul du g2")
                                self.data_received.emit(self.g2_3detect)
                                self.data_counterA.emit(counter_A)


                        except KeyboardInterrupt:
                                print("Fin du programme.")
                                self.running = False

        def read_counters(self):
                # Lire 18 octets (3 octets par compteur)
                data = self.serial_port.read(18)
                #data = b'\x01\x86\x94\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\xc3J\x00\xc3J'
                print(data)

                if len(data) == 18:
                        print('ok')
                        # Convertir les 18 octets reçus en 6 compteurs (3 octets pour chaque compteur)
                        counter_A = struct.unpack('>I', b'\x00' + data[0:3])[0]  # Utilise '>I' pour un entier Big Endian
                        counter_AB = struct.unpack('>I', b'\x00' + data[3:6])[0]
                        counter_AC = struct.unpack('>I', b'\x00' + data[6:9])[0]
                        counter_ABC = struct.unpack('>I', b'\x00' + data[9:12])[0]
                        counter_B = struct.unpack('>I', b'\x00' + data[12:15])[0]
                        counter_C = struct.unpack('>I', b'\x00' + data[15:18])[0]
                        counter_AB_corrected = int(counter_AB - counter_A*counter_B*self.tau)
                        counter_AC_corrected = int(counter_AC - counter_A*counter_C*self.tau)

                        return counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C, counter_AB_corrected, counter_AC_corrected
                else:
                        print("Erreur de lecture des données")
                        return None, None, None, None, None, None

class CounterStorageWorker(QtCore.QThread):
        counters_stored = QtCore.pyqtSignal(int, int, int, int)

        def __init__(self):
                super().__init__()
                self.counter_A = 0
                self.counter_AB = 0
                self.counter_AC = 0
                self.counter_ABC = 0

        def store_counters(self, counter_A, counter_AB, counter_AC, counter_ABC):
                self.counter_A = counter_A
                self.counter_AB = counter_AB
                self.counter_AC = counter_AC
                self.counter_ABC = counter_ABC
                self.counters_stored.emit(self.counter_A, self.counter_AB, self.counter_AC, self.counter_ABC)
   

class Ui_MainWindow(QtCore.QObject):
        data_g2 = QtCore.pyqtSignal(float)
        data_counter_A = QtCore.pyqtSignal(int)
        data_counter_multiple = QtCore.pyqtSignal(int, int, int, int, int, int)

        def __init__(self):
                super().__init__()
                serial_port = serial.tools.list_ports.comports()  # L’objet serial_port est alors une liste contenant tous les objets de type port de communication série de votre machine

                for port in serial_port:
                # Cela affiche chaque élément de la liste serial_port, c'est à dire tous les ports de communication série de l'ordinateur
                        print(f"{port.name} // {port.device} // D={port.description}")

                self.ser = serial.Serial("COM7", baudrate=9600)
                print(self.ser)
                
                self.stack = 0
                self.data_buffer = []
                self.data_g2.connect(self.update_plot)
                #self.data_counter_A.connect(self.update_progress_bar)
                
                self.A = 0 
                self.AB = 0
                self.AC = 0
                self.ABC = 0
                self.B = 0 
                self.C = 0 

                self.serial_worker = SerialWorker(self.ser)
                self.serial_worker.data_received.connect(self.data_g2.emit)
                #self.serial_worker.data_counterA.connect(self.data_counter_A.emit)
                
                self.serial_worker.counters_received.connect(self.data_counter_multiple.emit)
                self.data_counter_multiple.connect(self.update_progress_bar)

                self.counter_storage_worker = CounterStorageWorker()
                self.serial_worker.counters_received.connect(self.counter_storage_worker.store_counters)
                self.counter_storage_worker.counters_stored.connect(self.send_counters_to_other_code)

        def calculate_g2(self):
                self.serial_worker.start()

        #T_int in ms
        def change_integration_time(self,T_int):
                byt_val = T_int.to_bytes(2, 'big')
                print(byt_val)
                self.ser.write(byt_val)

        def stop_g2(self):
                self.serial_worker.running = False
        
        def update_progress_bar(self, counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C):
                self.A, self.AB, self.AC, self.ABC, self.B, self.C = counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C
        
        
        def setupUi(self, MainWindow):
                MainWindow.setObjectName("MainWindow")
                MainWindow.resize(770, 685)
                self.centralwidget = QtWidgets.QWidget(MainWindow)
                self.centralwidget.setObjectName("centralwidget")
                self.label_7 = QtWidgets.QLabel(self.centralwidget)
                self.label_7.setGeometry(QtCore.QRect(81, 21, 571, 41))
                self.label_7.setStyleSheet("    font-size: 15px;\n"
                "    font-weight: bold;\n"
                "    color: white;\n"
                "    background-color: grey;\n"
                "    border: 2px solid orange; /* Bordure verte */\n"
                "    border-radius: 5px; /* Coins arrondis */\n"
                "")
                self.label_7.setAlignment(QtCore.Qt.AlignCenter)
                self.label_7.setObjectName("label_7")
                self.frame = QtWidgets.QFrame(self.centralwidget)
                self.frame.setGeometry(QtCore.QRect(119, 99, 501, 371))
                self.frame.setStyleSheet("border-radius: 10px;\n"
                "background-color: lightgrey\n"
                "")
                self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame.setObjectName("frame")
                self.verticalLayoutWidget = QtWidgets.QWidget(self.frame)
                self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 481, 351))
                self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
                self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
                self.verticalLayout.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout.setObjectName("verticalLayout")
                self.label_8 = QtWidgets.QLabel(self.centralwidget)
                self.label_8.setGeometry(QtCore.QRect(130, 90, 185, 16))
                self.label_8.setStyleSheet("    font-size: 12px;\n"
                "    font-weight: bold;\n"
                "    color: white;\n"
                "    background-color: grey;\n"
                "    border: 2px solid grey; /* Bordure verte */\n"
                "    border-radius: 8px; /* Coins arrondis */\n"
                "")
                self.label_8.setObjectName("label_8")
                self.frame_2 = QtWidgets.QFrame(self.centralwidget)
                self.frame_2.setGeometry(QtCore.QRect(120, 480, 501, 171))
                self.frame_2.setStyleSheet("\n"
                "border-radius: 10px;\n"
                "background-color: lightgrey\n"
                "")
                self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame_2.setObjectName("frame_2")
                self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.frame_2)
                self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(20, 10, 461, 151))
                self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
                self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
                self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_6.setObjectName("verticalLayout_6")
                self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
                self.label_2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                self.label_2.setAutoFillBackground(False)
                self.label_2.setStyleSheet("QLabel {\n"
                "    font-size: 16px;\n"
                "    font-weight: bold;\n"
                "    color: white;\n"
                "    background-color: grey;\n"
                "    border: 2px solid orange; /* Bordure verte */\n"
                "    border-radius: 10px; /* Coins arrondis */\n"
                "    padding: 5px; /* Espacement interne */\n"
                "}")
                self.label_2.setFrameShape(QtWidgets.QFrame.NoFrame)
                self.label_2.setFrameShadow(QtWidgets.QFrame.Plain)
                self.label_2.setLineWidth(0)
                self.label_2.setMidLineWidth(0)
                self.label_2.setAlignment(QtCore.Qt.AlignCenter)
                self.label_2.setWordWrap(False)
                self.label_2.setObjectName("label_2")
                self.verticalLayout_6.addWidget(self.label_2)



                MainWindow.setCentralWidget(self.centralwidget)
                self.menubar = QtWidgets.QMenuBar(MainWindow)
                self.menubar.setGeometry(QtCore.QRect(0, 0, 770, 24))
                self.menubar.setObjectName("menubar")
                MainWindow.setMenuBar(self.menubar)
                self.statusbar = QtWidgets.QStatusBar(MainWindow)
                self.statusbar.setObjectName("statusbar")
                MainWindow.setStatusBar(self.statusbar)
                
                self.pushButton_5 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
                self.pushButton_5.setStyleSheet("QPushButton {\n"
                "    background-color: #4CAF50;\n"
                "    color: white;\n"
                "    font-size: 14px;\n"
                "    font-weight: bold;\n"
                "    border: 2px solid #2E7D32;\n"
                "    border-radius: 5px;\n"
                "    padding: 1px;\n"
                "}\n"
                "\n"
                "QPushButton:hover {\n"
                "    background-color: #45a049;\n"
                "    border-color: #1B5E20;\n"
                "}\n"
                "\n"
                "QPushButton:pressed {\n"
                "    background-color: #388E3C;\n"
                "    border-color: #1B5E20;\n"
                "}\n"
                "\n"
                "")
                self.pushButton_5.setObjectName("pushButton_5")
                self.pushButton_5.clicked.connect(self.save_plot)
                self.pushButton_5.setText("Enregistrer l'image")
                self.verticalLayout_6.addWidget(self.pushButton_5)

                self.retranslateUi(MainWindow)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

                self.plot_graph = pg.PlotWidget()
                self.plot_graph.setBackground("k")
                self.plot_graph.setLabel("left", "Valeur de la mesure")
                self.plot_graph.setLabel("bottom", "Temps (x1s)")
                self.plot_graph.setTitle("Affichage du calcul du 3 à trois détecteurs")
                self.plot_graph.showGrid(x=True, y=True)

                self.curve = self.plot_graph.plot(
                [],
                [],
                pen=pg.mkPen(width=5, color=(127, 127, 0)),
                name="Points de coïncidences",
                symbol="+",
                symbolSize=5,
                symbolBrush="b",
                )

                self.verticalLayout.addWidget(self.plot_graph)

        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("MainWindow", "Interface g2 à trois détecteurs"))
                self.label_7.setText(_translate("MainWindow", "Calcul et affichage du g2"))
                self.label_8.setText(_translate("MainWindow", "Représentation graphique g2"))
                self.label_2.setText(_translate("MainWindow", "Contrôle de la fenêtre du g2"))

        def update_plot(self, value):
                """Met à jour le graphique et le compteur de points"""
                self.data_buffer.append(value)
                self.curve.setData(range(len(self.data_buffer)), self.data_buffer)
                # self.label_11.setText(f'Nombres de points: {self.class_Data.counter}')

        def save_plot(self):
                self.stack+=1
                exporter = pg.exporters.ImageExporter(self.plot_graph.plotItem)
                # save to file
                exporter.export(f'{self.stack}_Graphique_g2.png')

        def send_counters_to_other_code(self, counter_A, counter_AB, counter_AC, counter_ABC):
                # Implémentez ici le code pour envoyer les valeurs des compteurs à un autre code
                print(f"Sending counters to other code: A={counter_A}, AB={counter_AB}, AC={counter_AC}, ABC={counter_ABC}")


