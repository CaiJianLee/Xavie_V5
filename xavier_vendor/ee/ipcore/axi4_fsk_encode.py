from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4FskEncode():
    
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
     
    def send_fsk_decode_data(self,fsk_send_data):
        """ send_fsk_decode_data, include checksum data
            
            Args:
                fsk_send_data(list): fsk send data

            Returns:
                True | False
        """
        # 0x12-[0]: fsk_encode_start 1 -- valid
        # 0x13-[0]: fsk_encode_state 0--busy,1--ready
        # 0x20: fsk_fifo_wr & fsk_fifo_wdata
        # 0x21~0x22: fsk_wr_data_len
        fsk_data_len = len(fsk_send_data)
        if(fsk_data_len == 0):
            return False
        # send fsk data to fsk data_fifo
        self.__axi4lite.write_array(0x20, fsk_send_data, fsk_data_len, 8)    
            
        # fsk encode start
        self.__axi4lite.write(0x12,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x13,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 1000:
            time.sleep(0.01)
            rd_data = self.__axi4lite.read(0x13,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 1000):
            return False
        return True
    
    