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

class TangoAttribute:
    def __init__(self, name: str, level=logging.DEBUG):
        # defaults
        self.name = str(name)
        self.dn = ''
        self.an = ''
        self.dp = None
        self.attr = None
        self.config = None
        self.format = None
        self.coeff = 1.0
        self.connected = False
        # configure logging
        self.logger = config_logger(level=level)
        try:
            n = name.rfind('/')
            self.dn = name[:n]
            self.an = name[n+1:]
            self.connect()
        except:
            self.logger.warning('Can not create attribute %s', self.name)
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
            self.logger.debug('Attribute %s disconnected', self.name)

    def connect(self):
        try:
            if self.dn in TangoWidget.DEVICES and TangoWidget.DEVICES[self.dn] is not None:
                self.dp = TangoWidget.DEVICES[self.dn]
            else:
                self.dp = tango.DeviceProxy(self.dn)
                TangoWidget.DEVICES[self.dn] = self.dp
            if not self.dp.is_attribute_polled(self.an):
                self.logger.info('Recommended to switch polling on for %s', self.name)
            self.dp.ping()
            self.attr = self.dp.read_attribute(self.an)
            self.update_config()
            self.connected = True
            self.time = time.time()
            self.logger.info('Connected to Attribute %s', self.name)
        except:
            self.logger.warning('Can not create attribute %s', self.name)
            self.logger.log(logging.DEBUG, 'Exception:', exc_info=True)
            self.connected = False
            self.time = time.time()

    def update_config(self):
        self.config = self.dp.get_attribute_config_ex(self.an)[0]
        self.format = self.config.format
        try:
            self.coeff = float(self.config.display_unit)
        except:
            self.coeff = 1.0

    def read(self, force=False):
        try:
            if not force and self.dp.is_attribute_polled(self.an):
                attrib = self.dp.attribute_history(self.an, 1)[0]
                if attrib.time.tv_sec > self.attr.time.tv_sec or \
                        (attrib.time.tv_sec == self.attr.time.tv_sec and attrib.time.tv_usec > self.attr.time.tv_usec):
                    self.attr = attrib
            else:
                self.attr = self.dp.read_attribute(self.an)
        except Exception as ex:
            self.attr = None
            self.disconnect()
            raise ex
        self.ex_count = 0
        return self.attr

    def write(self, value):
        #if self.readonly:
        #    return
        self.dp.write_attribute(self.an, value/self.coeff)
