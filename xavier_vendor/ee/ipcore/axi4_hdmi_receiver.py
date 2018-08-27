from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4HdmiRreceiver(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4_clk_frequency = 125000000
        self.__axi4lite=Axi4lite(self.name,self.reg_num) 
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        self.__data_width = 4

    def disable(self):
        """disable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        return None
          
    def enable(self):
        """enable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
    
    def initialize(self):   
        """ initialize the edid of hdmi receiver ddc.
            
            Args:
                None
            Returns:
                None
        """       
        self.disable()     
        # config ddc port paramer------------------------------------------
        # bit_rate_hz = 100000
        bit_clk_count = self.__axi4_clk_frequency/100000
        bit_clk_delay = int(bit_clk_count/4)
        # byte_ctrl = address_bytes * 16 +data_bytes
        byte_ctrl = 1*16 + 1 
        self.__data_width = 1;
        # slave_address = 0x50
        wr_data = [0x50,byte_ctrl]
        bit_clk_delay_temp = self.__data_deal.int_2_list(bit_clk_delay, 2)
        wr_data.extend(bit_clk_delay_temp)
        self.__axi4lite.write(0x30, wr_data, len(wr_data))
        # config edid data------------------------------------------------
        edid_720p_data = [0x00,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x00,0x10,0xEC,0x02,0x00,0x00,0x00,0x00,0x00
                        ,0x02,0x1A,0x01,0x03,0xA1,0x33,0x1D,0x78,0x0A,0xEC,0x18,0xA3,0x54,0x46,0x98,0x25
                        ,0x0F,0x48,0x4C,0x21,0x08,0x00,0xB3,0x00,0xD1,0xC0,0x81,0x80,0x81,0xC0,0xA9,0xC0
                        ,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x1D,0x00,0x72,0x51,0xD0,0x1E,0x20,0x6E,0x28
                        ,0x55,0x00,0x00,0xD0,0x52,0x00,0x00,0x1E,0x00,0x00,0x00,0xFC,0x20,0x44,0x69,0x67
                        ,0x69,0x6C,0x65,0x6E,0x74,0x44,0x56,0x49,0x2D,0x32,0x00,0x00,0x00,0x10,0x00,0x00
                        ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x10
                        ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xEE]
        self._register_write(0,edid_720p_data)
        self.enable()
        return None
     
    def _register_read(self,address,read_length):
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
        
    def _register_write(self,address,write_data):
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
    
      