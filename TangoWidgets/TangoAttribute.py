# coding: utf-8
'''
Created on Feb 4, 2020

@author: sanin
'''

import sys
import time

from PyQt5.QtWidgets import QWidget
import tango

from .Utils import *
from .TangoWidget import TangoWidget

class TangoAttribute:
    def __init__(self, name: str, level=logging.DEBUG):
        # defaults
        self.full_name = str(name)
        self.device_name, self.attribute_name = split_attribute_name(self.full_name)
        self.device_proxy = None
        self.attribute = None
        self.config = None
        self.format = None
        self.coeff = 1.0
        self.connected = False
        self.readonly = False
        # configure logging
        self.logger = config_logger(level=level)
        # connect attribute
        self.connect()
        self.time = time.time()

    def connect(self):
        try:
            self.device_proxy = self.create_device_proxy()
            self.set_config()
            self.attribute = self.device_proxy.read_attribute(self.attribute_name)
            self.connected = True
            self.time = time.time()
            self.logger.info('Attribute %s has been connected' % self.full_name)
        except:
            self.logger.warning('Can not connect attribute %s' % self.full_name)
            self.logger.debug('Exception connecting attribute %s' % self.full_name, exc_info=True)
            self.connected = False
            self.time = time.time()

    def disconnect(self):
        if not self.connected:
            return
        self.ex_count += 1
        if self.ex_count > 3:
            self.connected = False
            self.ex_count = 0
            self.time = time.time()
            self.logger.debug('Attribute %s has been disconnected.', self.full_name)

    def create_device_proxy(self):
        dp = None
        if self.device_name in TangoWidget.DEVICES and TangoWidget.DEVICES[self.device_name] is not None:
            try:
                pt = TangoWidget.DEVICES[self.device_name].ping()
                dp = TangoWidget.DEVICES[self.device_name]
                self.logger.info('Device %s for %s exists, ping=%d [s].' % (dp, self.device_name, pt))
            except:
                self.logger.warning('Exception connecting to %s.' % self.device_name, exc_info=True)
                dp = None
                TangoWidget.DEVICES[self.device_name] = dp
        if dp is None:
            dp = tango.DeviceProxy(self.device_name)
            self.logger.info('Device %s for %s has been created.' % (dp, self.device_name))
            TangoWidget.DEVICES[self.device_name] = dp
        return dp

    def set_config(self):
        self.config = self.device_proxy.get_attribute_config_ex(self.attribute_name)[0]
        self.format = self.config.format
        try:
            self.coeff = float(self.config.display_unit)
        except:
            self.coeff = 1.0
        self.readonly = self.readonly or self.is_readonly()

    def is_readonly(self):
        return self.config.writable == tango.AttrWriteType.READ

    def is_boolean(self):
        stat = self.config.data_format == tango.AttrDataFormat.SCALAR and\
            self.config.data_type == bool
        return stat

    def read(self, force=False):
        if not self.connected:
            msg = 'Attribute %s is disconnected.' % self.full_name
            self.logger.debug(msg)
            raise ConnectionError(msg)
        try:
            if not force and self.device_proxy.is_attribute_polled(self.attribute_name):
                at = self.device_proxy.attribute_history(self.attribute_name, 1)[0]
                if at.time.totime() > self.attribute.totime():
                    self.attribute = at
            else:
                self.attribute = self.device_proxy.read_attribute(self.attribute_name)
        except:
            msg = 'Attribute %s read error.' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.attribute = None
            self.disconnect()
            raise
        self.ex_count = 0
        return self.attribute

    def write(self, value):
        if self.readonly:
            return
        try:
            if self.is_boolean():
                wvalue = value
            else:
                wvalue = value / self.coeff
            self.device_proxy.write_attribute(self.attribute_name, wvalue)
        except:
            msg = 'Attribute %s write error.' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.attribute = None
            self.disconnect()
            raise

