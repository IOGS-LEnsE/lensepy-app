import os

import cv2
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QGuiApplication
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.modules.default.default_views import *
from lensepy_app.widgets import ImageDisplayWidget
from lensepy_app.widgets.html_view import HTMLView
from lensepy import load_dictionary, translate

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _app.main_manager import MainManager

class DefaultController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(None)
        self.parent = parent # main manager
        self.name = 'DefaultController'
        self.top_left = HTMLView()
        self.top_left.hide()
        self.top_right = ImageDisplayWidget(self)
        self.top_right.hide()
        self.bot_left = DefaultTopLeftWidget(self)
        self.bot_right = DefaultBotRightWidget(self)

    def display(self):
        config = self.parent.parent.config
        if 'default_lang' in config:
            load_dictionary(f"{os.path.dirname(__file__)}/lang/{config['default_lang']}.txt")
            self.bot_right.init_ui()
        if 'html' in config:
            if config['html'] is not None:
                self.top_left.show()
                url = config['html']
                self.top_left.set_url(url)
        if 'img_desc' in config:
            if config['img_desc'] is not None:
                self.top_right.show()
                image = cv2.imread(config['img_desc'])
                self.top_right.set_image_from_array(image)
                self.top_right.update()
        self.update_view()

        self.bot_left.display(config)

    def get_contributors_by_type(self):
        """Return a list of contributors based on type : dev, sciexp"""
        return self.parent.get_xml_contributors()

'''
import xml.etree.ElementTree as ET

# Charger le fichier XML
tree = ET.parse("mon_fichier.xml")  # remplace par le chemin réel
root = tree.getroot()

# Dictionnaire pour stocker les contributeurs par type
contributors_by_type = {}

# Parcourir tous les contributeurs
for contributor in root.findall("./contributors/contributor"):
    ctype = contributor.get("type")
    name = contributor.findtext("name")

    # Ajouter au dictionnaire
    if ctype not in contributors_by_type:
        contributors_by_type[ctype] = []
    contributors_by_type[ctype].append(name)

# Afficher le résultat
for ctype, names in contributors_by_type.items():
    print(f"{ctype}: {names}")
'''