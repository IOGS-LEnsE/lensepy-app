import sys, os
import xml.etree.ElementTree as ET


class XMLFileConfig:

    def __init__(self, xml_file: str):
        """

        :param xml_file:    File path of the XML file.
        """
        if os.path.isfile(xml_file):
            self.xml_file = xml_file
        else:
            self.xml_file = None

    def get_parameter_xml(self, parameter):
        """

        :param parameter:   Name of the node inside the XML file.
        :return:        Value of the parameter.
        """
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            param_value = xml_root.find(parameter)
            if param_value is not None:
                return param_value.text
        return None

    def get_app_name(self):
        """

        :return:    Name of the application from the XML file.
        """
        return self.get_parameter_xml('name')

    def get_app_desc(self):
        """

        :return:    Description of the application from the XML file.
        """
        return self.get_parameter_xml('description')

    def get_html_page(self):
        """

        :return:    Description of the application from the XML file.
        """
        return self.get_parameter_xml('html_page')

    def get_img_desc(self):
        """

        :return:    Path to the image of the application from the XML file.
        """
        return self.get_parameter_xml('img_desc')

    def get_list_modules(self):
        """

        :return:
        """
        modules_list = []
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            modules = xml_root.findall('module')
            for module in modules:
                modules_list.append(module.find('name').text)
        return modules_list

    def get_variables(self):
        """
        Get a dictionnary of variables.
        :return:
        """
        variables_list = {}
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            variables = xml_root.findall('variable')
            for var_ in variables:
                name = var_.get("name")
                value = var_.text  # sera None si vide
                variables_list[name] = value if value is not None else None
        return variables_list

    def get_module_path(self, module_name: str):
        """

        :param module_name: Name of the module
        :return:
        """
        modules_list = []
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            modules = xml_root.findall('module')
            for module in modules:
                if module.find('name').text == module_name:
                    module_path = module.find('location').text
                    return module_path
        return None

    def get_module_parameter(self, module_name: str, parameter: str):
        """

        :param module_name: Name of the module.
        :param parameter: Name of the parameter to get.
        :return:
        """
        modules_list = []
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            modules = xml_root.findall('module')
            for module in modules:
                if module.find('name').text == module_name:
                    if module.find(parameter) is not None:
                        return module.find(parameter).text
        return None

    def get_sub_parameter(self, parameter: str, sub_parameter: str):
        """
        Get a sub parameter in the XML config file.
        :param parameter:       Name of the parameter to get.
        :param sub_parameter:    Name of the sub paramter to get.
        :return:    Value of the sub parameter.
        """
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            module = xml_root.find(parameter)
            return module.find(sub_parameter).text
        return None

    def get_xml_file(self):
        """

        :return:
        """
        return self.xml_file


class XMLFileModule:

    def __init__(self, xml_file: str):
        """

        :param xml_file:    File path of the XML file.
        """
        if os.path.isfile(xml_file):
            self.xml_file = xml_file
        else:
            self.xml_file = None

    def get_parameter_xml(self, parameter):
        """

        :param parameter:   Name of the node inside the XML file.
        :return:        Value of the parameter.
        """
        if self.xml_file is not None:
            tree = ET.parse(self.xml_file)
            xml_root = tree.getroot()
            param_value = xml_root.find(parameter)
            if param_value is not None:
                return param_value.text
        return None


if __name__ == "__main__":
    pass
