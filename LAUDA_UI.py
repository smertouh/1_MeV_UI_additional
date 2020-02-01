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

from TangoWidgets.Utils import *
from TangoWidgets.TangoWidget import TangoWidget
from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoComboBox import TangoComboBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.TangoRadioButton import TangoRadioButton
from TangoWidgets.TangoPushButton import TangoPushButton

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'LAUDA_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global configuration dictionary
CONFIG = {}
TIMER_PERIOD = 1500  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        global logger
        # Initialization of the superclass
        super(MainWindow, self).__init__(parent)
        # logging config
        self.logger = config_logger()
        # members definition
        self.n = 0
        self.elapsed = 0.0

        # Load the UI
        uic.loadUi(UI_FILE, self)

        # main window parameters
        ##self.setMinimumSize(QSize(480, 640))        # min size
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        self.setWindowTitle(APPLICATION_NAME)       # title
        self.setWindowIcon(QtGui.QIcon('icon.png')) # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        self.restore_settings()

        # read attributes TangoWidgets list
        self.rdwdgts = (
            # lauda
            TangoLED('binp/nbi/lauda/6230_7', self.pushButton_34),  # Pump On
            TangoLED('binp/nbi/lauda/6230_0', self.pushButton_31),  # Valve
            TangoLabel('binp/nbi/lauda/1012', self.label_23),       # Return
        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (
            # lauda
            TangoAbstractSpinBox('binp/nbi/lauda/6200', self.spinBox_4, False),  # SetPoint
            TangoPushButton('binp/nbi/lauda/6210_3', self.pushButton_4, False),  # Valve
            TangoPushButton('binp/nbi/lauda/6210_1', self.pushButton_3, False),  # Run
            TangoPushButton('binp/nbi/lauda/6210_0', self.pushButton_6, False),  # Enable
            TangoPushButton('binp/nbi/lauda/6210_2', self.pushButton_9, False),  # Reset
        )
        #
        TangoWidget.RECONNECT_TIMEOUT = 5.0
        # Connect signals with slots
        self.pushButton_3.clicked.connect(self.lauda_pump_on_callback)
        self.spinBox_4.valueChanged.connect(self.setpoint_valueChanged)
        # lauda device
        try:
            self.lauda = TangoWidget.DEVICES['binp/nbi/lauda']
        except:
            self.lauda = None
        # Defile and start timer callback task
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)
        # start timer
        self.timer.start(TIMER_PERIOD)

    def setpoint_valueChanged(self):
        self.lauda.write_attribute('1100', self.spinBox_4.value())

    def lauda_pump_on_callback(self, value):
        if value:
            # reset
            #self.pushButton_9.setChecked(True)
            self.pushButton_9.tango_widget.pressed()
            #self.pushButton_9.setChecked(False)
            self.pushButton_9.tango_widget.released()
            # enable
            self.pushButton_6.setChecked(True)
            self.pushButton_6.tango_widget.clicked()

    def onQuit(self) :
        # Save global settings
        self.save_settings()
        self.timer.stop()
        
    def save_settings(self, widgets=(), file_name=CONFIG_FILE) :
        global CONFIG
        try:
            # Save window size and position
            p = self.pos()
            s = self.size()
            CONFIG['main_window'] = {'size':(s.width(), s.height()), 'position':(p.x(), p.y())}
            #get_state(self.comboBox_1, 'comboBox_1')
            for w in widgets:
                #get_widget_state(w, CONFIG)
                pass
            with open(file_name, 'w') as configfile:
                configfile.write(json.dumps(CONFIG, indent=4))
            self.logger.info('Configuration saved to %s' % file_name)
            return True
        except :
            self.logger.log(logging.WARNING, 'Configuration save error to %s' % file_name)
            print_exception_info()
            return False
        
    def restore_settings(self, widgets=(), file_name=CONFIG_FILE) :
        global CONFIG
        try :
            with open(file_name, 'r') as configfile:
                s = configfile.read()
            CONFIG = json.loads(s)
            # Restore log level
            if 'log_level' in CONFIG:
                v = CONFIG['log_level']
                self.logger.setLevel(v)
                levels = [logging.NOTSET, logging.DEBUG, logging.INFO,
                          logging.WARNING, logging.ERROR, logging.CRITICAL, logging.CRITICAL+10]
                n = 1
                for m in range(len(levels)):
                    if v < levels[m]:
                        n = m
                        break
                self.comboBox_1.setCurrentIndex(n-1)
            # Restore window size and position
            if 'main_window' in CONFIG:
                self.resize(QSize(CONFIG['main_window']['size'][0], CONFIG['main_window']['size'][1]))
                self.move(QPoint(CONFIG['main_window']['position'][0], CONFIG['main_window']['position'][1]))
            #set_state(self.plainTextEdit_1, 'plainTextEdit_1')
            #set_state(self.comboBox_1, 'comboBox_1')
            for w in widgets:
                #set_widget_state(w, CONFIG)
                pass
            self.logger.log(logging.INFO, 'Configuration restored from %s' % file_name)
            return True
        except :
            self.logger.log(logging.WARNING, 'Configuration restore error from %s' % file_name)
            print_exception_info()
            return False

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


def print_exception_info(level=logging.DEBUG):
    logger.log(level, "Exception ", exc_info=True)


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
