__author__ = 'Mingcheng'

import ee.common.utility as utility
from ee.bus.ci2c import CI2cBus
from ee.ipcore.axi4_iic import Axi4I2c
import ee.overlay.busswitch as BusSwitch
from ee.profile.profile import Profile

class I2cBus(object):
    
    def __init__(self, name, channel = None):
        self._name = name
        self._profile=Profile.get_bus_by_path(name)
        self._channel = None if channel == 'none' else channel
        if utility.mount_on_fpga(name) is None:
            self._bus = CI2cBus(name)
        else:
            self._bus = Axi4I2c(name)
            self._bus.config(int(self._profile["rate"]))

    def write(self, dev_addr, data):
        if self._channel is not None:
            switcher = BusSwitch.select_channel(self._channel)
            if switcher:
                result = self._bus.write(dev_addr, data)
                switcher.close_channel()
                return result
            else:
                return False;
        else:
            return self._bus.write(dev_addr, data)
        
    def read(self, dev_addr, length):
        if self._channel is not None:
            switcher = BusSwitch.select_channel(self._channel)
            if switcher:
                result = self._bus.read(dev_addr, length)
                switcher.close_channel()
                return result
            else:
                return False;
        else:
            return self._bus.read(dev_addr, length)
        
    def rdwr(self, dev_addr, write_data, read_length):
        if self._channel is not None:
            switcher = BusSwitch.select_channel(self._channel)
            if switcher:
                result = self._bus.rdwr(dev_addr, write_data, read_length)
                switcher.close_channel()
                return result
            else:
                return False;
        else:
            return self._bus.rdwr(dev_addr, write_data, read_length)

    def config(self, rate):
        if utility.mount_on_fpga(self._name) is not None:
            return self._bus.config(int(rate))
        
    def disable(self):
        if utility.mount_on_fpga(self._name) is not None:
            return self._bus.disable()
    def enable(self):
        if utility.mount_on_fpga(self._name) is not None:
            return self._bus.enable()