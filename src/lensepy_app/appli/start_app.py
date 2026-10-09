import sys, os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

import lensepy_app
from lensepy import translate, load_dictionary, dictionary

from lensepy_app.modules.default.default_controller import DefaultController
from lensepy_app.appli._app.app_utils import XMLFileConfig, XMLFileModule
from lensepy_app.appli._app.main_manager import MainManager
from PyQt6.QtWidgets import QApplication
import importlib
import importlib.util

DEFAULT_LANG = 'FR'

os.environ["QSG_RHI_BACKEND"] = "opengl"   # avant QApplication

# Palette sombre
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)


class My_Application(QApplication):

    def __init__(self, app_name=None, standalone=False, argv=None):
        if argv is None:
            argv = sys.argv
        super().__init__(argv)
        self.manager = MainManager(self)
        self.window = self.manager.main_window
        self.standalone = standalone
        self.package_root = os.path.dirname(lensepy_app.__file__)
        self.app_name = app_name
        self.appli_root = None
        if not self.standalone:
            self.appli_root = os.path.dirname(os.path.abspath(__file__))
            self.appli_root = os.path.dirname(self.appli_root)
            self.appli_root += f'/applis_dir/{app_name}'
        else:
            if app_name is not None:
                self.appli_root = f'{app_name}'
            else:
                return

        self.config_name = f'{self.appli_root}/config/appli.xml'
        # Parser for options
        self.config_ok = False
        self.config = {}
        self.initial_params = {}
        # Dependencies
        self.required_modules = []
        self.missing_modules = []
        self.error_modules = []

    def init_config(self):
        self.check_options()    # Change config_name if necessary
        self.config_ok = self.manager.set_xml_app(self.config_name)

        xml_data: XMLFileConfig = self.manager.xml_app
        if self.config_ok:
            self.config['global_theme'] = xml_data.get_parameter_xml('theme')
            if self.config['global_theme'] == 'BLACK':
                print(f'BLACK theme')
                self.setPalette(palette)
            self.config['open_gl'] = xml_data.get_parameter_xml('open_gl')
            app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            app_path += '/applis_dir/'
            self.config['general_mode'] = xml_data.get_parameter_xml('mode')
            self.config['theme'] = xml_data.get_parameter_xml('theme')
            self.config['default_lang'] = xml_data.get_parameter_xml('default_langage')
            if self.config['default_lang'] is None:
                self.config['default_lang'] = DEFAULT_LANG
            load_dictionary(f'{self.appli_root}/lang/{self.config["default_lang"]}.txt')
            self.manager.update_menu()
            self.config['name'] = xml_data.get_app_name() or None
            self.config['description'] = xml_data.get_app_desc() or None
            self.config['img_desc'] = xml_data.get_img_desc() or None
            if self.config['img_desc'] is not None:
                self.config['img_desc'] = app_path + self.config['img_desc']
            self.config['html'] = xml_data.get_html_page() or None
            if self.config['html'] is not None:
                if self.config['html'].startswith('http'):
                    app_path = ''
                self.config['html'] = app_path + self.config['html']
            self.config['organization'] = xml_data.get_parameter_xml('organization') or None
            self.config['year'] = xml_data.get_parameter_xml('year') or None
            self.config['img_dir'] = xml_data.get_parameter_xml('img_dir') or None
            # Init Camera if exists
            self.config['camera_ini'] = xml_data.get_sub_parameter('camera', 'init_file')
            if isinstance(self.manager.controller, DefaultController):
                self.manager.controller.display()
            self.manager.main_window.update_general_display()
            self.manager.update_menu()
            return True
        else:
            return False

    def init_params(self):
        xml_data: XMLFileConfig = self.manager.xml_app
        if self.config_ok:
            self.initial_params = xml_data.list_sub_parameter('init_params', '')
            return True
        else:
            return False

    def check_options(self):
        if not self.standalone:
            path = f'applis_dir.{self.app_name}'
            module = importlib.import_module(path)
            module.init_app(self)

    def init_app(self):
        self.manager.init_list_modules()

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        if self.config_ok:
            modules_list = self.manager.xml_app.get_list_modules()
            # List the missing modules
            for module in modules_list:
                module_path = self.manager.xml_app.get_module_path(module)
                if './' in module_path:
                    module_path_n = module_path.lstrip("./").replace("/", ".")
                    path_module = f'{module_path_n}.{module}'
                else:
                    path_module = f'{module_path}.{module}'
                try:
                    if importlib.util.find_spec(path_module) is None:
                        self.missing_modules.append(module)
                except ModuleNotFoundError:
                    self.error_modules.append(module)
            # List the required modules
            for module in modules_list:
                req_module = self.manager.xml_app.get_module_parameter(module, 'requirements')
                if req_module is not None:
                    req_module = req_module.split(',')
                    for r_module in req_module:
                        rr_module = r_module.split('/')
                        if len(rr_module) == 1:
                            if r_module not in modules_list:
                                self.required_modules.append(r_module)
                        else:
                            counter_req = 0
                            for rrr_module in rr_module:
                                if rrr_module in modules_list:
                                    counter_req = counter_req + 1
                            if counter_req == 0:
                                self.required_modules.append(r_module)

            # Output
            if len(self.missing_modules) == 0 and len(self.required_modules) == 0 and len(self.error_modules) == 0:
                return True
            else:
                return False
        return False

    def show(self):
        # Create main window title
        title = f''
        if self.config.get('name'):
            title += f'{self.config["name"]}'
        if self.config.get('organization'):
            title += f' / {self.config["organization"]}'
        if self.config.get('year'):
            title += f' - {self.config["year"]}' or ''
        # Display Main Window
        self.window.setWindowTitle(f'{title}')
        self.window.showMaximized()


def start_app(app_path, standalone=False, argv=None):
    if standalone:
        print('Standalone')
        app = My_Application(app_path, standalone)
    else:
        app = My_Application(app_path, argv=argv)

    if app.init_config():
        if app.check_dependencies():
            app.init_params()
            app.init_app()
            app.show()
            sys.exit(app.exec())
        else:
            print('Module dependencies failed.')
            if len(app.error_modules) != 0:
                print(f'Module errors: {app.error_modules} / Check the configuration of these modules.')
            if len(app.required_modules) != 0:
                print(f'Required modules: {app.required_modules} / These modules are required.')
            if len(app.missing_modules) != 0:
                print(f'Missing modules: {app.missing_modules} / These modules are not installed.')
            return
    else:
        print('Failed')
        return


if __name__ == "__main__":
    if len(sys.argv) > 1:
        application_name = sys.argv[1]
        start_app(application_name, standalone=False, argv=sys.argv)
    else:
        # Display all app
        path_to_app = Path("./")

        for element in path_to_app.iterdir():
            if element.is_dir() and not element.name.startswith('_'):
                print(f'Element Name : {element.name}')
