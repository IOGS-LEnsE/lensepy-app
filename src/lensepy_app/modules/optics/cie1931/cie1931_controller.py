__all__ = ["CIE1931Controller"]

from PyQt6.QtWidgets import QWidget

from lensepy.modules.optics.cie1931.cie1931_views import CIE1931MatplotlibWidget, CoordinateTableWidget
from lensepy.appli._app.template_controller import TemplateController


class CIE1931Controller(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)

        # Graphical layout
        self.top_left = CIE1931MatplotlibWidget()
        self.bot_left = QWidget()
        self.bot_right = QWidget()
        self.top_right = CoordinateTableWidget()
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

    def handle_point_added(self, data):
        """Action performed when a new point is added."""
        self.points_list[data.get_name()] = data
        self.parent.variables['points_list'] = self.points_list
        # Update graph ?
        self.top_left.update_list(self.points_list)

    def handle_point_deleted(self, data):
        """Action performed when a point is deleted."""
        self.points_list.pop(data.get_name())
        self.parent.variables['points_list'] = self.points_list
        # Update graph ?
        self.top_left.update_list(self.points_list)