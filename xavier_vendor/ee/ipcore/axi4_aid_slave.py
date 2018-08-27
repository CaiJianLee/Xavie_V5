# -*- coding: utf-8 -*-
from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4AidSlave():
    
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
  
    def cfg_aid_data(self,aid_index,aid_req_data,aid_req_data_mask,aid_resp_data):
        """ cfg aid slave module aid command data, include request and response command data.
            
            Args:
                aid_index(int): 0~63, up to 64 AID commands are supported, this parameter is the index number, and just a number,
                aid_req_data(list): use for match aid master req commamd(include CRC data), len 1~27
                aid_req_data_mask(int): aid master req commamd byte data mask, used to indicate the bytes that need to be detected.
                                        bit0--byte0,bit1--byte1,...bit_n--byte_n; 0--ineffectual,1--effective  
                aid_resp_data(list): use for resp aid master aid command(except CRC data), len 1~31

            Returns:
                None
        """
        # 0x20: aid_req_ram_wr
        # 0x21~0x22: aid_req_ram_addr
        # 0x23: wr--aid_req_ram_wdata & rd--aid_req_ram_rdata
        # 0x24~0x27: aid_rece_timeout_cnt
        # 0x30: aid_resp_ram_wr
        # 0x31~0x32: aid_resp_ram_addr
        # 0x33: wr--aid_resp_ram_wdata & rd--aid_resp_ram_rdata
        
        # aid_buff_num=64, aid_buff_len_max=32, aid_buff_content = 1_byte_len + 31_byte_aid_data; first byte is len info
        aid_req_len = len(aid_req_data)
        aid_resp_len = len(aid_resp_data)-1
        req_data_mask_data = self.__data_deal.int_2_list(aid_req_data_mask, 4)
        # cfg aid req len
        aid_req_addr = aid_index * 32;
        wr_data = self.__data_deal.int_2_list(aid_req_addr, 2)
        self.__axi4lite.write(0x21, wr_data, len(wr_data))
        wr_data = self.__data_deal.int_2_list(aid_req_len, 1)
        self.__axi4lite.write(0x23, [wr_data[0]], 1)
        self.__axi4lite.write(0x20, [0x01], 1)
        # cfg aid req mask
        for i in range(0, 4):
            aid_req_addr = aid_req_addr + 1
            wr_data = self.__data_deal.int_2_list(aid_req_addr, 2)
            self.__axi4lite.write(0x21, wr_data, len(wr_data))
            wr_data[0] = req_data_mask_data[i]
            self.__axi4lite.write(0x23, [wr_data[0]], 1)
            self.__axi4lite.write(0x20, [0x01], 1)
        # cfg aid req data
        for i in range(0, aid_req_len):
            aid_req_addr = aid_req_addr + 1
            wr_data = self.__data_deal.int_2_list(aid_req_addr, 2)
            self.__axi4lite.write(0x21, wr_data, len(wr_data))
            wr_data[0] = aid_req_data[i]
            self.__axi4lite.write(0x23, [wr_data[0]], 1)
            self.__axi4lite.write(0x20, [0x01], 1)
        # rece aid req cfg data from req ram
        # rece_aid_req_data = []
        # aid_req_addr = aid_index * 32;
        # for i in range(0, aid_req_len+1):
        #     wr_data = self.__data_deal.int_2_list(aid_req_addr, 2)
        #     self.__axi4lite.write(0x21, wr_data, len(wr_data))
        #     rd_data = self.__axi4lite.read(0x23,1)
        #     rece_aid_req_data = rece_aid_req_data + rd_data;
        #     aid_req_addr = aid_req_addr + 1
        # print('AID_REQ_RAM_INDEX:', aid_index, 'AID_REQ_RAM_DATA:', aid_req_data, 'AID_REQ_RAM_DATA_LEN:', len(aid_req_data))
        # print('AID_REQ_RAM_INDEX:', aid_index, 'RECE_AID_REQ_RAM_DATA:', rece_aid_req_data)
        
        # cfg aid resp len
        aid_resp_addr = aid_index * 32;
        wr_data = self.__data_deal.int_2_list(aid_resp_addr, 2)
        self.__axi4lite.write(0x31, wr_data, len(wr_data))
        wr_data = self.__data_deal.int_2_list(aid_resp_len, 1)
        self.__axi4lite.write(0x33, [wr_data[0]], 1)
        self.__axi4lite.write(0x30, [0x01], 1)
        # cfg aid resp data
        for i in range(0, aid_resp_len):
            aid_resp_addr = aid_resp_addr + 1
            wr_data = self.__data_deal.int_2_list(aid_resp_addr, 2)
            self.__axi4lite.write(0x31, wr_data, len(wr_data))
            wr_data[0] = aid_resp_data[i]
            self.__axi4lite.write(0x33, [wr_data[0]], 1)
            self.__axi4lite.write(0x30, [0x01], 1)
        # rece aid resp cfg data from resp ram
        # rece_aid_resp_data = []
        # aid_resp_addr = aid_index * 32;
        # for i in range(0, aid_resp_len+1):
        #     wr_data = self.__data_deal.int_2_list(aid_resp_addr, 2)
        #     self.__axi4lite.write(0x31, wr_data, len(wr_data))
        #     rd_data = self.__axi4lite.read(0x33,1)
        #     rece_aid_resp_data = rece_aid_resp_data + rd_data
        #     aid_resp_addr = aid_resp_addr + 1
        # print('AID_RESP_RAM_INDEX:', aid_index, 'AID_RESP_RAM_DATA:', aid_resp_data, 'AID_RESP_RAM_DATA_LEN:', len(aid_resp_data))
        # print('AID_RESP_RAM_INDEX:', aid_index, 'RECE_AID_RESP_RAM_DATA:', rece_aid_resp_data)
        return None
        
    def aid_slave_init(self):
        """ init aid slave module request and response command data,  last byte is CRC
            
            Args:
                None

            Returns:
                None
        """
        aid_req_dict = {
            0:[0x74,0x00,0x02,0x1F]};
        #    1:[0x74,0x00,0x01,0xFD],
        #    2:[0xE0,0x04,0x01,0x00,0x00,0xEE,0x01,0x01,0xC4],
        #    3:[0xE0,0x04,0x01,0x00,0x00,0x02,0x06,0x04,0xF1,0x00,0x00,0x00,0x00,0x42],
        #    4:[0x70,0x00,0x00,0x3D],
        #    5:[0x74,0x00,0x02,0x1F],
        #    6:[0x76,0x10]};
        aid_resp_dict = {
            0:[0x75,0x20,0x0A,0x00,0x00,0x00,0x00,0x17]};
        #    1:[0x75,0x04,0xF1,0x00,0x00,0x00,0x00,0xAB],
        #    2:[0xE1,0xAA,0xE1],
        #    3:[0xE1,0x55,0xD4],
        #    4:[0x71,0x93],
        #    5:[0x75,0x20,0x0A,0x00,0x00,0x00,0x00,0x17],    # Tristar MUX configured to debug ports (USB+UART0)
        #    5:[0x75,0xE0,0x00,0x00,0x00,0x00,0x00,0x35],   # pad reboot cmd
        #    5:[0x75,0xE0,0x08,0x00,0x00,0x00,0x00,0x0B],    # Tristar reset - we’ve done this and verified
        #    5:[0x75,0xA0,0x08,0x00,0x00,0x00,0x00,0x7E],    # Tristar MUX configured to SWD DFU + debug ports (SWD + USB + UART0)
        #    6:[0x77,0x02,0x01,0x02,0x80,0x60,0x00,0xE0,0x87,0x75,0x6B,0x37]};
        for i in range(0,1):
        #    print(i,aid_req_dict[i],aid_resp_dict[i])
            self.cfg_aid_data(i,aid_req_dict[i],0x00000003,aid_resp_dict[i])
        return None
    