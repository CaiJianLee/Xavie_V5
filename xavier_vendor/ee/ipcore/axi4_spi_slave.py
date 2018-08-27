from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4SpiSlave(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))    
        self.__axi4_clk_frequency = 125000000
        self.__data_deal = DataOperate()
        self.__data_width = 4
    def disable(self):
        """  Disable function        """    
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data], 1)
        return None    

    def enable(self):
        """  Enable function        """  
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data], 1)
        wr_data = rd_data[0] & 0xF0 | 0x01
        self.__axi4lite.write(0x10, [wr_data], 1)
        return None
               
    def config(self,spi_clk_cpha_cpol = 'Mode_0',spi_byte_cfg = '1'):
        """ Set spi bus parameter
            
            Args:
                spi_byte_cfg(str): '1'    --spi slave receive data or send data is 1byte
                                   '2'    --spi slave receive data or send data is 2byte
                                   '3'    --spi slave receive data or send data is 3byte
                                   '4'    --spi slave receive data or send data is 4byte
                
                spi_clk_cpha_cpol(str): 'Mode_0' --CPHA=0, CPOL=0,  when CS is high, the SCLK is low,  first edge sample
                                        'Mode_1' --CPHA=0, CPOL=1,  when CS is high, the SCLK is high, first edge sample
                                        'Mode_2' --CPHA=1, CPOL=0,  when CS is high, the SCLK is low,  second edge sample
                                        'Mode_3' --CPHA=1, CPOL=1,  when CS is high, the SCLK is high, second edge sample
            Returns:
                None
        """ 
        mode_set_data=self.__axi4lite.write(0x11,[0x00],1)
        if(spi_clk_cpha_cpol == 'Mode_0'):
            mode_set_data = 0x00
        elif(spi_clk_cpha_cpol== 'Mode_1'):
            mode_set_data = 0x01
        elif(spi_clk_cpha_cpol== 'Mode_2'):
            mode_set_data = 0x02
        elif(spi_clk_cpha_cpol== 'Mode_3'):
            mode_set_data = 0x03
        else:
            logger.error('@%s: Mode select error'%(self.name))
            return False
        self.__axi4lite.write(0x11, [mode_set_data], 1)
        self.__axi4lite.write(0x12,[0x01],1)
        if(spi_byte_cfg == '1'):
            set_byte = 0x01
        elif(spi_byte_cfg == '2'):
            set_byte = 0x02
        elif(spi_byte_cfg =='3'):
            set_byte = 0x03
        elif(spi_byte_cfg =='4'):
            set_byte = 0x04
        else:
            logger.error('@%s: byte select error'%(self.name))
            return False            
        self.__axi4lite.write(0x12, [set_byte], 1)
        self.__data_width=set_byte
        return None
      
    def register_read(self,address,read_length):
        read_data = []
        for i in range(0,read_length):
            wr_data = self.__data_deal.int_2_list(address, 2)
            self.__axi4lite.write(0x14, wr_data, len(wr_data))
            rd_data = self.__axi4lite.read(0x24,4)
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
            self.__axi4lite.write(0x20, wr_data, len(wr_data))
            wr_data = self.__data_deal.int_2_list(address, 2)
            self.__axi4lite.write(0x14, wr_data, len(wr_data))
            self.__axi4lite.write(0x16, [0x01], 1)
            address = address + 1
        return None
            