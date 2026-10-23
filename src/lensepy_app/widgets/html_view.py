# -*- coding: utf-8 -*-
"""*html_view.py* file.

./views/html_view.py contains HTMLView class to display an HTML page.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QColor, QTextDocument
from PyQt6.QtWidgets import (
    QHBoxLayout, QWidget, QTextBrowser
)
from lensepy_app import *
from lensepy_app.appli import *


class HTMLView(ModuleWidget):
    """
    Widget displaying an HTML content.
    """

    def __init__(self, url: str = '', parent=None):
        """Default constructor.
        :param url: filepath or url to the HTML page. Default ''.
        """
        super().__init__(parent=parent)
        self.url = url

        self.view = QTextBrowser()
        self.view.setStyleSheet(f"background-color: {IMAGE_BG[self.global_theme]};")
        # self.view.page().setBackgroundColor(QColor(IMAGE_BG[self.global_theme]))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        if url != '':
            print(f'HTML URL = {url}')
            self.set_url(self.url)

        #self.view.loadFinished.connect(self.on_load_finished)

    def set_url(self, url: str, css_path=''):
        """
        Set the URL of the mini browser.
        :param url: filepath or url to the HTML page.
        """
        self.url = url

        path = Path(url).resolve()
        print(f'Path = {path} / url = {url}')
        base_url = QUrl.fromLocalFile(str(path.parent) + "/")

        print(f'Base URL = {base_url}')

        with path.open("r", encoding="utf-8") as f:
            html = f.read()

        self.view.document().setBaseUrl(base_url)
        self.view.setHtml(html)

    def on_load_finished(self, ok):
        if not ok:
            return

        self.view.page().runJavaScript("""
            document.documentElement.style.setProperty(
                'background-color', '#2b2b2b', 'important'
            );
    
            document.body.style.setProperty(
                'background-color', '#2b2b2b', 'important'
            );
        """)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_widget = HTMLView(url='../docs/html/camera.html')
    main_widget.setGeometry(100, 100, 400, 600)
    main_widget.show()

    sys.exit(app.exec())