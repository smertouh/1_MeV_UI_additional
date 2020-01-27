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
        #self.items = self.widget.view()
        #self.widget.currentIndexChanged.connect(self.callback)
        self.widget.activated.connect(self.callback)

    def set_widget_value(self):
        try:
            self.widget.setCurrentIndex(int(self.attr.value))
        except:
            pass
        return self.attr.value

    def decorate_error(self):
        #print('decorate error', self)
        self.widget.setStyleSheet('color: gray')

    def update(self, decorate_only=True) -> None:
        super().update(decorate_only)

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
            else:
                self.decorate_error()
