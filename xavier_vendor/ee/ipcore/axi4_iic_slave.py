from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4I2cSlave(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4_clk_frequency = 125000000
        self.__axi4lite=Axi4lite(self.name,self.reg_num) 
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        self.__data_width = 4

    def enable(self):
        """enable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
    
    def disable(self):
        """disable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        return None
          
    def config(self,bit_rate_hz = 400000,slave_address = 0x48,address_bytes=1,data_bytes=1):   
        """ config ii2 slave
            
            Args:
                bit_rate_hz(int): iic bus bit rate, unit is Hz
                slave_address(int): iic slave device address
                address_bytes(int): iic register addresss bytes 
                data_bytes(int): iic register data bytes
            Returns:
                None
        """       
        self.disable()          
        bit_clk_count = self.__axi4_clk_frequency/bit_rate_hz
        bit_clk_delay = int(bit_clk_count/8)
        byte_ctrl = address_bytes * 16 +data_bytes
        wr_data = [slave_address,byte_ctrl]
        bit_clk_delay_temp = self.__data_deal.int_2_list(bit_clk_delay, 2)
        wr_data.extend(bit_clk_delay_temp)
        self.__axi4lite.write(0x30, wr_data, len(wr_data))
        self.__data_width = data_bytes;
        self.enable()
        return None
     
    def register_read(self,address,read_length):
        read_data = []
        for i in range(0,read_length):
            wr_data = self.__data_deal.int_2_list(address, 2)
            self.__axi4lite.write(0x38, wr_data, len(wr_data))
            rd_data = self.__axi4lite.read(0x3C,4)
            read_data_temp = self.__data_deal.list_2_int(rd_data)
            if(read_data_temp < 0):
                read_data_temp = read_data_temp + pow(2,32)
            read_data_temp = read_data_temp >> 8*(4-self.__data_width)
            read_data.append(read_data_temp)
            address = address + 1
        return read_data
        
    def register_write(self,address,write_data):
        for i in range(0,len(write_data)):
            write_data_temp = write_data[i] << 8*(4-self.__data_width)
            wr_data = self.__data_deal.int_2_list(write_data_temp, 4)
            self.__axi4lite.write(0x34, wr_data, len(wr_data))
            wr_data = self.__data_deal.int_2_list(address, 2)
            self.__axi4lite.write(0x38, wr_data, len(wr_data))
            self.__axi4lite.write(0x3A, [0x01], 1)
            address = address + 1
        return None
    
    def _axi4_clk_frequency_set(self,clk_frequency):
        self.__axi4_clk_frequency = clk_frequency
    
      