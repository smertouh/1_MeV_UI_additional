# coding: utf-8
"""
Created on Mar 2, 2020

@author: sanin
"""

import sys
import time

from PyQt5.QtWidgets import QWidget
import tango

from .Utils import *
from .TangoAttribute import TangoAttribute

class TangoMultiAttribute():
    def __init__(self, attributes: [str], level=logging.DEBUG, readonly=False, use_history=True):
        self.use_history = use_history
        self.connected = False
        self.readonly = readonly
        # configure logging
        self.logger = config_logger(level=level)
        self.tango_attributes = {}
        # connect attributes
        self.connect()
        self.time = 0.0

    def connect(self):
        all_connected = True
        for attr in self.attributes:
            if attr not in self.tango_attributes:
                self.tango_attributes[attr] = TangoAttribute(attr, level=self.logger.level, readonly=self.readonly)
            all_connected = all_connected or self.tango_attributes[attr].connected
        self.connected = all_connected

    def disconnect(self):
        if not self.connected:
            return
        for attr in self.attributes:
            self.tango_attributes[attr].disconnect()
        self.connected = False
        self.time = time.time()
        self.logger.debug('Attribute %s has been disconnected.', self.full_name)

    def reconnect(self):
        for attr in self.attributes:
            self.tango_attributes[attr].reconnect()

    def is_readonly(self):
        return self.config.writable == tango.AttrWriteType.READ

    def is_valid(self):
        return self.connected and self.read_result.quality == tango._tango.AttrQuality.ATTR_VALID

    def is_boolean(self):
        stat = self.config.data_format == tango.AttrDataFormat.SCALAR and \
               self.config.data_type == bool
        return stat

    def is_scalar(self):
        return self.config.data_format == tango._tango.AttrDataFormat.SCALAR

    def read(self, force=False):
        self.reconnect()
        if not self.connected:
            msg = 'Attribute %s is disconnected.' % self.full_name
            self.logger.debug(msg)
            raise ConnectionError(msg)
        try:
            if self.use_history and not force and self.device_proxy.is_attribute_polled(self.attribute_name):
                at = self.device_proxy.attribute_history(self.attribute_name, 1)[0]
                if at.time.totime() > self.read_result.totime():
                    self.read_result = at
            else:
                self.read_result = self.device_proxy.read_attribute(self.attribute_name)
        except:
            msg = 'Attribute %s read error.' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.read_result = None
            self.disconnect()
            raise
        return self.value()

    def write(self, value):
        if self.readonly:
            return
        self.reconnect()
        if not self.connected:
            msg = 'Attribute %s is disconnected.' % self.full_name
            self.logger.debug(msg)
            raise ConnectionError(msg)
        try:
            if self.is_boolean():
                wvalue = bool(value)
            else:
                wvalue = value / self.coeff
            self.device_proxy.write_attribute(self.attribute_name, wvalue)
        except:
            msg = 'Attribute %s write error.' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.read_result = None
            self.disconnect()
            raise

    def value(self):
        if self.is_boolean():
            rvalue = self.read_result.value
        else:
            rvalue = self.read_result.value * self.coeff
        return rvalue

    def text(self):
        try:
            txt = self.format % self.value()
        except:
            txt = str(self.read_result.value)
        return txt
