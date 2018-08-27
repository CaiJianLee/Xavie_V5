#-*- coding: UTF-8 -*-




#from __future__ import division
import time
import copy
from ee.ipcore.axi4_spi import Axi4Spi
from ee.common import logger
from ee.ipcore.axi4_gpio import Axi4Gpio
__version__="1.0"
wait_time={
           "t7":20,
           "t8":650, 
           "t12":8,     
           }
class AD7091(object):
    def __init__(self,spi_bus,gpio_divice,convst_gpio,vref):  
        self.spi_device= Axi4Spi(spi_bus)
        self.gpio_device = gpio_divice
        self.gpio_device.gpio_set([(convst_gpio,1)])
        self.convst_gpio=convst_gpio
        self.vref = vref
        self.spi_config()

        
    def spi_config(self):
        self.spi_device.config(20000,'neg')
        
    def spi_enable(self):
        self.spi_device.enable()
        
    def spi_disable(self):
        self.spi_device.disable()
    
    def measure_volt(self):  
        """ measure  volt in normal mode  without busy indicator
            Returns:
                bool:  False | voltage value, False for  spi read fail 
        """
        self.spi_disable()
        self.spi_enable()
        self.gpio_device.gpio_set([(self.convst_gpio,1)])
        self.gpio_device.gpio_set([(self.convst_gpio,0)])
        self.gpio_device.gpio_set([(self.convst_gpio,1)])
        ret=self.spi_device.read(2)   
        data=0
        if ret==False:
            return False
        else:
           data=(ret[1]+ret[0]*256)/16
           volt=data*self.vref /4096.0
        return volt
    def measure_average_volt_(self,measure_time):  
        """ measure average volt in normal mode  without busy indicator
            Returns:
                bool:  False | voltage value, False for  spi read fail 
        """
        sum=0
        for i in rang( measure_time):
            ret=self.measure_volt()
            if ret==False:
                 return False
            else:
                sum+=ret
        return sum/measure_time
                
 

    
        
  