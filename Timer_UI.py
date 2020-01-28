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

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'Timer_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '0_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'
UI_FILE = APPLICATION_NAME_SHORT + '.ui'

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
f_str = '%(asctime)s,%(msecs)d %(funcName)s(%(lineno)s) ' + \
        '%(levelname)-7s %(message)s'
log_formatter = logging.Formatter(f_str, datefmt='%H:%M:%S')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# Global configuration dictionary
CONFIG = {}
TIMER_PERIOD = 300  # ms


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        global logger
        # Initialization of the superclass
        super(MainWindow, self).__init__(parent)
        # logging config
        self.logger = logger
        # members definition
        self.n = 0
        self.elapsed = 0.0
        self.elapsed_time = 0.0
        self.pulse_duration = 0.0
        self.pulse_start = time.time()
        # Load the UI
        uic.loadUi(UI_FILE, self)
        # Default main window parameters
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        self.setWindowTitle(APPLICATION_NAME)       # title
        self.setWindowIcon(QtGui.QIcon('icon.png')) # icon
        # Connect menu actions
        self.actionQuit.triggered.connect(qApp.quit)
        self.actionAbout.triggered.connect(self.show_about)
        # Clock at status bar
        self.clock = QLabel(" ")
        self.statusBar().addPermanentWidget(self.clock)

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        # find all controls in config tab
        self.config_widgets = []
        self.config_widgets = get_widgets(self.stackedWidgetPage2)

        self.restore_settings(self.config_widgets)

        # read only attributes TangoWidgets list
        self.rdwdgts = (
            # timer
            TangoLabel('binp/nbi/adc0/Elapsed', self.label_3),  # elapsed
            #TangoLabel('binp/nbi/adc0/Elapsed', self.label_6),  # pulse duration
            TangoLabel('binp/nbi/timing/channel_enable0', self.label_30, prop='label'),  # ch0
            TangoLabel('binp/nbi/timing/channel_enable1', self.label_31, prop='label'),  # ch1
            TangoLabel('binp/nbi/timing/channel_enable2', self.label_34, prop='label'),  # ch2
            TangoLabel('binp/nbi/timing/channel_enable3', self.label_35, prop='label'),  # ch3
            TangoLabel('binp/nbi/timing/channel_enable4', self.label_36, prop='label'),  # ch3
            TangoLabel('binp/nbi/timing/channel_enable5', self.label_38, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable6', self.label_39, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable7', self.label_40, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable8', self.label_41, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable9', self.label_42, prop='label'),  # ch
            TangoLabel('binp/nbi/timing/channel_enable10', self.label_43, prop='label'),  # ch10
            TangoLabel('binp/nbi/timing/channel_enable11', self.label_44, prop='label'),  # ch11
        )
        # read write attributes TangoWidgets list
        self.wtwdgts = (
            # timer
            TangoAbstractSpinBox('binp/nbi/timing/Period', self.spinBox, False),  # period
            TangoPushButton('binp/nbi/timing/Start_single', self.pushButton, False),  # run
            TangoComboBox('binp/nbi/timing/Start_mode', self.comboBox, False),  # single/periodical
            TangoCheckBox('binp/nbi/timing/channel_enable0', self.checkBox_8),  # ch0
            TangoCheckBox('binp/nbi/timing/channel_enable1', self.checkBox_9),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable2', self.checkBox_10),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable3', self.checkBox_11),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable4', self.checkBox_12),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable5', self.checkBox_13),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable6', self.checkBox_14),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable7', self.checkBox_15),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable8', self.checkBox_16),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable9', self.checkBox_17),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable10', self.checkBox_18),  # ch
            TangoCheckBox('binp/nbi/timing/channel_enable11', self.checkBox_19),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start0', self.spinBox_10),  # ch
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
            TangoAbstractSpinBox('binp/nbi/timing/pulse_start11', self.spinBox_32),  # ch
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop0', self.spinBox_11),  # ch
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
            TangoAbstractSpinBox('binp/nbi/timing/pulse_stop11', self.spinBox_33),  # ch
        )
        # additional decorations
        self.single_periodical_callback(self.comboBox.currentIndex())
        # Connect signals with slots
        self.comboBox.currentIndexChanged.connect(self.single_periodical_callback)  # single/periodical combo
        self.pushButton.clicked.disconnect(self.pushButton.tango_widget.clicked)  # run button
        self.pushButton.clicked.connect(self.run_button_clicked)  # run button
        self.pushButton_3.clicked.connect(self.show_more_button_clicked)
        # find timer device
        self.timer_device = None
        for d in TangoWidget.DEVICES:
            if d[0] == 'binp/nbi/timing':
                self.timer_device = d[1]
                break
        # Defile and start timer callback task
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_handler)
        self.timer.start(TIMER_PERIOD)

    def show_more_button_clicked(self):
        if self.pushButton_3.isChecked():
            self.frame.setVisible(True)
            self.resize(QSize(self.stackedWidget.sizeHint().width(), self.stackedWidget.sizeHint().height()+54))
        else:
            self.frame.setVisible(False)
            #self.resize(QSize(280, 240))
            self.resize(QSize(self.stackedWidget.sizeHint().width(), self.stackedWidget.sizeHint().height()))

    def single_periodical_callback(self, value):
        if value == 0:  # single
            # hide remained
            self.label_4.setVisible(False)
            self.label_5.setVisible(False)
            # run button
            self.pushButton.setText('Run')
            #self.pushButton.setVisible(True)
            #self.pushButton.setCheckable(False)
        elif value == 1:  # periodical
            # show remained
            self.label_4.setVisible(True)
            self.label_5.setVisible(True)
            # run button
            #self.pushButton.setVisible(False)
            self.pushButton.setText('Stop')
            #self.pushButton.setCheckable(True)
            #self.pushButton.setChecked(True)

    def run_button_clicked(self, value):
        if self.comboBox.currentIndex() == 0:
            if self.check_timer_state():
                for k in range(12):
                    self.timer_device.write_attribute('channel_enable'+str(k), False)
                return
            # single
            self.pushButton.tango_widget.pressed()
            self.pushButton.tango_widget.released()
        elif self.comboBox.currentIndex() == 1:
            # periodical
            self.comboBox.setCurrentIndex(0)
            if self.timer_device is None:
                return
            if self.check_timer_state():
                for k in range(12):
                    self.timer_device.write_attribute('channel_enable'+str(k), False)

    def check_timer_state(self):
        if self.timer_device is None:
            return
        state = False
        for k in range(12):
            try:
                av = self.timer_device.read_attribute('channel_state'+str(k))
                state = state or av.value
            except:
                self.logger.debug("Exception ", exc_info=True)
        return state

    def show_about(self):
        QMessageBox.information(self, 'About', APPLICATION_NAME + ' Version ' + APPLICATION_VERSION +
            '\nUser interface program to control 1 MeV stand', QMessageBox.Ok)

    def log_level_changed(self, m):
        levels = [logging.NOTSET, logging.DEBUG, logging.INFO,
                  logging.WARNING, logging.ERROR, logging.CRITICAL]
        if m >= 0:
            self.logger.setLevel(levels[m])

    def onQuit(self) :
        # Save global settings
        self.save_settings(self.config_widgets)
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
                get_widget_state(w, CONFIG)
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
                set_widget_state(w, CONFIG)
            self.logger.log(logging.INFO, 'Configuration restored from %s' % file_name)
            return True
        except :
            self.logger.log(logging.WARNING, 'Configuration restore error from %s' % file_name)
            self.logger.log(logging.DEBUG, '', exc_info=True)
            print_exception_info()
            return False

    def timer_handler(self):
        t0 = time.time()
        t = time.strftime('%H:%M:%S')
        self.clock.setText('%s' % t)
        if len(self.rdwdgts) <= 0 and len(self.wtwdgts) <= 0:
            return
        # pulse duration update
        if self.check_timer_state():
            self.pushButton_29.setEnabled(True)
            #self.label_6.setVisible(True)
        else:
            self.pushButton_29.setEnabled(False)
            #self.label_6.setVisible(False)
        # remained
        try:
            self.remained = self.spinBox.value() - int(self.label_3.text())
        except:
            self.remained = 0.0
        self.label_5.setText('%d s' % self.remained)
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
                self.elapsed = time.time() - t0
                return


