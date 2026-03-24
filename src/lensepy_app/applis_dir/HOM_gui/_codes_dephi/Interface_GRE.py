from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont, QIcon
import interface_main
#from class_piezo import *


class Interface_GRE():
    def __init__(self):
        self.FirstWindow = QtWidgets.QMainWindow()
        self.w = interface_main.Ui_MainWindow()
        self.w.setupUi(self.FirstWindow)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #test1 = test()
    #test1.test_window.show()
    GRE = Interface_GRE()
    GRE.FirstWindow.show()
    sys.exit(app.exec_())
    