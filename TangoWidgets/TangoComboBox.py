# coding: utf-8
'''
Created on Jan 3, 2020

@author: sanin
'''
import sys
import time

from PyQt5.QtWidgets import QComboBox

from TangoWidgets.TangoWriteWidget import TangoWriteWidget
from TangoWidgets.TangoWidget import TangoWidget


class TangoComboBox(TangoWriteWidget):
    def __init__(self, name, widget: QComboBox, readonly=False):
        super().__init__(name, widget)
        self.widget.currentIndexChanged.connect(self.callback)

    def decorate_error(self):
        self.widget.setStyleSheet('color: red')

    def update(self, decorate_only=False):
        super().update(decorate_only)

    def set_widget_value(self):
        #bs = self.widget.blockSignals(True)
        try:
            self.widget.setCurrentIndex(int(self.attr.value))
        except:
            pass
        #self.widget.blockSignals(bs)
        return self.attr.value

    def compare(self):
        try:
            return int(self.attr.value) == self.widget.currentIndex()
        except:
            self.logger.debug('Exception in ComboBox compare', exc_info=True)
            return False

    def callback(self, value):
        if self.connected:
            try:
                self.dp.write_attribute(self.an, int(value))
                self.decorate_valid()
            except:
                self.logger.debug('Exception %s in callback', sys.exc_info()[0])
                self.decorate_error()
        else:
            if time.time() - self.time > TangoWidget.RECONNECT_TIMEOUT:
                self.connect_attribute_proxy()
            self.decorate_error()
