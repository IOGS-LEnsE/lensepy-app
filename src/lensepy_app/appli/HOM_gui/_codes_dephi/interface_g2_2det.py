from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont, QIcon
import pyqtgraph as pg
from serial import Serial, SerialException
import serial
import serial.tools.list_ports
import struct
import time
import random as rd
import struct


class SerialWorker(QtCore.QThread):
        data_received = QtCore.pyqtSignal(float)

        def __init__(self, serial_port):
                super().__init__()
                self.serial_port = serial_port
                self.running = True

        def run(self):
                while self.running:
                        try:
                                counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C = self.read_counters()

                                if counter_A is not None:
                                        # Afficher les résultats
                                        print(f"Counter A: {counter_A}")
                                        print(f"Counter AB: {counter_AB}")
                                        print(f"Counter AC: {counter_AC}")
                                        print(f"Counter ABC: {counter_ABC}")
                                        print(f"Counter B: {counter_B}")
                                        print(f"Counter C: {counter_C}")

                                self.g2_3detect = counter_ABC * counter_A / (counter_AB * counter_AC)
                                print(f"La valeur du g2 à trois détecteurs est : {self.g2_3detect}")
                                self.data_received.emit(self.g2_3detect)
                                # Attendre un peu avant de lire à nouveau les données
                                time.sleep(1)

                        except KeyboardInterrupt:
                                print("Fin du programme.")
                                self.running = False

        def read_counters(self):
                # Lire 18 octets (3 octets par compteur)
                data = self.serial_port.read(18)

                if len(data) == 18:
                        # Convertir les 18 octets reçus en 6 compteurs (3 octets pour chaque compteur)
                        self.counter_A = struct.unpack('>I', b'\x00' + data[0:3])[0] + rd.randint(0, 100000)  # Utilise '>I' pour un entier Big Endian
                        self.counter_AB = struct.unpack('>I', b'\x00' + data[3:6])[0] + rd.randint(0, 100000)
                        self.counter_AC = struct.unpack('>I', b'\x00' + data[6:9])[0] + rd.randint(0, 100000)
                        self.counter_ABC = struct.unpack('>I', b'\x00' + data[9:12])[0] + rd.randint(0, 100000)
                        counter_B = struct.unpack('>I', b'\x00' + data[12:15])[0]
                        counter_C = struct.unpack('>I', b'\x00' + data[15:18])[0]

                        return self.counter_A, self.counter_AB, self.counter_AC, self.counter_ABC, counter_B, counter_C
                else:
                        print("Erreur de lecture des données")
                        return None, None, None, None, None, None


class Ui_MainWindow(QtCore.QObject):
        data_g2 = QtCore.pyqtSignal(float)

        def __init__(self):
                super().__init__()
                self.data_buffer = []
                self.data_g2.connect(self.update_plot)

                self.serial_worker = SerialWorker(ser)
                self.serial_worker.data_received.connect(self.data_g2.emit)
        
        def calculate_g2(self):
                self.serial_worker.start()

        def stop_g2(self):
                self.serial_worker.running = False
                        
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
                self.pushButton_3 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
                self.pushButton_3.setStyleSheet("QPushButton {\n"
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
                self.pushButton_3.setObjectName("pushButton_3")
                self.verticalLayout_6.addWidget(self.pushButton_3)
                self.pushButton_3.clicked.connect(self.calculate_g2)
                self.pushButton_4 = QtWidgets.QPushButton(self.verticalLayoutWidget_5)
                self.pushButton_4.setStyleSheet("QPushButton {\n"
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
                self.pushButton_4.setObjectName("pushButton_4")
                self.pushButton_4.clicked.connect(self.stop_g2)
                self.verticalLayout_6.addWidget(self.pushButton_4)
                MainWindow.setCentralWidget(self.centralwidget)
                self.menubar = QtWidgets.QMenuBar(MainWindow)
                self.menubar.setGeometry(QtCore.QRect(0, 0, 770, 24))
                self.menubar.setObjectName("menubar")
                MainWindow.setMenuBar(self.menubar)
                self.statusbar = QtWidgets.QStatusBar(MainWindow)
                self.statusbar.setObjectName("statusbar")
                MainWindow.setStatusBar(self.statusbar)

                self.retranslateUi(MainWindow)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

                self.plot_graph = pg.PlotWidget()
                self.plot_graph.setBackground("k")
                self.plot_graph.setLabel("left", "Valeur de la mesure")
                self.plot_graph.setLabel("bottom", "Temps (x1s)")
                self.plot_graph.setTitle("Affichage du calcul du g2 à deux détecteurs")
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
                self.pushButton_5.setText("Enregistrer l'image")
                self.pushButton_5.clicked.connect(self.save_plot)
                self.verticalLayout_6.addWidget(self.pushButton_5)


        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("MainWindow", "Interface g2 à deux détecteurs"))
                self.label_7.setText(_translate("MainWindow", "Calcul et affichage du g2"))
                self.label_8.setText(_translate("MainWindow", "Représentation graphique g2")) 
                self.label_2.setText(_translate("MainWindow", "Contrôle de la fenêtre du g2"))
                self.pushButton_3.setText(_translate("MainWindow", "Démarrer le calcul du g2"))
                self.pushButton_4.setText(_translate("MainWindow", "Stopper le calcul du g2"))

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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
