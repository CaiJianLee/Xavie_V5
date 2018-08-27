from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4AskEncode():
    
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
       
    def set_ask_data_frequency(self,ask_data_freq):
        """ set_ask_date_frequency
            
            Args:
                ask_data_freq(int): ask data frequency,100~100000Hz

            Returns:
                None
        """
        rd_data = self.__axi4lite.read(0x04,4)
        base_freq = self.__data_deal.list_2_int(rd_data)
        data_freq_cnt = int(base_freq/ask_data_freq/2)-2
        wr_data = self.__data_deal.int_2_list(data_freq_cnt,3)
        self.__axi4lite.write(0x14,wr_data,len(wr_data))
        return None
   
    def send_ask_decode_data(self,ask_send_data):
        """ send_ask_decode_data, include checksum data
            
            Args:
                ask_send_data(list): ask send data

            Returns:
                True | False
        """
        # 0x12-[0]: ask_encode_start 1 -- valid
        # 0x13-[0]: ask_encode_state 0--busy,1--ready
        # 0x20: ask_fifo_wr & ask_fifo_wdata
        # 0x21~0x22: ask_wr_data_len
        ask_data_len = len(ask_send_data)
        if(ask_data_len == 0):
            return False
        # send ask data to ask data_fifo
        self.__axi4lite.write_array(0x20, ask_send_data, ask_data_len, 8)
        
        # ask encode start
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
    
    