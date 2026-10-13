# -*- coding: utf-8 -*-
"""*html_view.py* file.

./views/html_view.py contains HTMLView class to display an HTML page.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from lensepy_app import *
from lensepy_app.appli import *

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-direct-composition"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


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
        self.view = QWebEngineView()
        self.view.setStyleSheet(f"background-color: {IMAGE_BG[self.global_theme]};")
        self.view.page().setBackgroundColor(QColor(IMAGE_BG[self.global_theme]))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        if url != '':
            self.set_url(self.url)

        self.view.loadFinished.connect(self.on_load_finished)

    def set_url(self, url: str):
        """
        Set the URL of the mini browser.
        :param url: filepath or url to the HTML page.
        :param css: filepath to a css file. Default ''.
        """
        self.url = url
        print(url)
        if url.startswith('http'):
            self.view.setUrl(QUrl(url))
        else:
            self.view.setUrl(QUrl.fromLocalFile(self.url))

        '''
        if self.url != '':
            css_content = ''
            if os.path.exists(self.url):
                with open(url, "r", encoding="utf-8") as file:
                    html_content = file.read()
                if self.css != '':
                    with open(css, "r", encoding="utf-8") as file:
                        css_content = file.read()

                full_html_content = f"""
                <html>
                <head>
                    <style>
                    {css_content}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """

                self.html_page.setHtml(full_html_content)
        '''

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