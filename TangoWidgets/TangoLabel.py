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
        self.property = prop
        self.property_value = None
        self.refresh = refresh
        super().__init__(name, widget, readonly=True)

    def read(self, force=False):
        if self.property is None:
            super().read()
            return
        if self.attr is None:
            super().read()
        if self.refresh or self.property_value is None:
            db = tango.Database()
            self.property_value = db.get_device_attribute_property(self.dn, self.an)[self.an][self.property][0]
            #self.property_value = self.dp.get_property(self.an, self.property)[self.property][0]
        return self.attr

    def set_widget_value(self):
        if self.property is None:
            super().set_widget_value()
        else:
            self.widget.setText(self.property_value)

