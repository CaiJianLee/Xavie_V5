from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4FskDecode():
    
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
  
    def get_fsk_decode_state(self):
        """ get_fsk_decode_state
            
            Args:
                None

            Returns:
                True | False: True -- FSK decode Parity bit is ok, False -- FSK decode Parity bit is error.
        """
        # 0x12 bit0--Parity bit state
        rd_data = self.__axi4lite.read(0x12,1)
        self.__axi4lite.write(0x12,[0x01],1)
        if(rd_data[0] == 0x01):
            return False
        else:
            return True
    
    def get_fsk_decode_data(self):
        """ get_fsk_decode_data
            
            Args:
                None

            Returns:
                fsk_data(list): fsk decode data
        """
        # 0x20 rd_fsk_data
        # 0x21~0x22 fsk_data_len
        rd_data = self.__axi4lite.read(0x21,2)
        fsk_data_len = self.__data_deal.list_2_int(rd_data)
        fsk_data = []
        if(fsk_data_len != 0):
            fsk_data = self.__axi4lite.read_array(0x20, fsk_data_len, 8)
        
        return fsk_data
    
    