# coding: utf-8
"""
Created on Jul 28, 2019

@author: sanin
"""
from threading import Timer

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import PyQt5.QtGui as QtGui

from TangoWidgets.TangoCheckBox import TangoCheckBox
from TangoWidgets.TangoLED import TangoLED
from TangoWidgets.TangoLabel import TangoLabel
from TangoWidgets.TangoAbstractSpinBox import TangoAbstractSpinBox
from TangoWidgets.Utils import *

ORGANIZATION_NAME = 'BINP'
APPLICATION_NAME = 'Magnets_UI'
APPLICATION_NAME_SHORT = APPLICATION_NAME
APPLICATION_VERSION = '1_0'
CONFIG_FILE = APPLICATION_NAME_SHORT + '.json'

TIMER_PERIOD = 500  # ms


class MainWindow(QMainWindow):
    def __init__(self, loglevel=logging.DEBUG, ui_file='UI.ui', config_file='UI.json'):
        # Initialization of the superclass
        super().__init__(None)
        # logging config
        self.logger = config_logger(level=loglevel)
        # members definition
        self.n = 0
        self.elapsed = 0.0
        # Load the UI
        uic.loadUi(ui_file, self)
        # default main window parameters
        #self.resize(QSize(480, 640))                # size
        #self.move(QPoint(50, 50))                   # position
        #self.setWindowTitle('UI Application')       # title
        #self.setWindowIcon(QtGui.QIcon('UI_icon.ico'))  # icon

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=CONFIG_FILE)

        # read attributes TangoWidgets list
        self.rdwdgts = (
            # magnet 1
            #TangoLED('binp/nbi/magnet1/output_state', self.pushButton_38),
            self.create_widget('TangoLED', 'binp/nbi/magnet1/output_state', 'pushButton_38'),
            TangoLabel('binp/nbi/magnet1/voltage', self.label_149),
            TangoLabel('binp/nbi/magnet1/current', self.label_151),
            # magnet 2
            TangoLED('binp/nbi/magnet2/output_state', self.pushButton_41),
            TangoLabel('binp/nbi/magnet2/voltage', self.label_150),
            TangoLabel('binp/nbi/magnet2/current', self.label_152),
            # magnet 3
            TangoLED('binp/nbi/magnet3/output_state', self.pushButton_45),
            TangoLabel('binp/nbi/magnet3/voltage', self.label_157),
            TangoLabel('binp/nbi/magnet3/current', self.label_159),
            # magnet 4
            TangoLED('binp/nbi/magnet4/output_state', self.pushButton_46),
            TangoLabel('binp/nbi/magnet4/voltage', self.label_158),
            TangoLabel('binp/nbi/magnet4/current', self.label_160),
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
            TangoAbstractSpinBox('binp/nbi/magnet1/programmed_voltage', self.doubleSpinBox_53),
            TangoAbstractSpinBox('binp/nbi/magnet1/programmed_current', self.doubleSpinBox_55),
            # magnet 2
            TangoCheckBox('binp/nbi/magnet2/output_state', self.checkBox_55),
            TangoAbstractSpinBox('binp/nbi/magnet2/programmed_voltage', self.doubleSpinBox_54),
            TangoAbstractSpinBox('binp/nbi/magnet2/programmed_current', self.doubleSpinBox_56),
            # magnet 3
            TangoCheckBox('binp/nbi/magnet3/output_state', self.checkBox_56),
            TangoAbstractSpinBox('binp/nbi/magnet3/programmed_voltage', self.doubleSpinBox_57),
            TangoAbstractSpinBox('binp/nbi/magnet3/programmed_current', self.doubleSpinBox_59),
            # magnet 2
            TangoCheckBox('binp/nbi/magnet4/output_state', self.checkBox_57),
            TangoAbstractSpinBox('binp/nbi/magnet4/programmed_voltage', self.doubleSpinBox_58),
            TangoAbstractSpinBox('binp/nbi/magnet4/programmed_current', self.doubleSpinBox_60),
            # pg
            TangoCheckBox('binp/nbi/pg_offset/output_state', self.checkBox_52),
            TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_voltage', self.doubleSpinBox_50),
            TangoAbstractSpinBox('binp/nbi/pg_offset/programmed_current', self.doubleSpinBox_49),
            # extraction
            TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao00', self.doubleSpinBox_5),
            TangoAbstractSpinBox('ET7000_server/test/pet4_7026/ao01', self.doubleSpinBox_8),
            # acceleration
            TangoAbstractSpinBox('ET7000_server/test/pet9_7026/ao00', self.doubleSpinBox_9),
            TangoAbstractSpinBox('ET7000_server/test/pet7_7026/ao00', self.doubleSpinBox_10),
        )
        # Defile and start timer callback task
        self.timer = Timer(TIMER_PERIOD, self.timer_handler)
        # start timer
        self.timer.start()
        self.logger.info('\n\n------------ Attribute Config Finished -----------\n')

    def create_widget(self, class_name, attribute, control):
        try:
            widget = getattr(self, control)
            result = globals()[class_name](attribute, widget)
        except:
            result = None
        return result

    def on_quit(self):
        # Save global settings
        save_settings(self, file_name=CONFIG_FILE)
        self.timer.cancel()

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
