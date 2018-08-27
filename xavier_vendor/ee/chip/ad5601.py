 #-*- coding: UTF-8 -*-




#from __future__ import division
import time
import copy
from ee.ipcore.axi4_spi import Axi4Spi
from ee.common import logger
from ee.profile.profile import Profile
from ee.ipcore.axi4_gpio import Axi4Gpio
__version__="1.0"
AD5601_mode={
                 "normal":0x00,"tri_state":0xc0,"r_100k":0x80,"r_1k":0x40,
                 }
class AD5601(object):
    def __init__(self,spi_bus,vref):    
        self.spi_device= Axi4Spi(spi_bus)
        self.vref =vref
        self.spi_config()
    def spi_config(self):
        self.spi_device.config(500000,'pos')
    def spi_disable(self):
        self.spi_device.disable()    
    def spi_enable(self):
        self.spi_device.enable()
    
    def set_volt(self,volt):  
        """ set volt in normal mode 
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*256//self.vref
        if data1>255:
            data1=255
        if data1<0:
            data1=0
        data1=int(data1)
        temp0=AD5601_mode["normal"]|((data1>>2)&0x00ff)
        temp1=(data1<<6)&0x00ff
        data=[temp0,temp1]
        return self.spi_device.write(data)
    def set_tri_state_volt(self,volt):
        """ set volt in tri_state mode 
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*256//self.vref
        data1=int(data1)
        temp0=AD5601_mode["tri_state"]|((data1>>2)&0x00ff)
        temp1=(data1<<6)&0x00ff
        data=[temp0,temp1]
        return self.spi_device.write(data)
    def set_r_100k_volt(self,volt):
        """ set volt in  100k to gnd mode
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*256//self.vref
        data1=int(data1)
        temp0=AD5601_mode["r_100k"]|((data1>>2)&0x00ff)
        temp1=(data1<<6)&0x00ff
        data=[temp0,temp1]
        return self.spi_device.write(data)   
    def set_r_1k_volt(self,volt):
        """ set volt in 10k to gnd mode
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*256//self.vref
        data1=int(data1)
        temp0=AD5601_mode["r_1k"]|((data1>>2)&0x00ff)
        temp1=(data1<<6)&0x00ff
        data=[temp0,temp1]
        return self.spi_device.write(data)     