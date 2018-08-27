from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4JtagCore():
    
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

    def jtag_freq_set(self,freq_data):
        """ jtag tck freq set
            
            Args:
                freq_data(int): jtag tck freq set,Hz(1000~25000000)

            Returns:
                None
        """
        rd_data = self.__axi4lite.read(0x01, 3)
        base_clk_freq = self.__data_deal.list_2_int(rd_data)
        # set jtag freq
        jtag_freq_div = int(((base_clk_freq*1000)/(freq_data*2))-2)
        if(jtag_freq_div<0):
            jtag_freq_div = 0
        wr_data = self.__data_deal.int_2_list(jtag_freq_div,2)
        self.__axi4lite.write(0x04,wr_data,len(wr_data))
        return None
        
    def jtag_rst_pin_ctrl(self,level):
        """ jtag rst pin ctrl
            
            Args:
                level(string): 'H'--high level,'L'--low level

            Returns:
                None
        """
        rd_data = self.__axi4lite.read(0x13,1)
        if level == 'H':
            rd_data[0] = rd_data[0] & 0x7F;
        else:
            rd_data[0] = rd_data[0] | 0x80;
        self.__axi4lite.write(0x13, rd_data, 1)
        return None
        
    def jtag_logic_rst(self):
        """ jtag_logic_rst, the JTAG state machine reset logic.
            
            Args:
                None

            Returns:
                None
        """
        rd_data = self.__axi4lite.read(0x13,1)
        rd_data[0] = rd_data[0] | 0x01;    
        self.__axi4lite.write(0x13, rd_data, 1)
        rd_data[0] = rd_data[0] & 0xFE;    
        self.__axi4lite.write(0x13, rd_data, 1)
        return None
        
    def jtag_tran_operate(self,ir_bit_len,ir_data,dr_bit_len,dr_data):
        """ jtag tran operate, shift IR&DR
            
            Args:
                ir_bit_len(int): 0~32, when ir_bit_len is 0, no ir operation.
                ir_data(list): ir shift data, at most 4 byte data. Shift starts at first byte bit0.
                dr_bit_len(int): 0~16384, when dr_bit_len is 0, no dr operation.
                dr_data(list): dr shift data, at most 2048 bytes. Shift starts at first byte bit0.

            Returns:
                dr_shift_in_data(list): dr_bit_len valid bits, start first byte bit0.
        """
        # ir_len(0x20~0x21),dr_len(0x22~0x23)
        ir_bit_len_list = self.__data_deal.int_2_list(ir_bit_len,2)
        dr_bit_len_list = self.__data_deal.int_2_list(dr_bit_len,2)
        self.__axi4lite.write(0x20,ir_bit_len_list+dr_bit_len_list, 4)
        # ir_data(0x24~0x27)
        if(ir_bit_len != 0):
            self.__axi4lite.write(0x24,ir_data,len(ir_data))
        # start jtag tran operate
        self.__axi4lite.write(0x11, [0x01], 1)
        # dr_data(0x28~0x2B)
        dr_data_len = len(dr_data)
        wr_data_len = 0
        wr_data = []
        if(dr_bit_len != 0):
            if((dr_data_len%4) != 0):
                wr_data = ((4-(dr_data_len%4))*[0x00])
            wr_data = dr_data + wr_data
            wr_data_len = len(wr_data)
            self.__axi4lite.write_array(0x28,wr_data,wr_data_len,32)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 10000:
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 10000):
            logger.error('jtag tran operate wait time out')
            return False
        # rd dr data(0x28~0x2B)
        # wr_dr_dcnt(0x2C~0x2D),rd_dr_dcnt(0x2E~0x2F)
        dr_shift_in_data = []
        if(dr_bit_len != 0):
            dr_shift_in_data = self.__axi4lite.read_array(0x28,wr_data_len,32)
        return dr_shift_in_data[0:dr_data_len]
