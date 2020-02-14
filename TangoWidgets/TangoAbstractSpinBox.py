# coding: utf-8
'''
Created on Jan 3, 2020

@author: sanin
'''
import math

from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractSpinBox
from TangoWidgets.TangoWriteWidget import TangoWriteWidget

import tango


class TangoAbstractSpinBox(TangoWriteWidget):
    def __init__(self, name, widget: QAbstractSpinBox, readonly=False):
        super().__init__(name, widget, readonly)
        self.widget.setKeyboardTracking(False)
        if not readonly:
            self.widget.valueChanged.connect(self.callback)
            self.widget.last_keyPressEvent = self.widget.keyPressEvent
            self.widget.keyPressEvent = self.keyPressEvent

    def set_widget_value(self):
        if self.attr.quality != tango._tango.AttrQuality.ATTR_VALID:
            # dont set value from invalid attribute
            return
        bs = self.widget.blockSignals(True)
        try:
            if math.isnan(self.attr.value):
                self.widget.setValue(0.0)
            else:
                self.widget.setValue(self.attr.value * self.coeff)
        except:
            self.logger.debug('Exception in set_widget_value %s ' % self.attr.name, exc_info=True)
        self.widget.blockSignals(bs)

    def keyPressEvent(self, e):
        self.widget.last_keyPressEvent(e)
        k = e.key()
        if k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return:
            self.callback(self.widget.value())
