from lensepy_app.appli._app.template_controller import TemplateController
from .my_module_views import MyModuleTopLeftWidget, MyModuleBotLeftWidget

class MyModuleController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.top_left = MyModuleTopLeftWidget()
        self.bot_left = MyModuleBotLeftWidget()


        