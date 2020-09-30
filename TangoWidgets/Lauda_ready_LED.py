from PyQt5.QtWidgets import QPushButton
from .TangoAttribute import TangoAttribute
from.TangoLED import TangoLED


class Lauda_ready_LED(TangoLED):
    def __init__(self, name, widget):
        self.value = False
        if not name.endswith('/'):
            name += '/'
        self.valve = TangoAttribute(name + '6230_0')  # output valve
        super().__init__(name + '6230_7', widget)
        self.motor = self.attribute  # Lauda pump motor

    def read(self, force=False):
        self.value = self.motor.read(True) and self.valve.read(True)
        return self.value

    def decorate(self):
        self.set_widget_value()

    def set_widget_value(self):
        try:
            if self.valve.is_valid() and self.motor.is_valid() and self.value:
                self.widget.setChecked(True)
            else:
                self.widget.setChecked(False)
        except:
            self.widget.setChecked(False)
        return self.widget.isChecked()
