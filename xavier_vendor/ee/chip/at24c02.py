""" AT24C04 chip driver

"""
import ee.overlay.i2cbus as I2cBus
from ee.common.logger import *
from ee.chip.at24cxx import *



class AT24C02(AT24Cxx):
    """AT24C04 chip driver

    Public methods:
    - read: read datas from eeprom
    - write: write datas to eeprom 
    """
    def __init__(self,profile):
        super(AT24C02,self).__init__(profile,"at02")



