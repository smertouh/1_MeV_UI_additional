# coding: utf-8
'''
Created on Jan 1, 2020

@author: sanin
'''

import sys
import time

from PyQt5.QtWidgets import QWidget
import tango

from .Utils import *
from.TangoAttribute import TangoAttribute


class TangoWidget:
    ERROR_TEXT = '****'
    RECONNECT_TIMEOUT = 3.0    # seconds
    DEVICES = {}

    def __init__(self, name: str, widget: QWidget, readonly=True, level=logging.DEBUG):
        # configure logging
        self.logger = config_logger(level=level)
        self.name = name
        self.widget = widget
        self.widget.tango_widget = self
        self.readonly = readonly
        # create attribute proxy
        self.attribute = TangoAttribute(name, level=level, readonly=readonly)
        # update view
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
        self.widget.setStyleSheet('color: black')

    def read(self, force=False):
        return self.attribute.read()

    def write(self, value):
        return self.attribute.write()

    # compare widget displayed value and read attribute value
    def compare(self):
        return True

    def set_widget_value(self):
        if not self.attribute.is_valid():
            # dont set value from invalid attribute
            return
        bs = self.widget.blockSignals(True)
        if hasattr(self.attribute, 'value'):
            if hasattr(self.widget, 'setValue'):
                self.widget.setValue(self.attribute.value())
            elif hasattr(self.widget, 'setChecked'):
                self.widget.setChecked(self.attribute.value())
            elif hasattr(self.widget, 'setText'):
                self.widget.setText(self.attribute.text())
        self.widget.blockSignals(bs)

    def update(self, decorate_only=False) -> None:
        t0 = time.time()
        try:
            self.read()
            if not self.attribute.is_scalar():
                self.logger.debug('%s Non scalar attribute' % self.name)
                self.decorate_invalid_data_format()
            else:
                if not decorate_only:
                    self.set_widget_value()
                if not self.attribute.is_valid():
                    self.logger.debug('%s invalid' % self.name)
                    self.decorate_invalid_quality()
                else:
                    if not self.compare():
                        self.decorate_not_equal()
                    else:
                        self.decorate_valid()
        except:
            if self.connected:
                self.logger.debug('Exception updating widget', exc_info=True)
                self.disconnect_attribute_proxy()
            else:
                if (time.time() - self.time) > TangoWidget.RECONNECT_TIMEOUT:
                    self.connect_attribute_proxy()
                if self.connected:
                    if hasattr(self.widget, 'value'):
                        self.write(self.widget.value())
                    elif hasattr(self.widget, 'getChecked'):
                        self.write(self.widget.getChecked())
                    elif hasattr(self.widget, 'getText'):
                        self.write(self.widget.getText())
                    if self.attr.quality != tango._tango.AttrQuality.ATTR_VALID:
                        self.logger.debug('%s %s' % (self.attr.quality, self.attr.name))
                        self.decorate_invalid_quality()
                    else:
                        self.decorate_valid()
                else:
                    self.decorate_error()
        self.update_dt = time.time() - t0
        #print('update', self.attr_proxy, int(self.update_dt*1000.0), 'ms')

    def callback(self, value):
        #self.logger.debug('Callback entry')
        if self.readonly:
            return
        if self.connected:
            try:
                #self.write_read(value)
                self.write(value)
                self.read(True)
                #print('wr', self.attr.value, value)
                if self.attr.quality == tango._tango.AttrQuality.ATTR_VALID:
                    self.decorate_valid()
                else:
                    self.decorate_invalid()
            except:
                self.logger.debug('Exception %s in callback', sys.exc_info()[0])
                self.decorate_error()
        else:
            self.connect_attribute_proxy()
            self.decorate_error()
