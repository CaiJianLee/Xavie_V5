from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4AskDecode():
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 8192
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        
    def enable(self):
        """Enable this FPGA function"""
        self.__axi4lite.write(0x10,[0x01],1)
        return None
        
    def disable(self):
        """Disable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        return None

    def get_ask_decode_data(self):
        """ get_ask_decode_data
            
            Args:
                None

            Returns:
                ask_data(list): ask decode data
        """
        # get_ask_decode_data
        # 0x20 rd_ask_data
        # 0x21~0x22 ask_data_len
        rd_data = self.__axi4lite.read(0x21,2)
        ask_data_len = self.__data_deal.list_2_int(rd_data)
        ask_data = []
        if(ask_data_len != 0):
            ask_data = self.__axi4lite.read_array(0x20, ask_data_len, 8)
        
        return ask_data
    
    