from PyQt5.QtWidgets import QPushButton
from .TangoAttribute import TangoAttribute
from.TangoLED import TangoLED


class RF_ready_LED(TangoLED):
    def __init__(self, name, widget: QPushButton):
        self.av = TangoAttribute('binp/nbi/adc0/chan16')  # anode voltage > 8.0 kV
        self.cc = TangoAttribute('binp/nbi/adc0/chan22')  # cathode current > 0.1
        self.pr = TangoAttribute('binp/nbi/timing/di60')  #
        super().__init__(name, widget)

    def read(self, force=False):
        self.av.read(True)
        self.cc.read(True)
        self.pr.read(True)
        return self.attribute.read(force)

    def decorate(self):
        self.set_widget_value()

    def set_widget_value(self):
        try:
            if not self.av.is_valid() or self.av.value() < 8.0 or \
                    not self.cc.is_valid() or self.cc.value() < 0.1 or \
                    not self.pr.value():
                self.widget.setChecked(False)
            else:
                self.widget.setChecked(True)
        except:
            self.widget.setChecked(False)
        return self.widget.isChecked()
