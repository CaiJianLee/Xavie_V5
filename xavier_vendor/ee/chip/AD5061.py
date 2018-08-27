#-*- coding: UTF-8 -*-




#from __future__ import division
import time
import copy
from ee.ipcore.axi4_spi import Axi4Spi
from ee.common import logger
from ee.profile.profile import Profile
from ee.ipcore.axi4_gpio import Axi4Gpio
__version__="1.0"
AD5061_mode={
                 "normal":0x00,"tri_state":0x01,"r_100k":0x10,"r_10k":0x11,
                 }

class AD5061(object):
    def __init__(self,spi_bus,vref):    
        self.spi_device= Axi4Spi(spi_bus)
        self.vref = vref
        self.spi_config()
    def spi_config(self):
        self.spi_device.config(500000,'pos')
        
    def spi_enable(self):
        self.spi_device.enable()
    def spi_disable(self):
        self.spi_device.disable()
        
    
    def set_volt(self,volt):  
        """ set volt in normal mode 
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=65536*volt//self.vref
        data1=int(data1)
        if data1>65535:
            data1=65535
        if data1<0:
            data1=0
        temp0=AD5061_mode["normal"]
        temp1=(data1>>8)&0x00ff
        temp2=data1&0x00ff       
        data=[temp0,temp1,temp2]
        return self.spi_device.write(data)
    def set_tri_state_volt(self,volt):
        """ set volt in tri_state mode 
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*65536//self.vref
        data1=int(data1)
        temp0=AD5061_mode["tri_state"]
        temp1=data1&0x00ff
        temp2=(data1>>8)&0x00ff
        data=[temp0,temp1,temp2]
        return self.spi_device.write(data)
    def set_r_100k_volt(self,volt):
        """ set volt in  100k to gnd mode
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*65536//self.vref
        data1=int(data1)
        temp0=AD5061_mode["r_100k"]
        temp1=data1&0x00ff
        temp2=(data1>>8)&0x00ff
        data=[temp0,temp1,temp2]
        return self.spi_device.write(data)   
    def set_r_10k_volt(self,volt):
        """ set volt in 10k to gnd mode
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        data1=volt*65536//self.vref
        data1=int(data1)
        temp0=AD5601_mode["r_10k"]
        temp1=data&0x00ff
        temp2=(data>>8)&0x00ff
        data=[temp0,temp1,temp2]
        return self.spi_device.write(data)     
    
    def soft_reset(self):
        """ reset ad5601
            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.spi_disable()
        self.spi_enable()
        temp0=0xff
        temp1=0xff
        temp2=0xff
        data=[temp0,temp1,temp2]
        return self.spi_device.write(data)     
    
           
        
        

        







