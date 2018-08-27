""" CAT24C08 chip driver

"""
import ee.overlay.i2cbus as I2cBus
from ee.common import logger
from ee.chip.cat24cxx import CAT24Cxx



class CAT24C32(CAT24Cxx):
    """CAT24C32 chip driver

    Public methods:
    - read: read datas from eeprom
    - write: write datas to eeprom 
    """
    def __init__(self,profile):

        super(CAT24C32,self).__init__(profile,"cat32")



