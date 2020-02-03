# coding: utf-8
'''
Created on Jul 28, 2019

@author: sanin
'''

import sys
import json
import logging
import time

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
APPLICATION_NAME = 'Magnets_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global configuration dictionary
TIMER_PERIOD = 500  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        global logger
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
        self.setWindowIcon(QtGui.QIcon('icon.png')) # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=CONFIG_FILE)

        # read attributes TangoWidgets list
        self.rdwdgts = (
            # magnet 1
            TangoLED('binp/nbi/magnet1/output_state', self.pushButton_38),
            TangoLabel('binp/nbi/magnet1/voltage', self.label_149),
            TangoLabel('binp/nbi/magnet1/current', self.label_151),
            # magnet 2
            TangoLED('binp/nbi/magnet2/output_state', self.pushButton_41),
            TangoLabel('binp/nbi/magnet2/voltage', self.label_150),
            TangoLabel('binp/nbi/magnet2/current', self.label_152),
            # pg
            TangoLED('binp/nbi/pg_offset/output_state', self.pushButton_42),
            TangoLabel('binp/nbi/pg_offset/voltage', self.label_140),
            TangoLabel('binp/nbi/pg_offset/current', self.label_142),
            # acceleration
            TangoLabel('ET7000_server/test/pet9_7026/ai00', self.label_36),
            # extraction
            TangoLabel('ET7000_server/test/pet4_7026/ai00', self.label_34),
        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (
            # magnet 1
            TangoCheckBox('binp/nbi/magnet1/output_state', self.checkBox_54),
            TangoAbstractSpinBox('binp/nbi/magnet1/programmed_current', self.doubleSpinBox_55),
            TangoAbstractSpinBox('binp/nbi/magnet1/programmed_voltage', self.doubleSpinBox_53),
            # magnet 2
            TangoCheckBox('binp/nbi/magnet2/output_state', self.checkBox_55),
            TangoAbstractSpinBox('binp/nbi/magnet2/programmed_current', self.doubleSpinBox_56),
            TangoAbstractSpinBox('binp/nbi/magnet2/programmed_voltage', self.doubleSpinBox_54),
            # pg
            TangoCheckBox('binp/nbi/pg_offset/output_state', self.checkBox_52),
            TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_current', self.doubleSpinBox_49),
            TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_voltage', self.doubleSpinBox_50),
            # extraction
            TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao00', self.doubleSpinBox_5),
            TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao01', self.doubleSpinBox_8),
            # acceleration
            TangoAbstractSpinBox('ET7000_server/test/pet9_7026/ao00', self.doubleSpinBox_9),
            TangoAbstractSpinBox('ET7000_server/test/pet7_7026/ao00', self.doubleSpinBox_10),
        )
        # Defile and start timer callback task
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)
        # start timer
        self.timer.start(TIMER_PERIOD)
        # Connect signals with slots
        # acceleration
        self.checkBox_3.stateChanged.connect(self.cb3_callback)
        # extraction
        self.checkBox_2.stateChanged.connect(self.cb2_callback)

    def cb3_callback(self, value):
        if value:
            self.doubleSpinBox_9.setReadOnly(False)
            self.doubleSpinBox_10.setReadOnly(False)
        else:
            self.doubleSpinBox_9.setValue(0.0)
            self.doubleSpinBox_9.setReadOnly(True)
            self.doubleSpinBox_10.setValue(0.0)
            self.doubleSpinBox_10.setReadOnly(True)

    def cb2_callback(self, value):
        if value:
            self.doubleSpinBox_5.setReadOnly(False)
            self.doubleSpinBox_8.setReadOnly(False)
        else:
            self.doubleSpinBox_5.setValue(0.0)
            self.doubleSpinBox_5.setReadOnly(True)
            self.doubleSpinBox_8.setValue(0.0)
            self.doubleSpinBox_8.setReadOnly(True)

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
