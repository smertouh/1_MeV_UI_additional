# coding: utf-8
"""
Created on Jul 1, 200

@author: sanin
"""
import sys
from threading import Timer

from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

#from TangoWidgets.TangoCheckBox import TangoCheckBox
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
TIMER_LIMIT = 300  # ms


class TangoUI_MainWindow(QMainWindow):
    def __init__(self, config_file=CONFIG_FILE, loglevel=logging.DEBUG, ui_file=UI_FILE):
        # Initialization of the superclass
        super().__init__(None)
        # Default logging config
        self.logger = config_logger(level=loglevel)
        # Default attributes definition
        self.config = {}
        self.widgets = []
        self.n = 0
        self.elapsed = 0.0
        self.config_file = config_file
        self.ui_file = ui_file
        self.timer_period = TIMER_PERIOD
        # Default main window parameters
        self.resize(QSize(480, 640))                # size
        self.move(QPoint(50, 50))                   # position
        self.setWindowTitle(APPLICATION_NAME)       # title
        # Restore config
        self.restore_config(self.config_file)
        # Load the UI
        uic.loadUi(self.ui_file, self)
        # Create widgets
        self.create_widgets()
        self.logger.info('\n\n------------ Attribute Config Finished -----------\n')
        # Defile and start timer task
        self.timer = Timer(self.timer_period, self.timer_handler)
        self.timer.start()
        # Print start message
        print(APPLICATION_NAME + ' version ' + APPLICATION_VERSION + ' started')

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
        # Save settings on exit
        self.save_config(self.config_file)
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

    def restore_config(self, file_name='config.json'):
        self.config = {}
        try:
            # Open and read config file
            with open(file_name, 'r') as configfile:
                s = configfile.read()
            # Interpret file contents by json
            self.config = json.loads(s)
            # Restore log level
            if 'log_level' in self.config:
                v = self.config['log_level']
                self.logger.setLevel(v)
            # Restore window size and position (can be changed by user during operation)
            if 'main_window' in self.config:
                self.resize(QSize(self.config['main_window']['size'][0], self.config['main_window']['size'][1]))
                self.move(QPoint(self.config['main_window']['position'][0], self.config['main_window']['position'][1]))
            # UI file name
            if 'UI_file' in self.config:
                self.ui_file = self.config['UI_file']
            # Timer period
            if 'timer_period' in self.config:
                self.timer_period = self.config['timer_period']
            # OK message
            self.logger.info('Configuration restored from %s' % file_name)
        except:
            self.logger.warning('Configuration restore error from %s' % file_name)
            self.logger.debug('Exception:', exc_info=True)
        return self.config

    def save_config(self, file_name='config.json'):
        try:
            # Save current window size and position
            p = self.pos()
            s = self.size()
            self.config['main_window'] = {'size': (s.width(), s.height()), 'position': (p.x(), p.y())}
            # Write to file
            with open(file_name, 'w') as configfile:
                configfile.write(json.dumps(self.config, indent=4))
            # OK message
            self.logger.info('Configuration saved to %s' % file_name)
            return True
        except:
            self.logger.warning('Error saving configuration to %s' % file_name)
            self.logger.debug('Exception:', exc_info=True)
            return False


if __name__ == '__main__':
    # Load options from command line
    if len(sys.argv) > 1:
        CONFIG_FILE = sys.argv[1]
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