def get_widgets(obj: QtWidgets.QWidget):
    wgts = []
    lout = obj.layout()
    for k in range(lout.count()):
        wgt = lout.itemAt(k).widget()
        if wgt is not None and isinstance(wgt, QtWidgets.QWidget) and wgt not in wgts:
            wgts.append(wgt)
        if isinstance(wgt, QtWidgets.QFrame):
            wgts1 = get_widgets(wgt)
            for wgt1 in wgts1:
                if wgt1 not in wgts:
                    wgts.append(wgt1)
    return wgts

def get_widget_state(obj, config, name=None):
    try:
        if name is None:
            name = obj.objectName()
        if isinstance(obj, QLineEdit):
            config[name] = str(obj.text())
        elif isinstance(obj, QComboBox):
            config[name] = {'items': [str(obj.itemText(k)) for k in range(obj.count())],
                            'index': obj.currentIndex()}
        elif isinstance(obj, QtWidgets.QAbstractButton):
            config[name] = obj.isChecked()
        elif isinstance(obj, QPlainTextEdit) or isinstance(obj, QtWidgets.QTextEdit):
            config[name] = str(obj.toPlainText())
        elif isinstance(obj, QtWidgets.QSpinBox) or isinstance(obj, QtWidgets.QDoubleSpinBox):
            config[name] = obj.value()
    except:
        return

def set_widget_state(obj, config, name=None):
    try:
        if name is None:
            name = obj.objectName()
        if name not in config:
            return
        if isinstance(obj, QLineEdit):
            obj.setText(config[name])
        elif isinstance(obj, QComboBox):
            obj.setUpdatesEnabled(False)
            bs = obj.blockSignals(True)
            obj.clear()
            obj.addItems(config[name]['items'])
            obj.blockSignals(bs)
            obj.setUpdatesEnabled(True)
            obj.setCurrentIndex(config[name]['index'])
            # Force index change event in the case of index=0
            if config[name]['index'] == 0:
                obj.currentIndexChanged.emit(0)
        elif isinstance(obj, QtWidgets.QAbstractButton):
            obj.setChecked(config[name])
        elif isinstance(obj, QPlainTextEdit) or isinstance(obj, QtWidgets.QTextEdit):
            obj.setPlainText(config[name])
        elif isinstance(obj, QtWidgets.QSpinBox) or isinstance(obj, QtWidgets.QDoubleSpinBox):
            obj.setValue(config[name])
    except:
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
