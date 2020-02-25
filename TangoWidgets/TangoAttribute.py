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
        self.device_name = ''
        self.attribute_name = ''
        self.device_proxy = None
        self.attr = None
        self.config = None
        self.format = None
        self.coeff = 1.0
        self.connected = False
        # configure logging
        self.logger = config_logger(level=level)
        try:
            n = name.rfind('/')
            self.device_name = name[:n]
            self.attribute_name = name[n + 1:]
            self.connect()
        except:
            self.logger.warning('Can not create attribute %s', self.full_name)
            self.logger.log(logging.DEBUG, 'Exception:', exc_info=True)
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
            self.logger.debug('Attribute %s disconnected', self.full_name)

    def connect(self):
        try:
            if self.device_name in TangoWidget.DEVICES and TangoWidget.DEVICES[self.device_name] is not None:
                self.device_proxy = TangoWidget.DEVICES[self.device_name]
            else:
                self.device_proxy = tango.DeviceProxy(self.device_name)
                TangoWidget.DEVICES[self.device_name] = self.device_proxy
            self.device_proxy.ping()
            self.attr = self.device_proxy.read_attribute(self.attribute_name)
            self.update_config()
            self.connected = True
            self.time = time.time()
            self.logger.info('Connected to Attribute %s', self.full_name)
        except:
            self.logger.warning('Can not create attribute %s', self.full_name)
            self.logger.log(logging.DEBUG, 'Exception:', exc_info=True)
            self.connected = False
            self.time = time.time()

    def update_config(self):
        self.config = self.device_proxy.get_attribute_config_ex(self.attribute_name)[0]
        self.format = self.config.format
        try:
            self.coeff = float(self.config.display_unit)
        except:
            self.coeff = 1.0

    def read(self, force=False):
        try:
            if not force and self.device_proxy.is_attribute_polled(self.attribute_name):
                attrib = self.device_proxy.attribute_history(self.attribute_name, 1)[0]
                if attrib.time.tv_sec > self.attr.time.tv_sec or \
                        (attrib.time.tv_sec == self.attr.time.tv_sec and attrib.time.tv_usec > self.attr.time.tv_usec):
                    self.attr = attrib
            else:
                self.attr = self.device_proxy.read_attribute(self.attribute_name)
        except:
            self.attr = None
            self.disconnect()
            raise
        self.ex_count = 0

    def write(self, value):
        #if self.readonly:
        #    return
        self.device_proxy.write_attribute(self.attribute_name, value / self.coeff)
