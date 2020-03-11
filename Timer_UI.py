# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""

import sys
import time
import logging
import os.path

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

import tango

from TangoWidgets.TangoWidget import TangoWidget
from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoComboBox import TangoComboBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.Timer_on_LED import Timer_on_LED
from TangoWidgets.TangoRadioButton import TangoRadioButton
from TangoWidgets.TangoPushButton import TangoPushButton
from TangoWidgets.RF_ready_LED import RF_ready_LED
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'Timer_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '2_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Global configuration dictionary
TIMER_PERIOD = 300  # ms
timer_state_channels = ['channel_state'+str(k) for k in range(12)]


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
        # Default main window parameters
        self.resize(QSize(480, 640))                 # size
        self.move(QPoint(50, 50))                    # position
        self.setWindowTitle(APPLICATION_NAME)        # title
        self.setWindowIcon(QtGui.QIcon('icon.png'))  # icon
        #
        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')
        #
        #all_widgets = get_widgets(self)
        restore_settings(self, file_name=CONFIG_FILE)
        # timer device
        try:
            self.timer_device = tango.DeviceProxy('binp/nbi/timing')
            TangoWidget.DEVICES['binp/nbi/timing'] = self.timer_device
        except:
            self.timer_device = None
        # read only attributes TangoWidgets list
        self.rdwdgts = (
            # timer
            TangoLabel('binp/nbi/adc0/Elapsed', self.label_3),  # elapsed
            TangoLabel('binp/nbi/timing/channel_enable0', self.label_30, prop='label'),  # ch0
            TangoLabel('binp/nbi/timing/channel_enable1', self.label_31, prop='label'),  # ch1
            TangoLabel('binp/nbi/timing/channel_enable2', self.label_34, prop='label'),  # ch2
            TangoLabel('binp/nbi/timing/channel_enable3', self.label_35, prop='label'),  # ch3
            TangoLabel('binp/nbi/timing/channel_enable4', self.label_36, prop='label'),  # ch4
            TangoLabel('binp/nbi/timing/channel_enable5', self.label_38, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable6', self.label_39, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable7', self.label_40, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable8', self.label_41, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable9', self.label_42, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable10', self.label_43, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable11', self.label_44, prop='label'),  # ch11
            # pg
            TangoLED('binp/nbi/pg_offset/output_state', self.pushButton_31),  # PG offset on
            # lauda
            TangoLED('binp/nbi/lauda/6230_7', self.pushButton_30),  # Pump On
            #TangoLED('binp/nbi/lauda/6230_0', self.pushButton_30),  # Valve
            # rf system
            RF_ready_LED('binp/nbi/timing/di60', self.pushButton_32),  # RF system ready
        )
        # read write attributes TangoWidgets list
        self.wtwdgts = (
            # timer
            TangoAbstractSpinBox('binp/nbi/timing/Period', self.spinBox),  # period
            TangoComboBox('binp/nbi/timing/Start_mode', self.comboBox),  # single/periodical
            TangoCheckBox('binp/nbi/timing/channel_enable0', self.checkBox_8),  # ch0
            TangoCheckBox('binp/nbi/timing/channel_enable1', self.checkBox_9),  # ch1
            TangoCheckBox('binp/nbi/timing/channel_enable2', self.checkBox_10),  # ch2
            TangoCheckBox('binp/nbi/timing/channel_enable3', self.checkBox_11),  # ch3
            TangoCheckBox('binp/nbi/timing/channel_enable4', self.checkBox_12),  # ch4
            TangoCheckBox('binp/nbi/timing/channel_enable5', self.checkBox_13),  # ch5
            TangoCheckBox('binp/nbi/timing/channel_enable6', self.checkBox_14),  # ch6
            TangoCheckBox('binp/nbi/timing/channel_enable7', self.checkBox_15),  # ch7
            TangoCheckBox('binp/nbi/timing/channel_enable8', self.checkBox_16),  # ch8
            TangoCheckBox('binp/nbi/timing/channel_enable9', self.checkBox_17),  # ch9
            TangoCheckBox('binp/nbi/timing/channel_enable10', self.checkBox_18),  # ch10
            TangoCheckBox('binp/nbi/timing/channel_enable11', self.checkBox_19),  # ch11
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start0', self.spinBox_10),  # ch1
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start1', self.spinBox_12),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start2', self.spinBox_14),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start3', self.spinBox_16),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start4', self.spinBox_18),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start5', self.spinBox_20),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start6', self.spinBox_22),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start7', self.spinBox_24),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start8', self.spinBox_26),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start9', self.spinBox_28),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start10', self.spinBox_30),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start11', self.spinBox_32),  # ch11
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop0', self.spinBox_11),  # ch0
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop1', self.spinBox_13),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop2', self.spinBox_15),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop3', self.spinBox_17),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop4', self.spinBox_19),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop5', self.spinBox_21),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop6', self.spinBox_23),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop7', self.spinBox_25),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop8', self.spinBox_27),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop9', self.spinBox_29),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop10', self.spinBox_31),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop11', self.spinBox_33),  # ch11
            TangoAbstractSpinBox('binp/nbi/adc0/Acq_start', self.spinBox_34),  # adc start
            TangoAbstractSpinBox('binp/nbi/adc0/Acq_stop', self.spinBox_35),   # adc stop
        )
        # timer on
        #self.timer_on_led = Timer_on_LED('binp/nbi/timing/channel_state0', self.pushButton_29),  # timer on led
        #self.rdwdgts.append(self.timer_on_led)
        # additional decorations
        self.single_periodical_callback(self.comboBox.currentIndex())
        # Connect signals with slots
        self.comboBox.currentIndexChanged.disconnect(self.comboBox.tango_widget.callback)  # single/periodical combo
        self.comboBox.currentIndexChanged.connect(self.single_periodical_callback)  # single/periodical combo
        self.pushButton.clicked.connect(self.run_button_clicked)  # run button
        self.pushButton_3.clicked.connect(self.show_more_button_clicked)
        self.pushButton_2.clicked.connect(self.execute_button_clicked)
        # Defile and start timer callback task
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)
        # start timer device
        self.timer.start(TIMER_PERIOD)
        # resize main window
        self.show_more_button_clicked()
        # populate comboBOx_2
        scripts = read_folder('scripts')
        truncated = [s.replace('.py', '') for s in scripts]
        for i in range(self.comboBox_2.count()):
            self.comboBox_2.removeItem(0)
        self.comboBox_2.insertItems(0, truncated)
        if 'SetDefault' in truncated:
            self.comboBox_2.setCurrentIndex(truncated.index('SetDefault'))
        # lock timer for exclusive use of this app
        # if self.timer_device is not None:
        #     if self.timer_device.is_locked():
        #         self.logger.warning('Timer device is already locked')
        #         self.pushButton.setEnabled(False)
        #         self.comboBox.setEnabled(False)
        #     else:
        #         if self.timer_device.lock(100000):
        #             self.logger.debug('Timer device locked successfully')
        #         else:
        #             self.logger.error('Can not lock timer device')

    def check_protection_interlock(self):
        value = ((not self.checkBox_20.isChecked()) or self.pushButton_30.isChecked()) and \
                ((not self.checkBox_21.isChecked()) or self.pushButton_31.isChecked()) and \
                ((not self.checkBox_22.isChecked()) or self.pushButton_32.isChecked())
        # if value:
        #     self.pushButton.setStyleSheet('')
        # else:
        #     self.pushButton.setStyleSheet('border: 3px solid red')
        return value

    def execute_button_clicked(self):
        try:
            file_name = os.path.join('scripts', self.comboBox_2.currentText()+'.py')
            with open(file_name, 'r') as scriptfile:
                s = scriptfile.read()
                result = exec(s)
                self.logger.debug('Script %s executed', file_name)
                self.comboBox_2.setStyleSheet('')
        except:
            self.comboBox_2.setStyleSheet('color: red')
            self.logger.warning('Error action execution')
            self.logger.debug('', exc_info=True)

    def show_more_button_clicked(self):
        if self.pushButton_3.isChecked():
            self.frame.setVisible(True)
            #self.resize(QSize(418, 751))
            self.resize(QSize(self.gridLayout_2.sizeHint().width(),
                              self.gridLayout_2.sizeHint().height()+self.gridLayout_3.sizeHint().height()))
        else:
            self.frame.setVisible(False)
            #self.resize(QSize(418, 124))
            self.resize(self.gridLayout_2.sizeHint())

    def single_periodical_callback(self, value):
        if value == 0:  # single
            # hide remained
            self.label_4.setVisible(False)
            self.label_5.setVisible(False)
            # run button
            self.pushButton.setText('Shoot')
            self.comboBox.tango_widget.callback(value)
        elif value == 1:  # periodical
            # check protection interlock
            if not self.check_protection_interlock():
                self.logger.error('Shot is rejected')
                self.comboBox.setCurrentIndex(0)
                self.comboBox.setStyleSheet('border: 3px solid red')
                return
            # show remained
            self.label_4.setVisible(True)
            self.label_5.setVisible(True)
            # run button
            self.pushButton.setText('Stop')
            self.comboBox.tango_widget.callback(value)

    def run_button_clicked(self, value):
        if self.comboBox.currentIndex() == 0:   # single
            if self.check_timer_state(self.timer_device):
                self.pulse_off()
            else:
                # check protection interlock
                if not self.check_protection_interlock():
                    self.logger.error('Shot is rejected')
                    self.pushButton.setStyleSheet('border: 3px solid red')
                    return
                self.timer_device.write_attribute('Start_single', 1)
                self.timer_device.write_attribute('Start_single', 0)
        elif self.comboBox.currentIndex() == 1:  # periodical
            if self.check_timer_state(self.timer_device):
                self.pulse_off()
            self.comboBox.setCurrentIndex(0)

    @staticmethod
    def check_timer_state(timer_device):
        if timer_device is None:
            return False
        state = False
        avs = []
        try:
            avs = timer_device.read_attributes(timer_state_channels)
        except:
            pass
        for av in avs:
            state = state or av.value
        return state

    def pulse_off(self):
        for k in range(12):
            try:
                self.timer_device.write_attribute('channel_enable' + str(k), False)
            except:
                self.logger.debug("Exception ", exc_info=True)

    def onQuit(self) :
        # Save global settings
        save_settings(self, file_name=CONFIG_FILE)
        self.timer.stop()
        
    def timer_handler(self):
        t0 = time.time()
        if len(self.rdwdgts) <= 0 and len(self.wtwdgts) <= 0:
            return
        # during pulse
        if self.check_timer_state(self.timer_device):   # pulse is on
            # pulse ON LED -> ON
            self.pushButton_29.setEnabled(True)
            self.pushButton.setStyleSheet('color: red; font: bold')
            self.pushButton.setText('Stop')
        else:   # pulse is off
            # pulse ON LED -> OFF
            self.pushButton_29.setEnabled(False)
            self.pushButton.setStyleSheet('')
            if self.comboBox.currentIndex() == 0:
                self.pushButton.setText('Shoot')
        # remained
        try:
            self.remained = self.spinBox.value() - int(self.label_3.text())
        except:
            self.remained = 0.0
        self.label_5.setText('%d s' % self.remained)
        # main loop updating widgets
        count = 0
        while time.time() - t0 < TIMER_PERIOD/2000.0:
            if self.n < len(self.rdwdgts) and self.rdwdgts[self.n].widget.isVisible():
                self.rdwdgts[self.n].update()
            if self.n < len(self.wtwdgts) and self.wtwdgts[self.n].widget.isVisible():
                self.wtwdgts[self.n].update()
            self.n += 1
            if self.n >= max(len(self.rdwdgts), len(self.wtwdgts)):
                self.n = 0
            count += 1
            if count == max(len(self.rdwdgts), len(self.wtwdgts)):
                self.elapsed = time.time() - t0
                #print(self.elapsed)
                return
            self.elapsed = time.time() - t0
            #print(self.elapsed)


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
