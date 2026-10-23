import importlib
import os.path
from lensepy_app.appli.start_app import start_app

if __name__ == "__main__":
    app_path = os.path.dirname(__file__)
    start_app(app_path, True)