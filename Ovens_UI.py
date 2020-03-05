# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""

import sys
import json
import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

import tango

from TangoWidgets.Utils import *
from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoComboBox import TangoComboBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.TangoRadioButton import TangoRadioButton
from TangoWidgets.TangoPushButton import TangoPushButton
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'Ovens_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global configuration dictionary
TIMER_PERIOD = 1000  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # Initialization of the superclass
        super(MainWindow, self).__init__(parent)
        # logging config
        self.logger = config_logger(level=logging.INFO)
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
            # top oven
            TangoLED('binp/nbi/adam5/do01', self.pushButton_49),  # oven
            TangoLED('binp/nbi/adam5/do02', self.pushButton_53),  # tube
            TangoLED('binp/nbi/adam5/do00', self.pushButton_54),  # fan
            TangoLabel('binp/nbi/adam6/ai06', self.label_68),  # oven U
            TangoLabel('binp/nbi/adam6/ai05', self.label_69),  # oven I
            TangoLabel('binp/nbi/adam6/ai04', self.label_73),  # tube U
            TangoLabel('binp/nbi/adam6/ai03', self.label_75),  # tube I
            TangoLabel('binp/nbi/adam6/ai02', self.label_78),  # fan U
            TangoLabel('binp/nbi/adam6/ai01', self.label_80),  # fan I
            TangoLabel('ET7000_server/test/pet2_7015/ai05', self.label_107),  # tube T
            TangoLabel('ET7000_server/test/pet2_7015/ai06', self.label_110),  # Cs T
            # bottom oven
            TangoLED('binp/nbi/adam10/do01', self.pushButton_55),  # oven
            TangoLED('binp/nbi/adam10/do02', self.pushButton_56),  # tube
            TangoLED('binp/nbi/adam10/do00', self.pushButton_57),  # fan
            TangoLabel('binp/nbi/adam11/ai06', self.label_93),  # oven U
            TangoLabel('binp/nbi/adam11/ai05', self.label_88),  # oven I
            TangoLabel('binp/nbi/adam11/ai04', self.label_92),  # tube U
            TangoLabel('binp/nbi/adam11/ai03', self.label_96),  # tube I
            TangoLabel('binp/nbi/adam11/ai02', self.label_86),  # fan U
            TangoLabel('binp/nbi/adam11/ai01', self.label_97),  # fan I
            TangoLabel('ET7000_server/test/pet2_7015/ai01', self.label_100),  # tube T
            TangoLabel('ET7000_server/test/pet2_7015/ai00', self.label_101),  # Cs T
        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (
            # top oven
            TangoCheckBox('binp/nbi/adam5/do01', self.checkBox_20),  # oven
            TangoCheckBox('binp/nbi/adam5/do02', self.checkBox_21),  # tube
            TangoCheckBox('binp/nbi/adam5/do00', self.checkBox_22),  # fan
            TangoAbstractSpinBox('binp/nbi/adam7/ao01', self.doubleSpinBox),  # oven
            TangoAbstractSpinBox('binp/nbi/adam7/ao02', self.doubleSpinBox_3),  # tube
            TangoAbstractSpinBox('binp/nbi/adam7/ao00', self.doubleSpinBox_9),  # fan
            # bottom oven
            TangoCheckBox('binp/nbi/adam10/do01', self.checkBox_23),  # oven
            TangoCheckBox('binp/nbi/adam10/do02', self.checkBox_24),  # tube
            TangoCheckBox('binp/nbi/adam10/do00', self.checkBox_25),  # fan
            TangoAbstractSpinBox('binp/nbi/adam12/ao01', self.doubleSpinBox_11),  # oven
            TangoAbstractSpinBox('binp/nbi/adam12/ao02', self.doubleSpinBox_13),  # tube
            TangoAbstractSpinBox('binp/nbi/adam12/ao00', self.doubleSpinBox_14),  # fan
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
