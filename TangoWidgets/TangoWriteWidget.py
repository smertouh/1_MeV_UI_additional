# coding: utf-8
'''
Created on Jan 17, 2020

@author: sanin
'''
from PyQt5.QtWidgets import QWidget
from TangoWidgets.TangoWidget import TangoWidget


class TangoWriteWidget(TangoWidget):
    def __init__(self, name, widget: QWidget, readonly=False):
        super().__init__(name, widget, readonly)

    def decorate_error(self):
        #self.widget.setStyleSheet('color: gray')
        self.widget.setEnabled(False)

    def decorate_invalid(self, text: str = None):
        self.widget.setStyleSheet('color: red')
        #self.widget.setEnabled(True)

    def decorate_valid(self):
        self.widget.setStyleSheet('color: black')
        #self.widget.setEnabled(True)

    def update(self, decorate_only=True):
        super().update(decorate_only)

    # compare widget displayed value and read attribute value
    def compare(self):
        if self.readonly:
            return True
        else:
            try:
                if int(self.attr.value * self.coeff) != int(self.widget.value()):
                    self.logger.debug('%s %s != %s' % (self.attr.name, int(self.attr.value * self.coeff), int(self.widget.value())))
                    return False
                if abs(((self.attr.value * self.coeff) - self.widget.value())) > abs((1e-3 * self.widget.value())):
                    self.logger.debug('%s %s != %s' % (self.attr.name, self.attr.value * self.coeff, self.widget.value()))
                    return False
                else:
                    return True
            except:
                self.logger.debug('Exception in compare %s ' % self.attr.name, exc_info=True)
                return False
