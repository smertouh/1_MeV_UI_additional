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

from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.TangoRadioButton import TangoRadioButton
from TangoWidgets.TangoPushButton import TangoPushButton

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = '1_MeV_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '2_0'
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
        self.refresh_flag = False
        self.last_selection = -1
        self.elapsed = 0.0
        self.elapsed_time = 0.0
        self.pulse_duration = 0.0
        self.pulse_start = time.time()

        # Load the UI
        uic.loadUi(UI_FILE, self)
        # Default main window parameters
        ##self.setMinimumSize(QSize(480, 640))        # min size
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        ##self.setWindowTitle(APPLICATION_NAME)       # title
        ##self.setWindowIcon(QtGui.QIcon('icon.png')) # icon
        # Connect signals with slots
        ##self.plainTextEdit_1.textChanged.connect(self.refresh_on)
        ##self.checkBox_25.clicked.connect(self.phandler)
        # Connect menu actions
        self.actionQuit.triggered.connect(qApp.quit)
        self.actionAbout.triggered.connect(self.show_about)
        # Additional decorations
        ##self.radioButton.setStyleSheet('QRadioButton {background-color: red}')
        ##self.doubleSpinBox_4.setSingleStep(0.1)
        ##self.doubleSpinBox_21.setKeyboardTracking(False)
        # Clock at status bar
        self.clock = QLabel(" ")
        self.statusBar().addPermanentWidget(self.clock)

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        # find all controls in config tab
        self.config_widgets = []
        self.config_widgets = get_widgets(self.tabWidgetPage3)

        self.restore_settings(self.config_widgets)

        test = False
        # read attributes TangoWidgets list
        if not test:
            self.rdwdgts = (
                # magnet 1
                TangoLED('binp/nbi/magnet1/output_state', self.pushButton_37),
                TangoLabel('binp/nbi/magnet1/voltage', self.label_140),
                TangoLabel('binp/nbi/magnet1/current', self.label_142),
                # magnet 2
                TangoLED('binp/nbi/magnet2/output_state', self.pushButton_33),
                TangoLabel('binp/nbi/magnet2/voltage', self.label_125),
                TangoLabel('binp/nbi/magnet2/current', self.label_127),
                # pg
                TangoLED('binp/nbi/pg_offset/output_state', self.pushButton_30),
                TangoLabel('binp/nbi/pg_offset/voltage', self.label_121),
                TangoLabel('binp/nbi/pg_offset/current', self.label_122),
                # rf system
                TangoLED('binp/nbi/timing/di63', self.pushButton_32),
                # lauda
                TangoLED('binp/nbi/lauda/6230_0', self.pushButton_34),  # Pump On
                TangoLED('binp/nbi/lauda/6230_7', self.pushButton_31),  # Valve
                TangoLabel('binp/nbi/lauda/1012', self.label_23),       # Return
                # acceleration
                TangoLabel('ET7000_server/test/pet9_7026/ai00', self.label_34),
                # extraction
                TangoLabel('ET7000_server/test/pet4_7026/ai00', self.label_25),
                TangoLabel('ET7000_server/test/pet4_7026/ai00', self.label_25),
                # timer
                #TangoLED('binp/nbi/timing/', self.pushButton_6),  # shot is running
                #TangoLabel('binp/nbi/timing/', self.label_3),  # elapsed
                #TangoLabel('binp/nbi/timing/', self.label_5),  # remained
            )
            # write attributes TangoWidgets list
            self.wtwdgts = (
                # magnet 1
                TangoAbstractSpinBox('binp/nbi/magnet1/programmed_current', self.doubleSpinBox_49, False),
                TangoRadioButton('binp/nbi/magnet1/output_state', self.radioButton_52, False),
                TangoAbstractSpinBox('binp/nbi/magnet1/programmed_voltage', self.doubleSpinBox_50, False),
                # magnet 2
                TangoRadioButton('binp/nbi/magnet2/output_state', self.radioButton_49, False),
                TangoAbstractSpinBox('binp/nbi/magnet2/programmed_current', self.doubleSpinBox_43, False),
                TangoAbstractSpinBox('binp/nbi/magnet2/programmed_voltage', self.doubleSpinBox_44, False),
                # pg
                TangoRadioButton('binp/nbi/pg_offset/output_state', self.radioButton_48, False),
                TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_current', self.doubleSpinBox_41, False),
                TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_voltage', self.doubleSpinBox_42, False),
                # rf system
                TangoAbstractSpinBox('binp/nbi/dac0/channel0', self.spinBox_3, False),
                TangoAbstractSpinBox('binp/nbi/dac0/channel1', self.spinBox_2, False),
                TangoPushButton('binp/nbi/timing/do0', self.pushButton_7, False),
                TangoPushButton('binp/nbi/timing/do1', self.pushButton_8, False),
                TangoPushButton('binp/nbi/timing/do2', self.pushButton_5, False),
                # lauda
                TangoAbstractSpinBox('binp/nbi/lauda/1100', self.spinBox_4, False),  # SetPoint
                TangoPushButton('binp/nbi/lauda/6210_3', self.pushButton_4, False),  # Valve
                TangoPushButton('binp/nbi/lauda/6210_1', self.pushButton_3, False),  # Run
                TangoPushButton('binp/nbi/lauda/6210_0', self.pushButton_6, False),  # Enable
                TangoPushButton('binp/nbi/lauda/6210_2', self.pushButton_9, False),  # Reset
                # extraction
                TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao00', self.doubleSpinBox_5, False),
                TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao01', self.doubleSpinBox_6, False),
                # acceleration
                TangoAbstractSpinBox('ET7000_server/test/pet9_7026/ao00', self.doubleSpinBox_7, False),
                TangoAbstractSpinBox('ET7000_server/test/pet7_7026/ao00', self.doubleSpinBox_8, False),
                # timer
                #TangoAbstractSpinBox('binp/nbi/timing/', self.spinBox, False),  # period
                #TangoPushButton('binp/nbi/timing/', self.pushButton, False),  # run
                #TangoComboBox('binp/nbi/timing/', self.comboBox, False),  # single/periodical
            )
        else:
            self.rdwdgts = (TangoLED('binp/test/test1/output_state', self.pushButton_37),
                            TangoLabel('binp/test/test1/voltage', self.label_140),
                            TangoLabel('binp/test/test1/current', self.label_142),
                            TangoLED('binp/test/test2/output_state', self.pushButton_33),
                            TangoLabel('binp/test/test2/voltage', self.label_125),
                            TangoLabel('binp/test/test2/current', self.label_127),
                            )
            # write attributes TangoWidgets list
            self.wtwdgts = (TangoAbstractSpinBox('binp/test/test1/programmed_current', self.doubleSpinBox_49, False),
                            TangoRadioButton('binp/test/test1/output_state', self.radioButton_52),
                            TangoAbstractSpinBox('binp/test/test1/programmed_voltage', self.doubleSpinBox_50, False),
                            TangoRadioButton('binp/test/test2/output_state', self.radioButton_49),
                            TangoAbstractSpinBox('binp/test/test2/programmed_current', self.doubleSpinBox_43, False),
                            TangoAbstractSpinBox('binp/test/test2/programmed_voltage', self.doubleSpinBox_44, False),
                            )
        # Connect signals with slots
        # acceleration
        self.checkBox_6.stateChanged.connect(self.cb6_callback)
        # extraction
        self.checkBox_2.stateChanged.connect(self.cb2_callback)
        # lauda
        self.pushButton_3.clicked.connect(self.lauda_pump_on_callback)
        # timer
        self.comboBox.currentIndexChanged.connect(self.single_periodical_callback)  # single/periodical combo
        self.pushButton.clicked.connect(self.timer_run_callback)  # run button

    def cb6_callback(self, value):
        if value:
            self.doubleSpinBox_8.setReadOnly(False)
            self.doubleSpinBox_7.setReadOnly(False)
        else:
            self.doubleSpinBox_8.setValue(0.0)
            self.doubleSpinBox_8.setReadOnly(True)
            self.doubleSpinBox_7.setValue(0.0)
            self.doubleSpinBox_7.setReadOnly(True)

    def cb2_callback(self, value):
        if value:
            self.doubleSpinBox_5.setReadOnly(False)
            self.doubleSpinBox_6.setReadOnly(False)
        else:
            self.doubleSpinBox_5.setValue(0.0)
            self.doubleSpinBox_5.setReadOnly(True)
            self.doubleSpinBox_6.setValue(0.0)
            self.doubleSpinBox_6.setReadOnly(True)

    def lauda_pump_on_callback(self, value):
        if value:
            # enable
            self.pushButton_6.setChecked(True)
            # reset
            self.pushButton_9.setChecked(True)
            self.pushButton_9.setChecked(False)

    def single_periodical_callback(self, value):
        if value == 0:
            # hide remained
            self.label_4.setVisible(False)
            self.label_5.setVisible(False)
            self.pushButton.setCheckable(False)
        elif value == 1:
            # show remained
            self.label_4.setVisible(True)
            self.label_5.setVisible(True)
            self.pushButton.setCheckable(True)

    def timer_run_callback(self, value):
        # elapsed to 0.0
        self.label_5.setText('0.0 s')
        self.elapsed_time = 0.0
        self.pulse_duration = 0.0
        self.pulse_start = time.time()
        if value:
            self.pushButton.setText('Stop')
        else:
            self.pushButton.setText('Run')

    def get_widgets(self, obj, s=''):
        lout = obj.layout()
        for k in range(lout.count()):
            wgt = lout.itemAt(k).widget()
            #print(s, wgt)
            if wgt is not None and wgt not in self.config_widgets:
                self.config_widgets.append(wgt)
            if isinstance(wgt, QtWidgets.QFrame):
                self.get_widgets(wgt, s=s + '   ')

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
        timer.stop()
        
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
            print_exception_info()
            return False

    def timer_handler(self):
        t0 = time.time()
        #self.elapsed += 1
        t = time.strftime('%H:%M:%S')
        self.clock.setText('%s' % t)
        #self.clock.setText('Elapsed: %ds    %s' % (self.elapsed, t))
        if len(self.rdwdgts) <= 0:
            return
        # pulse duration update
        self.pulse_duration = time.time() - self.pulse_start
        self.label_6.setText('%d s' % int(self.pulse_duration))
        self.elapsed = time.time()
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
                #print('total loop', int((time.time()-t0)*1000.0), 'ms')
                #print('total loop', '%5.3f s'%self.elapsed)
                return
        #print(int((time.time()-t0)*1000.0), 'ms')
        #time.sleep(1.0)


