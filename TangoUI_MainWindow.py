# coding: utf-8
"""
Created on Jul 1, 200

@author: sanin
"""
import sys
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
APPLICATION_NAME = 'Tango_UI'
APPLICATION_VERSION = '0_0'
CONFIG_FILE = APPLICATION_NAME + '.json'
UI_FILE = APPLICATION_NAME + '.ui'

TIMER_PERIOD = 500  # ms
TIMER_LIMIT = 200  # ms


class TangoUI_MainWindow(QMainWindow):
    def __init__(self, loglevel=logging.DEBUG, ui_file=UI_FILE, config_file=CONFIG_FILE):
        # Initialization of the superclass
        super().__init__(None)
        # Logging config
        self.logger = config_logger(level=loglevel)
        # Attributes definition
        self.widgets = []
        self.n = 0
        self.elapsed = 0.0
        # Default main window parameters
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        self.setWindowTitle(APPLICATION_NAME)       # title
        # Load the UI
        uic.loadUi(ui_file, self)

        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

        restore_settings(self, file_name=config_file)

        self.create_widgets()
        self.logger.info('\n\n------------ Attribute Config Finished -----------\n')
        # Defile and start timer task
        self.timer = Timer(TIMER_PERIOD, self.timer_handler)
        self.timer.start()
        self.logger.info('\n\n------------ Timer Loop Activated -----------\n')

    def create_widget(self, class_name, attribute, control):
        widget = getattr(self, control)
        result = globals()[class_name](attribute, widget)
        self.logger.info('%s for %s at %s has been created' % (class_name, attribute, control))
        return result

    def create_widgets(self):
        self.widgets = []
        try:
            for item in self.config['TangoWidgets']:
                try:
                    widget = self.create_widget(item['class'], item['attribute'], item['widget'])
                    self.widgets.append(widget)
                except:
                    self.logger.warning('Error creating TangoWidget')
                    self.logger.debug('Exception:', exc_info=True)
        except:
            self.logger.warning('Error creating TangoWidget')
            self.logger.debug('Exception:', exc_info=True)
        return

    def on_quit(self):
        # Save global settings
        save_settings(self, file_name=CONFIG_FILE)
        self.timer.cancel()

    def timer_handler(self):
        self.elapsed = 0.0
        t0 = time.time()
        if len(self.widgets) <= 0:
            return
        for w in self.widgets[self.n:]:
            w.update()
            self.n += 1
            if time.time() - t0 > TIMER_LIMIT:
                break
        self.n = 0
        self.elapsed = time.time() - self.elapsed


if __name__ == '__main__':
    # Load options from command line
    if len(sys.argv) > 1:
        UI_FILE = sys.argv[1]
    if len(sys.argv) > 2:
        CONFIG_FILE = sys.argv[2]
    # Create the GUI application
    app = QApplication(sys.argv)
    # Instantiate the main window
    dmw = TangoUI_MainWindow()
    app.aboutToQuit.connect(dmw.on_quit)
    # Show it
    dmw.show()
    # Start the Qt main loop execution, exiting from this script
    # with the same return code of Qt application
    sys.exit(app.exec_())
