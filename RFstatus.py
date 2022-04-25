# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

from TangoWidgets.TangoWidget import TangoWidget
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.TangoPushButton import TangoPushButton
from TangoWidgets.TangoAttribute import TangoAttribute
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'RFstatus'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global parameters
TIMER_PERIOD = 1500  # ms


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
        self.resize(QSize(480, 640))                 # size
        self.move(QPoint(50, 50))                    # position
        self.setWindowTitle(APPLICATION_NAME)        # title
        self.setWindowIcon(QtGui.QIcon('icon.png'))  # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=CONFIG_FILE)

        # read attributes TangoWidgets list
        self.rdwdgts = (
            # APS_ILC
            TangoLED('binp/nbi/timing/di16', self.pushButton_32),
            # BC_HVC
            TangoLED('binp/nbi/timing/di17', self.pushButton_31),
            # AnV_ON
            TangoLED('binp/nbi/timing/di18', self.pushButton_33),
            # S_C_Prot
            TangoLED('binp/nbi/timing/di19', self.pushButton_34),
            # RF_FP_A1
            TangoLED('binp/nbi/timing/di20', self.pushButton_35),
            # RPL_PRT
            TangoLED('binp/nbi/timing/di24', self.pushButton_38),
            # RFG_R/L
            TangoLED('binp/nbi/timing/di25', self.pushButton_39),
            # RF_Status
            TangoLED('binp/nbi/timing/di26', self.pushButton_37),
            # HV_ILC
            TangoLED('binp/nbi/timing/di27', self.pushButton_36),
            # RF_Ready
            TangoLED('binp/nbi/timing/di28', self.pushButton_40),
            # door g1
            TangoLED('binp/nbi/timing/di32', self.pushButton_43),
            # PrA1_ready
            TangoLED('binp/nbi/timing/di33', self.pushButton_44),
            # S_C1_PRT
            TangoLED('binp/nbi/timing/di34', self.pushButton_42),
            # Bs_C1_PRT
            TangoLED('binp/nbi/timing/di35', self.pushButton_41),
            # Fil1_ILC
            TangoLED('binp/nbi/timing/di48', self.pushButton_45),
            # C_C_Prot_a1
            TangoLED('binp/nbi/timing/di49', self.pushButton_48),

        )
        # writable attributes TangoWidgets list
        self.wtwdgts = (

        )
        #
        TangoWidget.RECONNECT_TIMEOUT = 5.0
        # lauda device
        try:
            self.lauda = TangoAttribute.devices['binp/nbi/lauda']
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
            self.pushButton_9.tango_widget.pressed()
            self.pushButton_9.tango_widget.released()
            # enable
            self.pushButton_6.setChecked(True)
            self.pushButton_6.tango_widget.clicked()

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
