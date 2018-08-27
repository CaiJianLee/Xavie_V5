from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4SwdCore():
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 8192
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
    
    def enable(self):
        """Enable this FPGA function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] | 0x01;
        self.__axi4lite.write(0x10, rd_data, 1)
        return None
        
    def disable(self):
        """Disable this FPGA function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] & 0xFE;
        self.__axi4lite.write(0x10, rd_data, 1)
        return None

    def swd_freq_set(self,freq_data):
        """ Set swd clk freq parameter
            
            Args:
                freq_data(int): swd bus clock frequency, unit is Hz
            Returns:
                None
        """ 
        # read base clk freq: KHz
        rd_data = self.__axi4lite.read(0x01, 3)
        base_clk_freq = self.__data_deal.list_2_int(rd_data)
        # set swd freq
        swd_freq_div = int(((base_clk_freq*1000)/(freq_data*2))-2)
        if(swd_freq_div<0):
            swd_freq_div = 0
        wr_data = self.__data_deal.int_2_list(swd_freq_div,2)
        self.__axi4lite.write(0x04,wr_data,len(wr_data))
        return None
        
    def swd_rst_pin_ctrl(self,level):
        """ swd debug rst ctrl
            
            Args:
                level(string): 'L'--Low level,'H'--High level
            Returns:
                None
        """   
        # 0x12--bit7: rst_pin_level_ctrl, 0--high level; 1--low level
        rd_data = self.__axi4lite.read(0x12,1)
        if level == 'H':
            rd_data[0] = rd_data[0] & 0x7F;
        else:
            rd_data[0] = rd_data[0] | 0x80;
        self.__axi4lite.write(0x12, rd_data, 1)
        return None
        
    def swd_switch_timing_gen(self,timing_data): 
        """ swd_switch_timing_gen
            
            Args:
                timing_data(list): timing_data, bit order: first_byte_bit0-->bit7,second_byte_bit0-->bit7,...,last_byte_bit0-->bit7
            Returns:
                False | True
        """   
        # 0x30--wr switch timing data
        self.__axi4lite.write_array(0x30,timing_data,len(timing_data),8)
        # 0x12--bit0 = 1 : start switch timing output
        rd_data = self.__axi4lite.read(0x12,1)
        rd_data[0] = rd_data[0] | 0x01
        self.__axi4lite.write(0x12, rd_data, 1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100:
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100):
            logger.error('swd switch timing wait time out\n')
            return False
        return True

    def swd_wr_operate(self,swd_req_data,swd_wr_data):
        """ swd_wr_operate
            
            Args:
                swd_req_data(byte): swd_req_data
                swd_wr_data(list): swd_wr_data
            Returns:
                False | SWD RETURN ACK DATA(byte)
        """   
        # wr req data
        self.__axi4lite.write(0x23, [swd_req_data], 1)
        # wr wr_data
        self.__axi4lite.write(0x24,swd_wr_data,4)
        # start swd wr operate
        self.__axi4lite.write(0x11, [0x01], 1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100:
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100):
            logger.error('swd wr operate wait time out\n')
            return False
        # return ACK data(addr: 0x2C): 
        rd_data = self.__axi4lite.read(0x2C,1)
        return rd_data[0]
    
    def swd_rd_operate(self,swd_req_data):
        """ swd_rd_operate
            
            Args:
                swd_req_data(byte): swd_req_data
            Returns:
                False | swd_rd_data(list): 
                        Format, five bytes in total, 
                        the first four bytes are swd rd data, 
                        the last byte is ack data in bit0~bit2, and bit7 is swd rd data parity bit.
        """   
        # rd req data
        self.__axi4lite.write(0x23, [swd_req_data], 1)
        # start swd rd operate
        self.__axi4lite.write(0x11, [0x01], 1)
        # query state
        timeout_cnt = 0
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100:
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100):
            logger.error('swd rd operate wait time out\n')
            return False
        # return rd_data(addr: 0x28~0x2B) + ACK data(addr: 0x2C, [2:0]--ack data, [7]--swd rd data parity bit)
        swd_rd_data = self.__axi4lite.read(0x28,5)
        return swd_rd_data
