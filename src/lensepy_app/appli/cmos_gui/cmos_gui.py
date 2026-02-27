import sys, os
import lensepy
from lensepy import translate, load_dictionary, dictionary

from lensepy.appli._app.app_utils import XMLFileConfig, XMLFileModule
from lensepy.appli._app.main_manager import MainManager
from PyQt6.QtWidgets import QApplication
import importlib
import importlib.util


class My_Application(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        self.manager = MainManager(self)
        self.window = self.manager.main_window
        self.package_root = os.path.dirname(lensepy.__file__)
        appli_root = os.path.dirname(os.path.abspath(__file__))
        self.config_name = f'{appli_root}/config/appli.xml'
        self.config_ok = False
        self.config = {}
        # Dependencies
        self.required_modules = []
        self.missing_modules = []
        self.error_modules = []
        load_dictionary(f'{appli_root}/lang/FR.txt')

    def init_config(self):
        self.config_ok = self.manager.set_xml_app(self.config_name)
        xml_data: XMLFileConfig = self.manager.xml_app
        if self.config_ok:
            self.config['name'] = xml_data.get_app_name() or None
            self.config['organization'] = xml_data.get_parameter_xml('organization') or None
            self.config['year'] = xml_data.get_parameter_xml('year') or None
            appli_root = os.path.dirname(os.path.abspath(__file__))
            self.config['camera_ini'] = f'{appli_root}/config/camera.ini'
            self.config['camera_ini'] = f'{appli_root}/config/camera_small.ini'
            self.config['img_dir'] = xml_data.get_parameter_xml('img_dir') or None
            return True
        else:
            return False

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


def main():
    app = My_Application(sys.argv)
    if app.init_config():
        if app.check_dependencies():
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
        return


if __name__ == "__main__":
    main()
