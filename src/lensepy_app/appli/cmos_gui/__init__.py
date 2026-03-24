
def init_app(application):
    xml_data = application.manager.xml_app

    print(f'XML_DATA = {xml_data}')

    init_file = xml_data.get_sub_parameter('camera', 'init_file')
    application.config['camera_ini'] = f'{application.appli_root}/{init_file}'
    application.config['img_dir'] = xml_data.get_parameter_xml('img_dir') or None
