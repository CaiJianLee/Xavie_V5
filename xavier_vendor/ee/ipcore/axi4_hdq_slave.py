from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4HdqSlave(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))    
        self.__axi4_clk_frequency = 125000000
        self.__data_deal = DataOperate()
    def disable(self):
        """  Disable function        """    
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data], 1)
        return None    

    def enable(self):
        """  Enable function        """  
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data], 1)
        wr_data = rd_data[0] & 0xF0 | 0x01
        self.__axi4lite.write(0x10, [wr_data], 1)
        return None
               
    def hdq_receive_wr_addr(self):
        """ get hdq_master input wr_addr and wr flag
            
            Args:
                None
            Returns:
                the hdq_wr_addr and wr flag of input hdq_master
        """ 
        rd_data = self.__axi4lite.read(0x11, 1)
        hdq_wr_addr = self.__data_deal.list_2_int(rd_data)              
        return hdq_wr_addr      
      
    def hdq_receive_wr_data(self):
        """ get hdq_master input wr_data            
            Args:
                None
            Returns:
                the hdq_wr_data and wr flag of input hdq_master
        """ 
        rd_data = self.__axi4lite.read(0x12, 1)
        hdq_wr_data = self.__data_deal.list_2_int(rd_data)              
        return hdq_wr_data      
        
    def hdq_recevice_rd_addr(self):
        """ get hdq_master input rd_addr and wr flag
            
            Args:
                None
            Returns:
                the hdq_rd_addr and wr flag of input hdq_master
        """ 
        rd_data = self.__axi4lite.read(0x13, 1)
        hdq_rd_addr = self.__data_deal.list_2_int(rd_data)              
        return hdq_rd_addr      
 
    def hdq_sent_rd_data(self,wr_data):
        """ to hdq_master output rd_data 
            
            Args:
                the hdq_rd_data :hdq_slave send to hdq master
            Returns:
                None
        """ 
        self.__axi4lite.wite(0x14, [wr_data],1)           
        return None            