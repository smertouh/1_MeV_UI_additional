# coding: utf-8
"""
Created on Jan 1, 2020

@author: sanin
"""

import sys
import time

from PyQt5.QtWidgets import QWidget
import tango

from .Utils import *
from .TangoAttribute import TangoAttribute, TangoAttributeConnectionFailed


class TangoWidget:
    ERROR_TEXT = '****'
    RECONNECT_TIMEOUT = 3.0    # seconds
    DEVICES = {}

    def __init__(self, name: str, widget: QWidget, readonly: bool = True,  level=logging.DEBUG):
        # configure logging
        self.logger = config_logger(level=level)
        self.name = name
        self.widget = widget
        self.widget.tango_widget = self
        self.update_dt = 0.0
        # create attribute proxy
        self.attribute = TangoAttribute(name, level=level, readonly=readonly)
        # first update with set widget value from attribute
        self.update(decorate_only=False)

    def decorate_error(self, *args, **kwargs):
        if hasattr(self.widget, 'setText'):
            self.widget.setText(TangoWidget.ERROR_TEXT)
        self.widget.setStyleSheet('color: gray')

    def decorate_invalid(self, text: str = None, *args, **kwargs):
        if hasattr(self.widget, 'setText') and text is not None:
            self.widget.setText(text)
        self.widget.setStyleSheet('color: red')

    def decorate_invalid_data_format(self, text: str = None, *args, **kwargs):
        self.decorate_invalid(text, *args, **kwargs)

    def decorate_not_equal(self, text: str = None, *args, **kwargs):
        self.decorate_invalid(text, *args, **kwargs)

    def decorate_invalid_quality(self, *args, **kwargs):
        self.decorate_invalid(*args, **kwargs)

    def decorate_valid(self, *args, **kwargs):
        # self.widget.setStyleSheet('color: black')
        self.widget.setStyleSheet('')

    def read(self, force=False):
        return self.attribute.read(force)

    def write(self, value):
        return self.attribute.write(value)

    # compare widget displayed value and read attribute value
    def compare(self):
        return True

    def set_widget_value(self):
        if not (self.attribute.is_scalar() and self.attribute.is_valid()):
            # dont set value from invalid attribute
            return
        # block update events for widget
        bs = self.widget.blockSignals(True)
        # set widget value
        if hasattr(self.widget, 'setValue'):
            self.widget.setValue(self.attribute.value())
        elif hasattr(self.widget, 'setChecked'):
            self.widget.setChecked(self.attribute.value())
        elif hasattr(self.widget, 'setText'):
            self.widget.setText(self.attribute.text())
        # restore update events for widget
        self.widget.blockSignals(bs)

    def update(self, decorate_only=False) -> None:
        t0 = time.time()
        try:
            self.read()
            if not decorate_only:
                self.set_widget_value()
            self.decorate()
        except TangoAttributeConnectionFailed:
            # self.logger.info('Exception: %s' % sys.exc_info()[1])
            self.set_attribute_value()
            self.decorate()
        except:
            self.logger.info('Exception: %s' % sys.exc_info()[1])
            self.logger.debug('Exception Info:', exc_info=True)
            self.set_attribute_value()
            self.decorate()
        self.update_dt = time.time() - t0

    def decorate(self):
        if not self.attribute.connected:
            self.logger.debug('%s is not connected' % self.name)
            self.decorate_error()
        elif not self.attribute.is_scalar():
            self.logger.debug('%s is non scalar' % self.name)
            self.decorate_invalid_data_format()
        elif not self.attribute.is_valid():
            self.logger.debug('%s is invalid' % self.name)
            self.decorate_invalid_quality()
        else:
            if not self.compare():
                self.logger.debug('%s not equal' % self.name)
                self.decorate_not_equal()
            else:
                self.decorate_valid()

    def set_attribute_value(self, value=None):
        if self.attribute.is_readonly():
            return
        if value is None:
            value = self.get_widget_value()
        if value is None:
            return
        if isinstance(value, bool) and (not self.attribute.is_boolean()):
            return
        try:
            self.write(value)
        except:
            self.logger.info('Exception: %s' % sys.exc_info()[1])
            self.logger.debug('Exception Info:', exc_info=True)

    def get_widget_value(self):
        result = None
        if hasattr(self.widget, 'value'):
            result = self.widget.value()
        elif hasattr(self.widget, 'getChecked'):
            result = self.widget.getChecked()
        elif hasattr(self.widget, 'getText'):
            result = self.widget.getText()
        return result

    def callback(self, value):
        # self.logger.debug('Callback entry')
        if self.attribute.is_readonly():
            return
        try:
            self.write(value)
            self.read(True)
            self.decorate()
        except:
            self.logger.warning('Exception in callback')
            self.logger.debug('Exception Info:', exc_info=True)
            self.decorate()
