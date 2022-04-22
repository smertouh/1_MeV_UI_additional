import tango
from PyQt5.QtWidgets import QPushButton
from .TangoAttribute import TangoAttribute
from.TangoLED import TangoLED


class RF_anode_power_LED(TangoLED):
    def __init__(self, name, widget: QPushButton):
        self.state = TangoAttribute('binp/nbi/rfpowercontrol/state')
        self.ap = TangoAttribute('binp/nbi/rfpowercontrol/anode_power')
        super().__init__(name, widget)

    def read(self, force=False):
        self.st.read(force)
        self.ap.read(force)
        return self.attribute.read(force)

    def decorate(self):
        self.set_widget_value()

    def set_widget_value(self):
        try:
            if not self.state.value != tango.DevState.RUNNING or \
                    self.ap.value > 50.0
                self.widget.setChecked(False)
            else:
                self.widget.setChecked(True)
        except:
            self.widget.setChecked(False)
        return self.widget.isChecked()
