__all__ = ["CIE1931Controller"]

from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from lensepy import translate

from lensepy_app.modules.optics.cie1931.cie1931_views import CIE1931MatplotlibWidget, CoordinateTableWidget
from lensepy_app.appli._app.template_controller import TemplateController


class CIE1931Controller(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.image_dir = self._get_image_dir(self.parent.parent.config['img_dir'])
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
        self.top_left.point_clicked.connect(
            self.top_right.open_add_dialog_with_coords
        )
        self.top_left.saved_chart.connect(self.handle_save_cie)

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

    def handle_save_cie(self):
        """Action performed when a PNG is required."""
        save_dir = self._get_file_path(self.image_dir, 'CIE_chart.png')
        if save_dir != '':
            self.top_left.save_image(save_dir)
        self.top_left.set_saving_activated(enabled=False)

    def _get_file_path(self, default_dir: str = '', default_name: str = '') -> str:
        """
        Open an image from a file.
        """
        file_dialog = QFileDialog()
        if default_name != '' and default_dir != '':
            new_dir = default_dir+"/"+default_name
        else:
            new_dir = default_dir
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            translate('dialog_save_cie_png'),
            new_dir,
            "Images (*.png)"
        )

        if file_path != '':
            return file_path
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return ''