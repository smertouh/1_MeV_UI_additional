# coding: utf-8
"""
Created on Jan 17, 2020

@author: sanin
"""
from PyQt5.QtWidgets import QWidget
from TangoWidgets.TangoWidget import TangoWidget


class TangoWriteWidget(TangoWidget):
    def __init__(self, name, widget: QWidget, readonly=False):
        super().__init__(name, widget, readonly)

    def decorate_error(self):
        self.widget.setStyleSheet('color: gray')
        self.widget.setEnabled(False)

    def decorate_invalid(self, text: str = None):
        #self.widget.setStyleSheet('color: red; selection-color: red')
        self.widget.setStyleSheet('color: red')
        self.widget.setEnabled(True)

    def decorate_valid(self):
        self.widget.setStyleSheet('')
        self.widget.setEnabled(True)

    def update(self, decorate_only=True):
        super().update(decorate_only)

    # compare widget displayed value and read attribute value
    def compare(self):
        if self.attribute.is_readonly():
            return True
        else:
            try:
                if abs(int(self.attribute.value()) - int(self.widget.value())) > 1:
                    self.logger.debug('%s %s != %s' % (self.attribute.full_name, int(self.attribute.value()), int(self.widget.value())))
                    return False
                if abs((self.attribute.value() - self.widget.value())) > abs((1e-3 * self.widget.value())):
                    self.logger.debug('%s %s != %s' % (self.attribute.full_name, self.attribute.value(), self.widget.value()))
                    return False
                else:
                    return True
            except:
                self.logger.debug('%s Exception in compare' % self.attribute.full_name, exc_info=True)
                return False
