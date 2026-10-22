__all__ = ["ZygoMasksController"]

from PyQt6.QtWidgets import QWidget, QDialog

from lensepy_app.appli._app.template_controller import TemplateController
from lensepy_app.widgets.image_display_widget import ImageDisplayWidget
from lensepy_app.modules.optics.fizeau.maskslite.maskslite_view import (
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
        self.check_first_mask = True
        if self.get_variables('dataset') is not None:
            self.masks = self.get_variables('dataset').get_masks_set()
        else:
            self.masks = MasksSet()
            self.masks.reset_masks()
            self.set_variables('masks', self.masks)

        '''
        TO DELETE
        import cv2
        file_path = '../lensepy-data/optics/fizeau/interference.png'
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        self.manager.variables['image'] = image
        END DELETE
        '''

        self.first_image = self.get_variables('dataset').get_image_from_set(1,1)
        print(f'First Image = {self.first_image.shape}')
        theme = self.manager.controller.get_config('global_theme')
        # Graphical layout
        self.top_left = ImageDisplayWidget(self, bg_color=IMAGE_BG[theme])
        self.bot_left = AddMaskView(self)
        self.bot_right = QWidget()
        self.top_right = MasksOptionsView(self)

        # Setup widgets
        if self.get_variables('bits_depth') is not None:
            self.top_left.set_bits_depth(self.get_variables('bits_depth'))
        self.top_left.set_image_from_array(self.first_image)
        if self.masks is not None :
            if self.masks.get_masks_number() != 0:
                #self.set_variables('mask_loaded', True)
                self.manager.update_menu()
        if self.masks.get_masks_number() == 0 :
            self.bot_left.set_enabled_check(False)
        else:
            self.bot_left.set_enabled_check(True)
            self.bot_left.set_checked_check(True)
            self.handle_mask_changed()
        # Signals
        self.bot_left.mask_added.connect(self.handle_mask_added)
        self.top_right.masks_changed.connect(self.handle_mask_changed)

    def handle_mask_added(self, event):
        if 'update' in event:
            self.set_variables("masks", self.masks)
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

            if self.get_variables('bits_depth') == 12:
                image = self.first_image // 16
            else:
                image = self.first_image
            if self.bot_left.is_mask_displayed():
                mask = self.masks.get_global_mask()
                image = image * mask
            dialog = MasksView(image, type, help, parent=self)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                message_box('No mask added', 'No mask will be added to the list of masks.')
            else:
                mask = dialog.mask.copy()
                # Add mask to the data_set
                self.masks.add_mask(mask, type_m)
                self.set_variables("mask", self.masks.get_global_mask())
                self.set_variables("masks", self.masks)
                self.manager.update_menu()

                # Refresh list
                self.top_right.masks_list.update_display()
                self.handle_mask_changed()

    def handle_mask_changed(self):
        nb_mask = self.masks.get_masks_number()
        if nb_mask != 0:
            mask = self.masks.get_global_mask()
            mask_disp = False
            if mask is None:
                self.check_first_mask = True
                self.bot_left.set_checked_check(False)
                self.bot_left.set_enabled_check(False)
            elif self.check_first_mask and mask is not None:
                self.check_first_mask = False
                self.bot_left.set_checked_check(True)
                self.bot_left.set_enabled_check(True)
                mask_disp = True
            else:
                mask_disp = self.bot_left.is_mask_displayed()
                self.bot_left.set_enabled_check(True)
            if mask is not None and mask_disp:
                image_disp = self.first_image * mask
            else:
                #self.parent.variables['mask_loaded'] = None
                self.manager.update_menu()
                image_disp = self.first_image
        else:
            self.check_first_mask = True
            self.set_variables('mask', None)
            self.bot_left.set_checked_check(False)
            self.bot_left.set_enabled_check(False)
            self.manager.update_menu()
            image_disp = self.first_image
        #

        self.top_left.set_image_from_array(image_disp)
        self.top_left.repaint()