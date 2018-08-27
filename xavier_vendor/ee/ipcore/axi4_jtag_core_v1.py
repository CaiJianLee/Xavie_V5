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
        
    def jtag_logic_rst(self,tms_1_cycle_cnt):
        """ jtag_logic_rst, the JTAG state machine reset logic.
            
            Args:
                tms_1_cycle_cnt(int): 1~30, tms high level cycle count.

            Returns:
                None
        """
        # config tms path
        # tms_path_len = [0x0C] 
        # self.__axi4lite.write(0x12, tms_path_len, 1)
        # tms_path_data = [0xFF,0x00,0x00,0x00] 
        # self.__axi4lite.write(0x24, tms_path_data, 4)
        tms_path_len = tms_1_cycle_cnt + 2 
        self.__axi4lite.write(0x12, [tms_path_len], 1)
        tms_path_data = [0x00,0x00,0x00,0x00] 
        index = 0
        while(tms_1_cycle_cnt != 0):
            if(tms_1_cycle_cnt < 8):
                for i in range(tms_1_cycle_cnt):
                    tms_path_data[index] = tms_path_data[index] | (0x01<<i)
                tms_1_cycle_cnt = 0
            else:
                tms_1_cycle_cnt = tms_1_cycle_cnt - 8
                tms_path_data[index] = 0xFF;
            index = index + 1
            
        self.__axi4lite.write(0x24, tms_path_data, 4)
        # start jtag operate
        self.__axi4lite.write(0x11, [0x01], 1)
        # query state
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00):
            rd_data = self.__axi4lite.read(0x14,1)
        return None
        
    def jtag_run_test(self,run_test_cnt):
        """ jtag_run_test, loop idle state.
            
            Args:
                run_test_cnt(int): jtag run test TCK cnt.

            Returns:
                None
        """
        # config tms path
        tms_path_len = [0x20] 
        self.__axi4lite.write(0x12, tms_path_len, 1)
        tms_path_data = [0x00,0x00,0x00,0x00] 
        self.__axi4lite.write(0x24, tms_path_data, 4)
        for i in range(int(run_test_cnt/32)+1):
            # start jtag operate
            self.__axi4lite.write(0x11, [0x01], 1)
            # query state
            rd_data = self.__axi4lite.read(0x14,1)
            while (rd_data[0] == 0x00):
                rd_data = self.__axi4lite.read(0x14,1)
        return None
        
    def jtag_tran_operate(self,ir_bit_len,ir_data,dr_bit_len,dr_data):
        """ jtag tran operate, shift IR&DR
            
            Args:
                ir_bit_len(int): 0,3~16384, when ir_bit_len is 0, no ir operation.
                ir_data(list): ir shift data, at most 2048 bytes. Shift starts at first byte bit0.
                dr_bit_len(int): 0,3~16384, when dr_bit_len is 0, no dr operation.
                dr_data(list): dr shift data, at most 2048 bytes. Shift starts at first byte bit0.

            Returns:
                ir_shift_in_data(list): ir_bit_len valid bits, start first byte bit0.
                dr_shift_in_data(list): dr_bit_len valid bits, start first byte bit0.
        """
        # config tms path & ir_len(0x20~0x21),dr_len(0x22~0x23)
        if(ir_bit_len != 0) and (dr_bit_len != 0):
            tms_path_len = [0x14] 
            self.__axi4lite.write(0x12, tms_path_len, 1)
            tms_path_data = [0x30,0x67,0x00,0x00] 
            self.__axi4lite.write(0x24, tms_path_data, 4)
            ir_bit_len_list = self.__data_deal.int_2_list(ir_bit_len-1,2)
            dr_bit_len_list = self.__data_deal.int_2_list(dr_bit_len-1,2)
            self.__axi4lite.write(0x20,ir_bit_len_list+dr_bit_len_list,4)
        elif(ir_bit_len != 0) and (dr_bit_len == 0):
            tms_path_len = [0x07] 
            self.__axi4lite.write(0x12, tms_path_len, 1)
            tms_path_data = [0x33,0x00,0x00,0x00] 
            self.__axi4lite.write(0x24, tms_path_data, 4)
            ir_bit_len_list = self.__data_deal.int_2_list(ir_bit_len-1,2)
            dr_bit_len_list = [0x00,0x00]
            self.__axi4lite.write(0x20,ir_bit_len_list+dr_bit_len_list,4)
        elif(ir_bit_len == 0) and (dr_bit_len != 0):
            tms_path_len = [0x06] 
            self.__axi4lite.write(0x12, tms_path_len, 1)
            tms_path_data = [0x19,0x00,0x00,0x00] 
            self.__axi4lite.write(0x24, tms_path_data, 4)
            ir_bit_len_list = [0x00,0x00]
            dr_bit_len_list = self.__data_deal.int_2_list(dr_bit_len-1,2)
            self.__axi4lite.write(0x20,ir_bit_len_list+dr_bit_len_list,4)
        else:
            logger.error('parameter error')
            return False
        # wr ir_data & dr_data(0x28~0x2B)
        ir_wr_len = 0
        ir_list_len = 0
        if(ir_bit_len != 0):
            wr_data = []
            ir_list_len = len(ir_data)
            if((ir_list_len%4) != 0):
                wr_data = ((4-(ir_list_len%4))*[0x00])
            wr_data = ir_data + wr_data
            ir_wr_len = len(wr_data)
            self.__axi4lite.write_array(0x28,wr_data,ir_wr_len,32)
        dr_wr_len = 0
        dr_list_len = 0
        if(dr_bit_len != 0):
            wr_data = []
            dr_list_len = len(dr_data)
            if((dr_list_len%4) != 0):
                wr_data = ((4-(dr_list_len%4))*[0x00])
            wr_data = dr_data + wr_data
            dr_wr_len = len(wr_data)
            self.__axi4lite.write_array(0x28,wr_data,dr_wr_len,32)
        # start jtag tran operate
        self.__axi4lite.write(0x11, [0x01], 1)
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
        # rd ir&dr data(0x28~0x2B)
        # wr_dr_dcnt(0x2C~0x2D),rd_dr_dcnt(0x2E~0x2F)
        ir_shift_in_data = []
        dr_shift_in_data = []
        if(ir_bit_len != 0) and (dr_bit_len != 0):
            rd_data = self.__axi4lite.read_array(0x28,(ir_wr_len+dr_wr_len),32)
            ir_shift_in_data = rd_data[0:ir_list_len]
            dr_shift_in_data = rd_data[ir_wr_len:ir_wr_len+dr_list_len]
        elif(ir_bit_len != 0) and (dr_bit_len == 0):
            rd_data = self.__axi4lite.read_array(0x28,ir_wr_len,32)
            ir_shift_in_data = rd_data[0:ir_list_len]
        elif(ir_bit_len == 0) and (dr_bit_len != 0):
            rd_data = self.__axi4lite.read_array(0x28,dr_wr_len,32)
            dr_shift_in_data = rd_data[0:dr_list_len]
        # 0x30~0x31: RW--o_jtag_ir_end_state
        # 0x32~0x33: RW--o_jtag_dr_end_state
        # 0x34~0x35: R--i_jtag_current_state
        return (ir_shift_in_data,dr_shift_in_data)
