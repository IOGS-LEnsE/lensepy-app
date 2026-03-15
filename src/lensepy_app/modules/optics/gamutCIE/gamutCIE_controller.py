__all__ = ["GamutCIEController"]

from PyQt6.QtWidgets import QWidget

from lensepy_app.modules.optics.gamutCIE.gamutCIE_views import GamutCIEMatplotlibWidget, GamutTableWidget
from lensepy_app.appli._app.template_controller import TemplateController


class GamutCIEController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = GamutCIEMatplotlibWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = GamutTableWidget()
        # Update list of points if exists
        if isinstance(self.parent.variables['points_list'], dict):
            self.points_list = self.parent.variables['points_list']
            for key in self.points_list:
                point = self.points_list[key]
                [x, y] = point.get_coords()
                name = point.get_name()
                self.top_right.add_point(name, x, y)
        else:
            self.points_list = {}

        # Setup widgets
        self.top_left.update_list(self.points_list)
        # Signals
        self.top_right.point_added.connect(self.handle_point_added)
        self.top_right.point_deleted.connect(self.handle_point_deleted)
        self.top_left.point_clicked.connect(
            self.top_right.open_add_dialog_with_coords
        )

    def handle_point_added(self, data):
        """Action performed when a new point is added."""
        self.points_list[data.get_name()] = data
        self.parent.variables['points_list'] = self.points_list
        # Update graph ?
        self.top_left.update_list(self.points_list)

    def handle_point_deleted(self, data):
        """Action performed when a point is deleted."""
        self.points_list.pop(data.get_name(), None)
        self.parent.variables['points_list'] = self.points_list
        # Update graph ?
        self.top_left.update_list(self.points_list)


