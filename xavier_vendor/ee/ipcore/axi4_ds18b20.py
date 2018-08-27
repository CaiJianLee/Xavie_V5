from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate
import time
__version__ = '1.0.0'

class Axi4Ds18b20(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        rd_data = self.__axi4lite.read(0x04,4)
        self.__clk_frequency = self.__data_deal.list_2_int(rd_data) 
    
    
    def disable(self):
        """  Disable function        """        
        self.__axi4lite.write(0x11,[0x00],1)
        return None

    def enable(self):
        """  Enable function        """         
        self.__axi4lite.write(0x11,[0x00],1)
        self.__axi4lite.write(0x11,[0x01],1)

        return None
        
    

    def config_ds18b20(self,wr_data):
        """  config_ds18b20 function  
			 wr_data is list
		"""   
        self.__axi4lite.write(0x14,wr_data,len(wr_data))  
        return None
  
  
    def measure_disbale(self):
        """  Disable function        """         
        self.__axi4lite.write(0x10,[0x00],1)
           
    
    def measure_enable(self):
        """  Enable function        """ 
        self.__axi4lite.write(0x10,[0x00],1)
        time.sleep(0.01)        
        self.__axi4lite.write(0x10,[0x01],1)   
         
    def rd_data(self):
        """  config_ds18b20 function  
			 wr_data is list
		"""   
        rd_data=self.__axi4lite.read(0x20,2)  
        return rd_data    
        
        
        
        
        