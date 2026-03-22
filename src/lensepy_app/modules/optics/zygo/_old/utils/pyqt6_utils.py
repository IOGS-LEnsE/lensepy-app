# -*- coding: utf-8 -*-
"""*pyqt6_utils.py* file.

./utils/pyqt6_utils.py contains tools for views.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout,
    QMessageBox, QFileDialog, QDialog
)

def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)

def message_box(warning="Warning - No File Loaded", text=""):
    """Open a warning dialog box."""
    dlg = QMessageBox()
    dlg.setWindowTitle(warning)
    dlg.setText(text)
    dlg.setStandardButtons(
        QMessageBox.StandardButton.Ok
    )
    dlg.setIcon(QMessageBox.Icon.Warning)
    return dlg.exec()

