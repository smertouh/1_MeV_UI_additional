# coding: utf-8
"""
Created on Feb 4, 2020

@author: sanin
"""

import sys
import time

from PyQt5.QtWidgets import QWidget
import tango
from tango import DeviceProxy, GreenMode

from .Utils import *


class TangoAttribute:
    devices = {}
    reconnect_timeout = 5.0

    def __init__(self, name: str, level=logging.DEBUG, readonly=False, use_history=True):
        # defaults
        self.full_name = str(name)
        self.use_history = use_history
        self.device_name, self.attribute_name = split_attribute_name(self.full_name)
        self.device_proxy = None
        self.read_result = None
        self.config = None
        self.format = None
        self.coeff = 1.0
        self.connected = False
        self.readonly = readonly
        # configure logging
        self.logger = config_logger(level=level)
        # connect attribute
        self.connect()
        self.time = time.time()
        # asynch operation vars
        self.read_call_id = None
        self.write_call_id = None
        self.read_time = 0.0
        self.write_time = 0.0
        self.read_timeout = 5.0
        self.write_timeout = 5.0

    def connect(self):
        try:
            self.device_proxy = self.create_device_proxy()
            self.set_config()
            self.read_result = self.device_proxy.read_attribute(self.attribute_name)
            self.connected = True
            self.time = 0.0
            self.logger.info('Attribute %s has been connected' % self.full_name)
        except:
            self.logger.warning('Can not connect attribute %s' % self.full_name)
            self.logger.debug('Exception connecting attribute %s' % self.full_name, exc_info=True)
            self.disconnect()

    def disconnect(self):
        self.time = time.time()
        if not self.connected:
            return
        self.connected = False
        self.logger.debug('Attribute %s has been disconnected', self.full_name)

    def reconnect(self):
        if self.device_name in TangoAttribute.devices and TangoAttribute.devices[self.device_name] is not self.device_proxy:
            self.logger.debug('Device proxy changed for %s' % self.full_name)
            self.connect()
        if self.connected:
            return
        if time.time() - self.time > self.reconnect_timeout:
            self.logger.debug('Reconnection timeout exceeded for %s' % self.full_name)
            self.connect()

    def create_device_proxy(self):
        dp = None
        if self.device_name in TangoAttribute.devices and TangoAttribute.devices[self.device_name] is not None:
            try:
                pt = TangoAttribute.devices[self.device_name].ping()
                dp = TangoAttribute.devices[self.device_name]
                self.logger.debug('Device %s for %s exists, ping=%ds' % (self.device_name, self.attribute_name, pt))
            except:
                self.logger.warning('Exception %s connecting to %s' % (sys.exc_info()[0], self.device_name))
                self.logger.debug('Exception:', exc_info=True)
                dp = None
                TangoAttribute.devices[self.device_name] = dp
        if dp is None:
            dp = tango.DeviceProxy(self.device_name)
            ###dp.set_green_mode(GreenMode.Asyncio)
            self.logger.info('Device proxy for %s has been created' % self.device_name)
            TangoAttribute.devices[self.device_name] = dp
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
        if self.config is not None:
            return self.config.writable == tango.AttrWriteType.READ
        else:
            return True

    def is_valid(self):
        return self.connected and self.read_result.quality == tango._tango.AttrQuality.ATTR_VALID

    def is_boolean(self):
        if not self.connected:
            return False
        return isinstance(self.read_result.value, bool)

    def is_scalar(self):
        if not self.connected:
            return False
        return self.config.data_format == tango._tango.AttrDataFormat.SCALAR

    def read(self, force=False):
        self.reconnect()
        if not self.connected:
            msg = 'Attribute %s is disconnected.' % self.full_name
            self.logger.debug(msg)
            raise ConnectionError(msg)
        try:
            if self.read_call_id is None:
                # no read request before, so send it
                self.read_call_id = self.device_proxy.read_attribute_asynch(self.attribute_name)
                self.read_time = time.time()
            else:
                # read request has been sent before
                if force:
                    to = 0.0
                else:
                    to = 0.001
                # elf.read_result = self.device_proxy.read_attribute_reply(self.read_call_id, timeout=to)
                self.read_result = self.device_proxy.read_attribute_reply(self.read_call_id)
                # clear call id
                self.read_call_id = None
        except tango.AsynReplyNotArrived:
            msg = 'AsynReplyNotArrived for %s' % self.full_name
            self.logger.debug(msg)
            if self.read_time - time.time() > self.read_timeout:
                msg = 'Timeout reading of %s' % self.full_name
                self.logger.warning(msg)
                raise
        except:
            msg = 'Attribute %s read error' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.read_result = None
            self.disconnect()
            raise
        return self.value()

    def write(self, value, force=False):
        if self.readonly:
            return
        self.reconnect()
        if not self.connected:
            msg = 'Attribute %s is disconnected' % self.full_name
            self.logger.debug(msg)
            raise ConnectionError(msg)
        try:
            if self.is_boolean():
                wvalue = bool(value)
            else:
                wvalue = value / self.coeff
            if self.write_call_id is None:
                # no request before, so send it
                self.write_call_id = self.device_proxy.write_attribute_asynch(self.attribute_name, wvalue)
            else:
                # write request has been sent before
                if force:
                    to = 0.0
                else:
                    to = 0.001
                #self.device_proxy.write_attribute_reply(self.write_call_id, timeout=to)
                self.device_proxy.write_attribute_reply(self.write_call_id)
                # clear call id
                self.write_call_id = None
        except tango.AsynReplyNotArrived:
            msg = 'AsynReplyNotArrived for %s' % self.full_name
            self.logger.debug(msg)
            if self.write_time - time.time() > self.write_timeout:
                msg = 'Timeout writing of %s' % self.full_name
                self.logger.warning(msg)
                raise
        except:
            msg = 'Attribute %s write error' % self.full_name
            self.logger.info(msg)
            self.logger.debug('Exception:', exc_info=True)
            self.read_result = None
            self.disconnect()
            raise

    def value(self):
        if self.read_result is None:
            return None
        if self.is_boolean() or self.read_result.value is None:
            return self.read_result.value
        return self.read_result.value * self.coeff

    def text(self):
        try:
            txt = self.format % self.value()
        except:
            txt = str(self.value())
        return txt
