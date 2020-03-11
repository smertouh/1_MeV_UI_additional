from PyQt5.QtWidgets import QPushButton
from .TangoAttribute import TangoAttribute
from.TangoLED import TangoLED


class Timer_on_LED(TangoLED):
    def __init__(self, name, widget: QPushButton):
        super().__init__(name, widget)
        self.timer_state_channels = ['channel_state'+str(k) for k in range(12)]
        self.value = False

    def read(self, force=False):
        self.value = self.check_state()
        return self.value

    def set_widget_value(self):
        self.widget.setChecked(self.value)
        return self.widget.isChecked()

    def decorate(self):
        self.set_widget_value()

    def check_state(self):
        timer_device = self.attribute.device_proxy
        if timer_device is None:
            return False
        avs = []
        try:
            avs = timer_device.read_attributes(self.timer_state_channels)
        except:
            pass
        state = False
        for av in avs:
            state = state or av.value
        return state
