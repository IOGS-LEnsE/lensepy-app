from lensepy.appli.VI_gui.machine_vision_gui import *

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