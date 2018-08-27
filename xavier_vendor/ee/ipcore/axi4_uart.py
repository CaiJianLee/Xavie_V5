from __future__ import division
from time import sleep
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.1'

class Axi4Uart(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)    
        self.__axi4_clk_frequency = 125000000
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        rd_data = self.__axi4lite.read(0x0C,2)
        self._tx_cache = self.__data_deal.list_2_int(rd_data)
           
    def enable(self):
        """  Enable function        """  
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
    
    def disable(self):
        """  Disable function        """   
        self.__axi4lite.write(0x10, [0x00], 1)
        return None
    
    def config(self,baud_rate=115200,data_bits=8,parity_type='NONE',stop_bits=1, time_insert='NONE'):
        """ Set uart bus parameter
            
            Args:
                baud_rate(int)   : UART baud rate
                data_bits(int)   : Data width 5/6/7/8
                parity_type(str) : parity type. "ODD"/"EVNE"/"NONE"
                stop_bits(float) : stop bit width. 1/1.5/2
                time_insert(str) : Insert timestamp Control, "TS"/"NONE"
            Returns:
                None
        """         
        logger.info("%s set baud_rate: %s ; data_bits: %s; stop_bits : %s ;parity: %s; time_insert: %s;"\
                     %(self.name, baud_rate, data_bits,stop_bits,parity_type,time_insert))
        baud_rate_temp = int(pow(2,32)*baud_rate/self.__axi4_clk_frequency)
        wr_data = self.__data_deal.int_2_list(baud_rate_temp, 4)
        self.__axi4lite.write(0x20, wr_data, len(wr_data))
        if(parity_type == 'ODD'):
            parity_data = 0x01
        elif(parity_type == 'EVNE'):
            parity_data = 0x00
        else:
            parity_data = 0x02
        if(stop_bits == 1):
            stop_bits_data = 0x04
        elif(stop_bits == 1.5):
            stop_bits_data = 0x08
        else:
            stop_bits_data = 0x0C
        data_bits_data = (data_bits-1)<<4
        wr_data_temp = parity_data | stop_bits_data | data_bits_data
        self.__axi4lite.write(0x24, [wr_data_temp], 1)
        if(time_insert == "TS"):
            self.__axi4lite.write(0x25, [0x01], 1)
        else:
            self.__axi4lite.write(0x25, [0x00], 1)
        self.__axi4lite.write(0x26, [0x11], 1)
        return None
    
    def write(self,wr_data,block='non-block'):
        """ uart write access
            
            Args:
                write_data(bytes): uart send bytearray
            Returns:
                NONE
        """         
        i = len(wr_data)
        wr_data_index = 0
        while(i > 0):
            rd_data = self.__axi4lite.read(0x35,2)
            cache_deep = self.__data_deal.list_2_int(rd_data)
            if(cache_deep > i):
                send_cnt = i
            else:
                send_cnt = cache_deep -3
            self.__axi4lite.write_byte_array(0x34, wr_data[wr_data_index:wr_data_index+send_cnt], send_cnt, 8)
            wr_data_index += send_cnt
            i -= send_cnt
        if block is 'block':
            i = 0
            while( i < self._tx_cache):
                rd_data = self.__axi4lite.read(0x35,2)
                cache_deep = self.__data_deal.list_2_int(rd_data)
                sleep(10)              
        return None
        
    def read(self):
        """ uart read access
            
            Args:
                NONE
            Returns:
                receive_str(bytes): uart receive bytearray
        """         
        rd_data = self.__axi4lite.read(0x31, 2)
        cache_deep = self.__data_deal.list_2_int(rd_data)
        if cache_deep != 0:
            rd_data = self.__axi4lite.read_byte_array(0x30, cache_deep, 8)
            return rd_data
        else:
            return None    
        