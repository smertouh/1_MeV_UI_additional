# coding: utf-8
'''
Created on Jan 3, 2020

@author: sanin
'''
import sys
import time
from PyQt5.QtWidgets import QCheckBox
from TangoWidgets.TangoWidget import TangoWidget


class TangoCheckBox(TangoWidget):
    def __init__(self, name, widget: QCheckBox, readonly=False):
        super().__init__(name, widget)
        if not readonly:
            self.widget.stateChanged.connect(self.callback)

    def set_widget_value(self):
        self.value = self.attr.value
        self.widget.setChecked(self.value)
        return self.value

    def decorate_error(self):
        self.widget.setStyleSheet('color: gray')
        self.widget.setEnabled(False)

    def decorate_invalid(self, text: str = None):
        self.widget.setStyleSheet('color: red')
        self.widget.setEnabled(True)

    def decorate_valid(self):
        self.widget.setStyleSheet('color: black')
        self.widget.setEnabled(True)

    def callback(self, value):
        if self.connected:
            try:
                self.dp.write_attribute(self.an, bool(value))
                self.decorate_valid()
            except:
                self.logger.debug('Exception %s in callback', exc_info=True)
                self.decorate_error()
        else:
            if time.time() - self.time > TangoWidget.RECONNECT_TIMEOUT:
                self.connect_attribute_proxy(self.attr_proxy)
            else:
                self.decorate_error()
