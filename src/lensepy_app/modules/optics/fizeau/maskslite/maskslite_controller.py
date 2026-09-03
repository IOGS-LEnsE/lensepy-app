__all__ = ["ZygoMasksController"]

from PyQt6.QtWidgets import QWidget, QDialog
from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.zygo.masks.masks_view import (
    MasksOptionsView, AddMaskView, MasksView)
from lensepy.optics.zygo.dataset import MasksSet, DataSet
from lensepy_app import *


class ZygoMasksController(TemplateController):
    """

    """

    def __init__(self, parent=None):
        """

        """
        super().__init__(parent)
        if self.parent.variables['masks'] is not None:
            self.masks : MasksSet = self.parent.variables['masks']
        else:
            self.masks = MasksSet()
            self.masks.reset_masks()
            self.parent.variables['masks'] = self.masks
        self.first_image = self.parent.variables['image']

        # Graphical layout
        self.top_left = ImageDisplayWidget()
        self.bot_left = AddMaskView()
        self.bot_right = QWidget()
        self.top_right = MasksOptionsView(self)

        # Setup widgets
        if self.parent.variables['bits_depth'] is not None:
            self.top_left.set_bits_depth(self.parent.variables['bits_depth'])
        self.top_left.set_image_from_array(self.first_image)
        if self.masks is not None :
            if self.masks.get_masks_number() != 0:
                self.parent.variables['mask_loaded'] = True
                self.parent.update_menu()
        # Signals
        self.bot_left.mask_added.connect(self.handle_mask_added)
        self.top_right.masks_changed.connect(self.handle_mask_changed)

    def handle_mask_added(self, event):
        if 'update' in event:
            self.handle_mask_changed()
        elif '_masks' in event:
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

            if self.parent.variables['bits_depth'] == 12:
                image = self.first_image // 16
            else:
                image = self.first_image
            if self.bot_left.is_mask_displayed():
                mask = self.masks.get_global_mask()
                image = image * mask
            dialog = MasksView(image, type, help)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                message_box('No mask added', 'No mask will be added to the list of masks.')
            else:
                mask = dialog.mask.copy()
                # Add mask to the data_set
                self.masks.add_mask(mask, type_m)
                self.parent.variables["mask"] = self.masks.get_global_mask()
                self.parent.update_menu()

                # Refresh list
                self.top_right.masks_list.update_display()
            self.handle_mask_changed()

    def handle_mask_changed(self):
        mask_disp = self.bot_left.is_mask_displayed()
        mask = self.masks.get_global_mask()
        if mask is not None and mask_disp:
            image_disp = self.first_image * mask
        else:
            self.parent.variables['mask_loaded'] = None
            self.parent.update_menu()
            image_disp = self.first_image
        self.top_left.set_image_from_array(image_disp)