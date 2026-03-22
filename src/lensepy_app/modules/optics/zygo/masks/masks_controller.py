__all__ = ["ZygoMasksController"]

from PyQt6.QtWidgets import QWidget, QDialog
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.masks.masks_view import (
    MasksOptionsView, AddMaskView, MasksView)
from lensepy.optics.zygo.dataset import DataSet
from lensepy_app import *


class ZygoMasksController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        self.data_set : DataSet = self.parent.variables['dataset']
        self.first_image = self.data_set.get_image_from_set(1, 1)

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = AddMaskView()
        self.bot_right = QWidget()
        self.top_right = MasksOptionsView(self)

        # Setup widgets
        self.top_left.set_image_from_array(self.first_image)

        # Signals
        self.bot_left.mask_added.connect(self.handle_mask_added)
        self.top_right.masks_changed.connect(self.handle_mask_changed)

    def handle_mask_added(self, event):
        if '_masks' in event:
            if 'circular' in event:
                type = 'circular'
                help = 'Select 3 different points and then Click Enter'
                type_m = 'circ'
            elif 'rectangular' in event:
                type = 'rectangular'
                help = 'Select 2 different points (diagonal of the rectangle) and then Click Enter'
                type_m = 'rect'
            elif 'polygon' in event:
                type = 'polygon'
                help = ('Select N different points, the last one must be at the same place'
                        ' as the first one and then Click Enter')
                type_m = 'poly'
            dialog = MasksView(self.first_image, type, help)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                message_box('No mask added', 'No mask will be added to the list of masks.')
            else:
                mask = dialog.mask.copy()
                # Add mask to the data_set
                self.data_set.add_mask(mask, type_m)
                self.data_set.set_cropped_state(False)
                self.data_set.set_analyzed_state(False)
                self.data_set.set_wrapped_state(False)
                self.data_set.set_unwrapped_state(False)

                # Refresh list
                self.top_right.masks_list.update_display()


    def handle_mask_changed(self):
        mask = self.data_set.get_global_mask()
        if mask is not None:
            image_disp = self.first_image * mask
        else:
            image_disp = self.first_image
        self.top_left.set_image_from_array(image_disp)