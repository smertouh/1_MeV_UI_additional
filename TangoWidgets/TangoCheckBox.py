# coding: utf-8
'''
Created on Jan 3, 2020

@author: sanin
'''
import sys
import time

from PyQt5.QtWidgets import QCheckBox

from .Utils import *
from TangoWidgets.TangoWriteWidget import TangoWriteWidget
from TangoWidgets.TangoWidget import TangoWidget

import resources

class TangoCheckBox(TangoWriteWidget):
    def __init__(self, name, widget: QCheckBox, readonly=False):
        super().__init__(name, widget, readonly=readonly)
        if not readonly:
            self.widget.stateChanged.connect(self.callback)

    def set_widget_value(self):
        if self.readonly:
            return
        self.widget.setChecked(self.attr.value)

    def decorate_error(self):
        self.widget.setStyleSheet('color: gray')
        self.widget.setEnabled(False)

    def decorate_invalid(self, text: str = None):
        self.widget.setStyleSheet('QCheckBox::indicator:checked {\
            image:url(:/checkbox/TangoWidgets/images/checked_red.png);}')
        #checkBox_set_bg_color(self.widget, 'red')
        self.widget.setEnabled(True)

    def decorate_valid(self):
        self.widget.setStyleSheet('')
        #checkBox_set_bg_color(self.widget, 'black')
        self.widget.setEnabled(True)

    def compare(self):
        try:
            return int(self.attr.value) == self.widget.isChecked()
        except:
            self.logger.debug('Exception in CheckBox compare', exc_info=True)
            return False

    def callback(self, value):
        if self.connected:
            try:
                self.dp.write_attribute(self.an, bool(value))
                self.decorate_valid()
            except:
                self.logger.debug('Exception in CheckBox callback', exc_info=True)
                self.decorate_error()
        else:
            if time.time() - self.time > TangoWidget.RECONNECT_TIMEOUT:
                self.connect_attribute_proxy()
            self.decorate_error()
