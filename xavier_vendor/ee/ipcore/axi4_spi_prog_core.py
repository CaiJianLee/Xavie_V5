from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

__version__ = '1.0.1'

class Axi4SpiProgCore():
    
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

    def spi_module_config(self,spi_clk_mode,spi_clk_freq):
        """ jtag tck freq set
            
            Args:
                spi_clk_mode(int): 0~3 ==> SPI MODE 0~3
                spi_clk_freq(int): 2000~62500000 Hz

            Returns:
                None
        """
        # spi_mode_reg addr: 0x10--bit4 CPHA;0x10--bit5 CPOL;
        #           Mode 0: CPOL=0,CPHA=0; Mode 1: CPOL=0,CPHA=1;Mode 2: CPOL=1,CPHA=0; Mode 3: CPOL=1,CPHA=1
        # spi_clk_freq_reg addr: 0x20~0x21
        # set spi clk mode reg
        rd_data = self.__axi4lite.read(0x10, 1)
        rd_data[0] = (rd_data[0] & 0xCF) | ((spi_clk_mode&0x03)<<4)
        self.__axi4lite.write(0x10,rd_data, 1)
        # set spi clk freq reg
        rd_data = self.__axi4lite.read(0x01, 3)
        base_clk_freq = self.__data_deal.list_2_int(rd_data)
        freq_div = int(((base_clk_freq*1000)/(spi_clk_freq*2))-2)
        if(freq_div<0):
            freq_div = 0
        wr_data = self.__data_deal.int_2_list(freq_div,2)
        self.__axi4lite.write(0x20,wr_data,2)
        return None

    def spi_normal_fifo_clr(self):
        """ spi_normal_fifo_clr, clear spi normal fifo data.
            
            Args:
                None

            Returns:
                None
        """
        # fifo clr addr: 0x12--bit0
        self.__axi4lite.write(0x12, [0x01], 1)
        return None
        
    def spi_dma_fifo_clr(self):
        """ spi_dma_fifo_clr, Reserved function, Don't use it temporarily.
            
            Args:
                None

            Returns:
                None
        """
        # fifo clr addr: 0x12--bit1
        self.__axi4lite.write(0x12, [0x02], 1)
        return None
        
    def spi_cs_ctrl(self,cs_ch,level):
        """ spi_cs_ctrl
            
            Args:
                cs_ch(int): 0~7 -- cs channel
                level(string): 'L' or 'H' ~~ 'L'--low level,'H'~high level

            Returns:
                None
        """
        # cs reg addr: 0x13,bit0~bit7 ==> cs0~cs7
        rd_data = self.__axi4lite.read(0x13, 1)
        if level == 'L':
            rd_data[0] = rd_data[0] & (~(0x01<<cs_ch))
        else:
            rd_data[0] = rd_data[0] | (0x01<<cs_ch)
        self.__axi4lite.write(0x13, rd_data, 1)
        read_data = self.__axi4lite.read(0x13, 1)
        print("CS_CFG_DATA:",read_data)
        return None
        
    def spi_extend_io_ctrl(self,ext_io_ch,level):
        """ spi_extend_io_ctrl
            
            Args:
                ext_io_ch(int): 0~7 -- ext_io channel
                level(string): 'L' or 'H' ~~ 'L'--low level,'H'~high level

            Returns:
                None
        """
        # extend_io reg addr: 0x15,bit0~bit7 ==> ext_io0~ext_io7
        rd_data = self.__axi4lite.read(0x15, 1)
        if level == 'L':
            rd_data[0] = rd_data[0] & (~(0x01<<ext_io_ch))
        else:
            rd_data[0] = rd_data[0] | (0x01<<ext_io_ch)
        self.__axi4lite.write(0x15, rd_data, 1)
        return None
    
    def spi_arbitrary_n_clk(self,clk_cycle_num):
        """ spi_arbitrary_n_clk
            
            Args:
                clk_cycle_num(int): 1~8
                level(string): 'L' or 'H' ~~ 'L'--low level,'H'~high level

            Returns:
                None
        """
        # n clk & spi operate mode addr: 0x16
        # [0]--arbitrary_n_clk enable bit, [3:1]--clk_cycle_num
        rd_data = self.__axi4lite.read(0x16, 1)
        rd_data[0] = (rd_data[0]&0xF0) | (0x01|((clk_cycle_num-1)<<1))
        self.__axi4lite.write(0x16, rd_data, 1)
        return None
    
    def spi_normal_write(self,wr_data):
        """ spi_normal_write
            
            Args:
                wr_data(list): spi write data list(byte), len 1~2048

            Returns:
                True | False
        """
        # wr data addr: 0x80
        # spi_ctrl addr: 0x16_bit4--spi operate mode sel, 0--normal operate mdoe,1--dma operate mode
        # spi_ctrl addr: 0x16_bit5--varify mode en bit, 0--enable,1--disable         
        # config to spi normal operate mode 
        self.__axi4lite.write(0x16, [0x00], 1)
        # wr data to normal wr_fifo
        # self.__axi4lite.write_byte_array(0x80, wr_data, len(wr_data), 8)
        self.__axi4lite.write_array(0x80, wr_data, len(wr_data), 8) 
        # spi tran start
        self.__axi4lite.write(0x11,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100000:
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100000):
            return False
        # spi fifo clr
        self.spi_normal_fifo_clr()
        return True

    def spi_normal_read(self,read_len):
        """ spi_normal_read
            
            Args:
                read_len(int): 1~2048

            Returns:
                spi_read_data(list): spi read data list(byte), len 1~2048
        """
        # rd data addr:0x80
        # spi_ctrl addr: 0x16_bit4--spi operate mode sel, 0--normal operate mdoe,1--dma operate mode
        # spi_ctrl addr: 0x16_bit5--varify mode en bit, 0--enable,1--disable  
        # config to spi normal operate mode 
        self.__axi4lite.write(0x16, [0x00], 1)
        # wr data to normal wr_fifo, invalid data
        wr_data = []
        for i in range(read_len):
            wr_data.append(0xAA)
            # wr_data.append([0xAA])
        # self.__axi4lite.write_byte_array(0x80, wr_data, read_len, 8)
        self.__axi4lite.write_array(0x80, wr_data, read_len, 8) 
        # spi tran start
        self.__axi4lite.write(0x11,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100000:
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100000):
            return False
        # spi rd data ==> rd data addr:0x80
        # spi_read_data = self.__axi4lite.read_byte_array(0x80, read_len, 8)
        spi_read_data = self.__axi4lite.read_array(0x80, read_len, 8)
        return spi_read_data

    def spi_normal_write_read(self,wr_data):
        """ spi_normal_write_read
            
            Args:
                wr_data(list): spi write data list(byte), len 1~2048

            Returns:
                spi_read_data(list): spi read data list(byte), len 1~2048
        """
        # rd data addr:0x80
        # spi_ctrl addr: 0x16_bit4--spi operate mode sel, 0--normal operate mdoe,1--dma operate mode
        # spi_ctrl addr: 0x16_bit5--varify mode en bit, 0--enable,1--disable  
        # config to spi normal operate mode 
        self.__axi4lite.write(0x16, [0x00], 1)
        # wr data to normal wr_fifo
        # self.__axi4lite.write_byte_array(0x80, wr_data, len(wr_data), 8)
        self.__axi4lite.write_array(0x80, wr_data, len(wr_data), 8) 
        # spi tran start
        self.__axi4lite.write(0x11,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100000:
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100000):
            return False
        # spi rd data ==> rd data addr:0x80
        # spi_read_data = self.__axi4lite.read_byte_array(0x80, len(wr_data), 8)
        spi_read_data = self.__axi4lite.read_array(0x80, len(wr_data), 8)
        return spi_read_data

    def spi_dma_write(self,write_len):
        """ spi_dma_write,Reserved function, Don't use it temporarily.
            
            Args:
                write_len(int): 1~256

            Returns:
                True | False
        """
        # write_len: 1~256
        # operate len addr: 0x24
        # spi_ctrl addr: 0x16_bit4--spi operate mode sel, 0--normal operate mdoe,1--dma operate mode
        # spi_ctrl addr: 0x16_bit5--varify mode en bit, 0--enable,1--disable  
        # config to spi dma operate mode 
        self.__axi4lite.write(0x16, [0x10], 1)
        # config dma mode operate len
        self.__axi4lite.write(0x24, [(write_len-1)], 1)
        # spi tran start
        self.__axi4lite.write(0x11,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100000:
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100000):
            return False
        return True

    def spi_dma_varify(self,varify_len):
        """ spi_dma_write,Reserved function, Don't use it temporarily.
            
            Args:
                varify_len(int): 1~256

            Returns:
                True | False
        """
        # operate len addr: 0x24
        # spi_ctrl addr: 0x16_bit4--spi operate mode sel, 0--normal operate mdoe,1--dma operate mode
        # spi_ctrl addr: 0x16_bit5--varify mode en bit, 0--enable,1--disable  
        # config to spi dma operate mode and enable varify mode
        self.__axi4lite.write(0x16, [0x30], 1)
        # config dma mode operate len
        self.__axi4lite.write(0x24, [varify_len-1], 1)
        # spi tran start
        self.__axi4lite.write(0x11,[0x01],1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x14,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100000:
            rd_data = self.__axi4lite.read(0x14,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100000):
            return False
        if((rd_data[0] & 0x02) == 0x02):
            return False
        return True
