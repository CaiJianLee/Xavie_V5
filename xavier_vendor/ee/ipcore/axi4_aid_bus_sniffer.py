from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4AidBusSniffer():
    
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

    def rece_aid_req_data(self):
        """ rece_aid_req_data, Format:0x00+FB,0x00+SB,...,0x00+LB,0xFF+Frame_Number
            
            Args:
                None

            Returns:
                aid_req_data(list): Format:0x00+FB,0x00+SB,...,0x00+LB,0xFF+Frame_Number,len 0~2048(len=0 --> no aid request data)
        """
        # 0x20~0x23: aid_rece_timeout_cnt
        # 0x80: aid_req_fifo_rd & aid_req_fifo_rdata
        # 0x81~0x82: aid_req_fifo_dcnt
        # query fifo data len
        rd_data = self.__axi4lite.read(0x81,2)
        aid_req_len = self.__data_deal.list_2_int(rd_data)
        # rece aid req data
        aid_req_data = []
        if(aid_req_len != 0):
            aid_req_data = self.__axi4lite.read_array(0x80, aid_req_len, 8)
        return aid_req_data
        
    def rece_aid_resp_data(self):
        """ rece_aid_resp_data, Format:0x00+FB,0x00+SB,...,0x00+LB,0xFF+Frame_Number
            
            Args:
                None

            Returns:
                aid_resp_data(list): Format:0x00+FB,0x00+SB,...,0x00+LB,0xFF+Frame_Number,len 0~2048(len=0 --> no aid response data)
        """
        # 0x20~0x23: aid_rece_timeout_cnt
        # 0x84: aid_resp_fifo_rd & aid_resp_fifo_rdata
        # 0x85~0x86: aid_resp_fifo_dcnt
        # query fifo data len
        rd_data = self.__axi4lite.read(0x85,2)
        aid_resp_len = self.__data_deal.list_2_int(rd_data)
        # rece aid resp data
        aid_resp_data = []
        if(aid_resp_len != 0):
            aid_resp_data = self.__axi4lite.read_array(0x84, aid_resp_len, 8)
        return aid_resp_data
        