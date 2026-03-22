# -*- coding: utf-8 -*-
"""*html_view.py* file.

./views/html_view.py contains HTMLView class to display an HTML page.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
from PyQt6.QtWidgets import (
    QWidget, QTextEdit,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


class HTMLView(QWidget):
    """
    Widget displaying an HTML content.
    """

    def __init__(self, url: str = '', css: str = ''):
        """Default constructor.
        :param url: filepath or url to the HTML page. Default ''.
        """
        super().__init__()
        self.url = url
        self.css = css
        self.html_page = QTextEdit()
        self.html_page.setReadOnly(True)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.html_page)
        self.setLayout(self.layout)
        if url != '':
            self.set_url(self.url, self.css)

    def set_url(self, url: str, css: str = ''):
        """
        Set the URL of the mini browser.
        :param url: filepath or url to the HTML page.
        :param css: filepath to a css file. Default ''.
        """
        self.url = url
        self.css = css

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


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_widget = HTMLView(url='../docs/html/camera.html', css='../docs/html/styles.css')
    main_widget.setGeometry(100, 100, 400, 600)
    main_widget.show()

    sys.exit(app.exec())