def get_widgets(obj: QtWidgets.QWidget):
    wgts = []
    lout = obj.layout()
    for k in range(lout.count()):
        wgt = lout.itemAt(k).widget()
        #if wgt is not None and not isinstance(wgt, QtWidgets.QFrame) and wgt not in wgts:
        #if wgt is not None and wgt not in wgts:
        if wgt is not None and isinstance(wgt, QtWidgets.QWidget) and wgt not in wgts:
            wgts.append(wgt)
        if isinstance(wgt, QtWidgets.QFrame):
            wgts1 = get_widgets(wgt)
            for wgt1 in wgts1:
                if wgt1 not in wgts:
                    wgts.append(wgt1)
    return wgts

def cb_set_color(cb: QCheckBox, m, colors=('green', 'red')):
    if isinstance(m, bool):
        if m:
            cb.setStyleSheet('QCheckBox::indicator { background: ' + colors[0] + ';}')
        else:
            cb.setStyleSheet('QCheckBox::indicator { background: ' + colors[1] + ';}')
            # cb.setStyleSheet('QCheckBox::indicator { background: red;}')
    if isinstance(m, str):
        cb.setStyleSheet('QCheckBox::indicator { background: ' + m + ';}')

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
    # Defile and start timer task
    timer = QTimer()
    timer.timeout.connect(dmw.timer_handler)
    timer.start(TIMER_PERIOD)
    # Start the Qt main loop execution, exiting from this script
    # with the same return code of Qt application
    sys.exit(app.exec_())
