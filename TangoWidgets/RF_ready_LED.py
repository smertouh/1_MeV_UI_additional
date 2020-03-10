from PyQt5.QtWidgets import QPushButton
import tango
from .TangoAttribute import TangoAttribute
from.TangoLED import TangoLED


class RF_ready_LED(TangoLED):
    def __init__(self, name, widget: QPushButton):
        super().__init__(name, widget)
        dn = 'binp/nbi/adc0'
        if dn not in TangoAttribute.devices:
            TangoAttribute.devices[dn] = tango.DeviceProxy(dn)
        self.adc_device = TangoAttribute.devices[dn]
        dn = 'binp/nbi/timing'
        if dn not in TangoAttribute.devices:
            TangoAttribute.devices[dn] = tango.DeviceProxy(dn)
        self.timer_device = TangoAttribute.devices[dn]

    def set_widget_value(self):
        try:
            self.av = self.adc_device.read_attribute('chan16')
            self.cc = self.adc_device.read_attribute('chan22')
            pr = self.timer_device.read_attribute('di60')
            if self.av.quality != tango._tango.AttrQuality.ATTR_VALID or \
                    self.av.value * self.av_coeff < 8.0 or \
                    self.cc.quality != tango._tango.AttrQuality.ATTR_VALID or \
                    self.cc.value * self.cc_coeff < 0.1 or \
                    not pr.value:
                self.pushButton_1.setChecked(False)
            else:
                self.pushButton_1.setChecked(True)
        except:
            self.pushButton_1.setChecked(False)

        self.widget.setChecked(bool(self.attribute.value()))
        return self.attribute.value()
