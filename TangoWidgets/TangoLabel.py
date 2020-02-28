# coding: utf-8
'''
Created on Jan 3, 2020

@author: sanin
'''
from PyQt5.QtWidgets import QLabel
from TangoWidgets.TangoWidget import TangoWidget
import tango


class TangoLabel(TangoWidget):
    def __init__(self, name, widget: QLabel, prop=None, refresh=False):
        super().__init__(name, widget, readonly=True)
        self.property = prop
        if self.property is None:
            self.database = None
        else:
            self.database = tango.Database()
        self.property_value = None
        self.refresh = refresh

    def read_property(self):
        if self.database is None:
            self.database = tango.Database()
        self.property_value = self.database.get_device_attribute_property(self.attribute.device_name, self.attribute.attribute_name)[self.attribute.attribute_name][self.property][0]

    def read(self, force=False):
        if self.property is None:
            super().read()
            return
        if self.refresh or self.property_value is None:
            self.read_property()
        return

    def set_widget_value(self):
        if self.property is None:
            super().set_widget_value()
        else:
            self.widget.setText(str(self.property_value))

