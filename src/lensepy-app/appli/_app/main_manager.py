import sys, os
import lensepy
from pathlib import Path
from lensepy.appli._app.app_utils import XMLFileConfig, XMLFileModule
from lensepy.appli._app.main_view import MainWindow
import importlib
from lensepy.modules.default.default_controller import DefaultController

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lensepy.appli.VI_gui.machine_vision_gui import My_Application


class MainManager:
    """
    Main widget/application manager.
    """
    def __init__(self, parent=None):
        self.parent: My_Application = parent    # Parent application
        self.main_window: MainWindow = MainWindow(self)     # Main window management
        self.main_window.menu_changed.connect(self.handle_menu_changed)
        self.controller = None
        self.xml_app: XMLFileConfig = None     # XML file containing application parameters
        self.xml_module: XMLFileModule = None
        self.list_modules = {}
        self.list_modules_name = []      # List of the required modules
        self.actual_module = 'default'
        self.app_title = ''         # Title of the application
        self.app_logo = ''          # Logo (filepath) to display of the application
        self.variables = {}         # Application variables
        self.req_variables = {}     # Required variables for each module (separated by ',')

    def set_xml_app(self, xml_app):
        """

        :param xml_app:     Filepath of the XML file containing app parameters.
        :return:    True if file exists, else False.
        """
        if os.path.exists(xml_app):
            self.xml_app = XMLFileConfig(xml_app)
            self.app_logo = self.xml_app.get_parameter_xml('logo') or ''
            if './' not in self.app_logo:
                root_path = os.path.dirname(lensepy.__file__)
                self.app_logo = f'{root_path}/{self.app_logo}'
            self.app_title = self.xml_app.get_parameter_xml('appname') or ''
            if self.init_variables():
                self.list_modules_name = self.xml_app.get_list_modules()
                self.req_variables = self.get_module_required_variables()
                return self.init_main_menu()
            return False
        else:
            return False

    def init_variables(self) -> bool:
        """
        Initialize variables from application XML file.
        :return:
        """
        if self.xml_app is not None:
            self.variables = self.xml_app.get_variables()
            return True
        return False

    def init_main_menu(self):
        """
        Initialize the main menu from the module list in the application XML file.
        :return:
        """
        if self.xml_app is not None:
            self.main_window.set_menu_elements(self.list_modules_name)
            if self.actual_module == 'default':
                self.init_controller()
            return True
        else:
            return False

    def init_controller(self):
        package_root = os.path.dirname(lensepy.__file__)
        if self.actual_module == 'default':
            lensepy_path = (os.path.dirname(lensepy.__file__))
            xml_path = lensepy_path +'/modules/default/default.xml'
            self.xml_module = XMLFileModule(xml_path)
            self.controller = DefaultController(self)
        else:
            # Delete old controller
            if self.controller is not None:
                if hasattr(self.controller, "cleanup"):
                    self.controller.cleanup()
            # Find controller for actual module
            module_path = self.xml_app.get_module_path(self.actual_module)
            if module_path.startswith('./'):
                path_name = str(module_path)
                sys.path.append(path_name)
                module_path = ''
            else:
                module_path += '.'
            module_path += f'{self.actual_module}'
            module = importlib.import_module(module_path, package=__package__)
            xml_path = os.path.dirname(module.__file__)
            xml_path += f'/{self.actual_module}.xml'
            self.xml_module = XMLFileModule(xml_path)
            controller_name = self.xml_module.get_parameter_xml('controller')
            controller_class = getattr(self.list_modules[self.actual_module], controller_name)
            self.controller = controller_class(self)
        self.controller.init_view()

    def init_list_modules(self):
        """
        Get a list of modules to include in the application.
        :return:
        """
        # Importation of modules
        for module in self.list_modules_name:
            module_path = self.xml_app.get_module_path(module)
            if './' in module_path:
                module_path_n = module_path.lstrip("./").replace("/", ".")
                self.list_modules[module] = importlib.import_module(f'{module_path_n}.{module}')
            else:
                self.list_modules[module] = importlib.import_module(f'{module_path}.{module}')

    def get_module_required_variables(self):
        """
        Collect all the required variables for each module of the application.
        :return:    list of the required variables.
        """
        var_list = {}
        for module in self.list_modules_name:
            module_path = self.xml_app.get_module_path(module)
            if './' in module_path:
                # external module
                module_path_n = module_path.lstrip("./").replace("/", ".")
                xml_path = f'{module_path}/{module}/{module}.xml'
            else:
                # lensepy module
                module_path = f'{module_path}.{module}'
                module_i = importlib.import_module(module_path)
                xml_path = f'{os.path.dirname(module_i.__file__)}/{module}.xml'
            xml_module = XMLFileModule(xml_path)
            var_module_list = xml_module.get_parameter_xml('req_var')
            var_list[module] = var_module_list
        return var_list

    def check_module_requirements(self, module):
        """
        Check if the module parameter 'requirements' is set.
        :param module:      Name of the module.
        :return:            True if module parameter 'requirements' is set, else False.
        """
        module_path = self.xml_app.get_module_path(module)
        if './' in module_path:
            module_path_n = module_path.lstrip("./").replace("/", ".")
            xml_path = f'{module_path}/{module}/{module}.xml'
            xml_module = XMLFileModule(xml_path)
            req_module = xml_module.get_parameter_xml('requirements')
            return req_module is None
        elif module_path != '':
            # lensepy module
            module_path = f'{module_path}.{module}'
            module_i = importlib.import_module(module_path)
            xml_path = f'{os.path.dirname(module_i.__file__)}/{module}.xml'
            xml_module = XMLFileModule(xml_path)
            req_module = xml_module.get_parameter_xml('requirements')
            return req_module is None
        return False

    def get_variable(self, name):
        """
        Get a variable in the config list by its name.
        :param name:    Name of the variable.
        :return:        Value of the variable.
        """
        if name in self.variables:
            return self.variables[name]
        else:
            return None

    def update_menu(self):
        """Update the main menu of the application."""
        self.main_window.update_menu()

    def handle_menu_changed(self, event):
        """
        Action performed when menu changed.
            Check if the module exists
        :param event:
        """
        # Load module and initialize views
        self.actual_module = event
        self.init_controller()


