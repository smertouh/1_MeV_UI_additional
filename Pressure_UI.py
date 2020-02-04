# coding: utf-8
'''
Created on Jul 28, 2019

@author: sanin
'''

import sys
import json
import logging
import time
import math

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QLineEdit
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

import tango

from TangoWidgets.TangoWidget import TangoWidget
from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoComboBox import TangoComboBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.TangoRadioButton import TangoRadioButton
from TangoWidgets.TangoPushButton import TangoPushButton
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'Pressure_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global configuration dictionary
TIMER_PERIOD = 300  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialization of the superclass
        super(MainWindow, self).__init__(parent)
        # logging config
        self.logger = config_logger(level=logging.DEBUG)
        # members definition
        self.n = 0
        self.elapsed = 0.0
        # Load the UI
        uic.loadUi(UI_FILE, self)
        # main window parameters
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        self.setWindowTitle(APPLICATION_NAME)       # title
        self.setWindowIcon(QtGui.QIcon('icon_green.png')) # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=CONFIG_FILE)        # define devices in use
        # additional devices
        try:
            dn = 'ET7000_server/test/pet7_7026'
            self.pressure_tank = tango.DeviceProxy(dn)
            TangoWidget.DEVICES[dn] = self.pressure_tank
            dn = 'ET7000_server/test/pet12_7018'
            self.pressure_magnet = tango.DeviceProxy(dn)
            TangoWidget.DEVICES[dn] = self.pressure_magnet
        except:
            pass
        # define _coeff s
        try:
            self.pt = self.pressure_tank.read_attribute('ai05')
            self.pt_config = self.pressure_tank.get_attribute_config_ex('ai05')[0]
            self.pt_coeff = float(self.av_config.display_unit)
        except:
            self.pt_coeff = 1.0
        try:
            self.pm = self.pressure_magnet.read_attribute('ai09')
            self.pm_config = self.pressure_magnet.get_attribute_config_ex('ai09')[0]
            self.pm_coeff = float(self.pm_config.display_unit)
        except:
            self.pm_coeff = 1.0


        # read attributes TangoWidgets list
        self.rdwdgts = (
            # Interlock 15 kV
            TangoLED('ET7000_server/test/pet6_7060/di01', self.pushButton_71),
            # TMP Pump
            TangoLED('ET7000_server/test/pet6_7060/di00', self.pushButton_65),
            # Fore Pump
            TangoLED('ET7000_server/test/pet5_7060/di04', self.pushButton_67),
            # Fore Pump 2
            TangoLED('ET7000_server/test/pet5_7060/di05', self.pushButton_70),
            # Source Gate
            TangoLED('ET7000_server/test/pet5_7060/di03', self.pushButton_69),
            # TMP Gate
            TangoLED('ET7000_server/test/pet5_7060/di02', self.pushButton_66),
            # Fore Valve
            TangoLED('ET7000_server/test/pet5_7060/di01', self.pushButton_68),
            # Cryo 1
            TangoLED('ET7000_server/test/pet8_7060/di00', self.pushButton_60),
            # Cryo 2
            TangoLED('ET7000_server/test/pet8_7060/di01', self.pushButton_57),
            # Cryo 3
            TangoLED('ET7000_server/test/pet8_7060/di02', self.pushButton_58),
            # Cryo 4
            TangoLED('ET7000_server/test/pet8_7060/di03', self.pushButton_59),
            # U1 Front
            TangoLED('ET7000_server/test/pet6_7060/di03', self.pushButton_61),
            # U1 Current
            TangoLED('ET7000_server/test/pet6_7060/di02', self.pushButton_62),
            # U2 Front
            TangoLED('ET7000_server/test/pet6_7060/di05', self.pushButton_63),
            # U2 Current
            TangoLED('ET7000_server/test/pet6_7060/di04', self.pushButton_64),
            # T Ceramics
            TangoLabel('ET7000_server/test/pet2_7015/ai02', self.label_104),
            # T Calorimeter
            TangoLabel('ET7000_server/test/pet12_7018/ai03', self.label_106),
        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (
            # Interlock Valves Water
            TangoPushButton('ET7000_server/test/pet5_7060/do00', self.pushButton_37),
            # TMP Pump
            TangoCheckBox('ET7000_server/test/pet6_7060/do04', self.checkBox_27),
            TangoCheckBox('ET7000_server/test/pet6_7060/do05', self.checkBox_29),
            # Fore Pump
            TangoCheckBox('ET7000_server/test/pet6_7060/do02', self.checkBox_31),
            TangoCheckBox('ET7000_server/test/pet6_7060/do03', self.checkBox_32),
            # Source Gate
            TangoCheckBox('ET7000_server/test/pet5_7060/do04', self.checkBox_33),
            TangoCheckBox('ET7000_server/test/pet6_7060/do01', self.checkBox_34),
            # TMP Gate
            TangoCheckBox('ET7000_server/test/pet5_7060/do03', self.checkBox_28),
            TangoCheckBox('ET7000_server/test/pet6_7060/do00', self.checkBox_30),
            # Fore Valve
            TangoCheckBox('ET7000_server/test/pet5_7060/do02', self.checkBox_35),
            TangoCheckBox('ET7000_server/test/pet5_7060/do05', self.checkBox_36),
            # Cryo 1
            TangoCheckBox('ET7000_server/test/pet8_7060/do01', self.checkBox_23),
            # Cryo 2
            TangoCheckBox('ET7000_server/test/pet8_7060/do02', self.checkBox_24),
            # Cryo 3
            TangoCheckBox('ET7000_server/test/pet8_7060/do03', self.checkBox_25),
            # Cryo 4
            TangoCheckBox('ET7000_server/test/pet8_7060/do04', self.checkBox_26),
            # reset cryo
            TangoCheckBox('ET7000_server/test/pet8_7060/do00', self.checkBox_38),
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

    def process_additional_widgets(self):
        try:
            self.pt = self.pressure_tank.read_attribute('ai05')
            pt = math.pow(10.0, (1.667 * self.pt.value*self.pt_coeff - 11.46))
            self.label_93.setText('%8.2e' % pt)
        except:
            self.label_93.setText('********')
        try:
            self.pm = self.pressure_magnet.read_attribute('ai09')
            pm = math.pow(10.0, (1.667 * self.pm.value*self.pm_coeff - 11.46))
            self.label_88.setText('%8.2e' % pm)
        except:
            self.label_88.setText('********')

    def timer_handler(self):
        t0 = time.time()
        self.elapsed = 0.0
        self.process_additional_widgets()
        if len(self.rdwdgts) <= 0 and len(self.wtwdgts) <= 0:
            self.elapsed = time.time() - self.elapsed
            return
        # main loop
        count = 0
        while time.time() - t0 < TIMER_PERIOD/2000.0:
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
        logging.debug('Loop takes %5.0f ms %d %d'% (self.elapsed*1000.0, count, self.n))


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
