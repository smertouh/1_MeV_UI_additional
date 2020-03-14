# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.RF_ready_LED import RF_ready_LED
from TangoWidgets.RF_on_LED import RF_on_LED
from TangoWidgets.TangoPushButton import TangoPushButton
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'RF_System_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '2_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

TIMER_PERIOD = 300  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # logging config
        self.logger = config_logger(level=logging.INFO)
        # members definition
        self.n = 0
        self.elapsed = 0.0
        # Load the UI
        uic.loadUi(UI_FILE, self)
        # main window parameters
        self.resize(QSize(480, 640))                 # size
        self.move(QPoint(50, 50))                    # position
        self.setWindowTitle(APPLICATION_NAME)        # title
        self.setWindowIcon(QtGui.QIcon('icon.png'))  # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=CONFIG_FILE)

        # define devices in use
        # try:
        #     dn = 'binp/nbi/dac0'
        #     self.dac_device = tango.DeviceProxy(dn)
        #     TangoWidget.DEVICES[dn] = self.dac_device
        #     dn = 'binp/nbi/adc0'
        #     self.adc_device = tango.DeviceProxy(dn)
        #     TangoWidget.DEVICES[dn] = self.adc_device
        #     dn = 'binp/nbi/timing'
        #     self.timer_device = tango.DeviceProxy(dn)
        #     TangoWidget.DEVICES[dn] = self.timer_device
        # except:
        #     pass
        # define _coeff s
        # try:
        #     self.av = self.adc_device.read_attribute('chan16')
        #     self.av_config = self.adc_device.get_attribute_config_ex('chan16')[0]
        #     self.av_coeff = float(self.av_config.display_unit)
        # except:
        #     self.av_coeff = 1.0
        # try:
        #     self.cc = self.adc_device.read_attribute('chan22')
        #     self.cc_config = self.adc_device.get_attribute_config_ex('chan22')[0]
        #     self.cc_coeff = float(self.cc_config.display_unit)
        # except:
        #     self.cc_coeff = 1.0
        # try:
        #     self.ua = self.adc_device.read_attribute('chan1')
        #     self.ua_config = self.adc_device.get_attribute_config_ex('chan1')[0]
        #     self.ua_coeff = float(self.ua_config.display_unit)
        # except:
        #     self.ua_coeff = 1.0

        # read attributes TangoWidgets list
        self.rdwdgts = (
            # rf system
            RF_ready_LED('binp/nbi/timing/di60', self.pushButton_1),  # RF system ready
            RF_on_LED('binp/nbi/adc0/chan1', self.pushButton_2),  # RF system ready
        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (
            # rf system
            TangoAbstractSpinBox('binp/nbi/dac0/channel0', self.spinBox_1, False),
            TangoAbstractSpinBox('binp/nbi/dac0/channel1', self.spinBox_2, False),
            TangoPushButton('binp/nbi/timing/do0', self.pushButton_3, False),
            TangoPushButton('binp/nbi/timing/do1', self.pushButton_4, False),
            TangoPushButton('binp/nbi/timing/do2', self.pushButton_5, False),
        )
        # Defile and start timer callback task
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)
        # start timer
        self.timer.start(TIMER_PERIOD)

    def onQuit(self) :
        # Save global settings
        save_settings(self, file_name=CONFIG_FILE)
        self.timer.stop()
        
    def timer_handler(self):
        t0 = time.time()
        if len(self.rdwdgts) <= 0 and len(self.wtwdgts) <= 0:
            return
        self.elapsed = 0.0
        count = 0
        while time.time() - t0 < TIMER_PERIOD/1000.0:
            if self.n < len(self.rdwdgts) and self.rdwdgts[self.n].widget.isVisible():
                self.rdwdgts[self.n].update()
            if self.n < len(self.wtwdgts) and self.wtwdgts[self.n].widget.isVisible():
                self.wtwdgts[self.n].update(decorate_only=True)
            self.n += 1
            if self.n >= max(len(self.rdwdgts), len(self.wtwdgts)):
                self.n = 0
            count += 1
            if count == max(len(self.rdwdgts), len(self.wtwdgts)):
                self.elapsed = time.time() - self.elapsed
                return
            self.elapsed = time.time() - self.elapsed


if __name__ == '__main__':
    # Create the GUI application
    app = QApplication(sys.argv)
    # Instantiate the main window
    dmw = MainWindow()
    app.aboutToQuit.connect(dmw.onQuit)
    # Show it
    dmw.show()
    # Start the Qt main loop execution, exiting from this script
    # with the same return code of Qt application
    sys.exit(app.exec_())
