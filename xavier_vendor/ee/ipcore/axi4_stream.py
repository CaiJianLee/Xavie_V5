from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.1.0'

class Axi4L2S:
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))        
        self.__data_deal = DataOperate()
        rd_data = self.__axi4lite.read(0x0C, 2)    
        self.__tx_width = rd_data[0]
        self.__rx_width = rd_data[1]
            
    def write(self,write_data):
        """ write access
            
            Args:
                write_data(bytes): write data bytes
            Returns:
                NONE
        """         
        rd_data = self.__axi4lite.read(0x0C,1)
        bits_width = rd_data[0]
        if(len(write_data)%4 > 0):
            logger.error('%s: write data length error'%(self.name)) 
            return False
        i = int(len(write_data)/bits_width)
        wr_data_index = 0
        while(i > 0):
            rd_data = self.__axi4lite.read(0x10,2)
            cache_deep = self.__data_deal.list_2_int(rd_data)
            if(cache_deep > i):
                send_cnt = i
            else:
                send_cnt = cache_deep -3
            send_byte_cnt = send_cnt*bits_width
            #self.__axi4lite.write_byte_array(0x14, write_data[wr_data_index:wr_data_index+send_byte_cnt], send_byte_cnt, bits_width*8)
            self.__axi4lite.write_array(0x14, write_data[wr_data_index:wr_data_index+send_byte_cnt], send_byte_cnt, bits_width*8)
            wr_data_index += send_byte_cnt
            i -= send_cnt
        return None
    
    def read(self):
        """ read access
            
            Args:
                NONE
            Returns:
                read_data(bytes): read data bytes
        """      
        rd_data = self.__axi4lite.read(0x0D,1)
        bits_width = rd_data[0]   
        rd_data = self.__axi4lite.read(0x12, 2)
        cache_deep = self.__data_deal.list_2_int(rd_data)
        read_data = []
        if cache_deep != 0:
            read_data = self.__axi4lite.read_byte_array(0x18, cache_deep*bits_width, bits_width*8)
            return read_data
        else:
            return None   
			
			
	

	def cache_deep(self):
		"""cache_deep"""
		cache_data = self.__axi4lite.read(0x12, 2)
		if cache_data != 0:
			return False	
		else:
			return True   
 
			
			
		