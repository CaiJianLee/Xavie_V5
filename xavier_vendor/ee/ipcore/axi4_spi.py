from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.1'

class Axi4Spi(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))    
        self.__axi4_clk_frequency = 125000000
        self.__data_deal = DataOperate()
        self.__cache_size = 0
    
    def enable(self):
        """  Enable function        """  
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data_temp = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data_temp], 1)
        wr_data_temp = rd_data[0] & 0xF0 | 0x01
        self.__axi4lite.write(0x10, [wr_data_temp], 1)
        return None
        
    def disable(self):
        """  Disable function        """    
        rd_data = self.__axi4lite.read(0x10, 1)
        wr_data_temp = rd_data[0] & 0xF0
        self.__axi4lite.write(0x10, [wr_data_temp], 1)
        return None
        
    def config(self,spi_clk_frequency = 500000,spi_clk_type = 'neg',wait_time_us = 1,spi_clk_polarity = 'high',cache_size=64):
        """ Set spi bus parameter
            
            Args:
                spi_clk_frequency(int): spi bus clock frequency, unit is Hz
                spi_clk_type(str): 'pos' --sclk posedge send data, sclk negedge receive data
                                   'neg' --sclk negedge send data, sclk posedge receive data
                wait_time_us(float):    the wait time for new spi access
                spi_clk_polarity(str): 'high' --when CS is high, the SCLK is high
                                       'low' --when CS is high, the SCLK is low
                cache_size(int): data cache depth
            Returns:
                None
        """ 
        rd_data = self.__axi4lite.read(0x10,1);          
        if(spi_clk_type == 'pos'):
            set_data = rd_data[0] | 0x10
        elif(spi_clk_type == 'neg'):
            set_data = rd_data[0] & 0xEF
        else:
            logger.error('@%s: sclk edge select error'%(self.name))
            return False
        if(spi_clk_polarity == 'high'):
            set_data = set_data | 0x20
        elif(spi_clk_polarity == 'low'):
            set_data = set_data & 0xDF
        else:
            logger.error('@%s: sclk polarity select error'%(self.name))
            return False            
        self.__axi4lite.write(0x10, [set_data], 1)
        freq_ctrl = int(spi_clk_frequency * pow(2,32)/self.__axi4_clk_frequency)
        wr_data = self.__data_deal.int_2_list(freq_ctrl, 4)
        self.__axi4lite.write(0x14, wr_data, len(wr_data))
        wait_cnt = int(wait_time_us * self.__axi4_clk_frequency/1000000)
        wr_data = self.__data_deal.int_2_list(wait_cnt, 3)
        self.__axi4lite.write(0x11, wr_data, len(wr_data))
        self.__cache_size = cache_size
        return None
      
    def write(self,write_data,cs_extend = 0):
        """ SPI write access
            
            Args:
                write_data(list): write data list
                cs_extend(float): The extend CS low when SPI access over, cs_extend is 0 to 8, min resolution is 0.5
            Returns:
                False | True
        """           
        send_cache_depth = self.__axi4lite.read(0x28,1)
        last_append = (int(cs_extend)*16 + 5)
        if(cs_extend > int(cs_extend)):
        	last_append = last_append + 8
        if(self.__cache_size < (send_cache_depth[0] + len(write_data))):
            logger.error('@%s: send cache not enough')
            return False       
        write_data_temp = []
        for i in range(0,len(write_data)):
            write_data_temp.append(write_data[i])
            if(i == (len(write_data)-1)):
                write_data_temp.append(last_append)
            else:
                write_data_temp.append(0x04)
        self.__axi4lite.write_array(0x20, write_data_temp, len(write_data_temp), 16)
        return True
    
    def read(self,read_length,cs_extend = 0):    
        """ SPI read access
            
            Args:
                read_length(int): number of read data
                cs_extend(float): The extend CS low when SPI access over, cs_extend is 0 to 8, min resolution is 0.5
            Returns:
                receive_data(list): read data list
                if error ,return False
        """    
        send_cache_depth = self.__axi4lite.read(0x28,1)
        last_append = (int(cs_extend)*16 + 3)
       	if(cs_extend > int(cs_extend)):
        	last_append = last_append + 8
        if(send_cache_depth[0] + read_length  > self.__cache_size):
            logger.error('@%s: send cache not enough'%(self.name))
            return False     
        recieve_cache_depth = self.__axi4lite.read(0x29,1)
        if(recieve_cache_depth[0] > 0):
            logger.error('@%s: receive cache not empty'%(self.name))
            receive_data_temp = self.__axi4lite.read_array(0x24, 2*recieve_cache_depth[0], 16)
            return False   
        tx_data_temp = []       
        for i in range(0,read_length):
            tx_data_temp.append(0x00)
            if(i == (read_length-1)):
                tx_data_temp.append(last_append)
            else:
                tx_data_temp.append(0x02)    
        self.__axi4lite.write_array(0x20, tx_data_temp, len(tx_data_temp), 16) 
        time_out = 0
        while time_out < 3000 :
            recieve_cache_depth = self.__axi4lite.read(0x29,1)
            if(recieve_cache_depth[0] < read_length):
                time.sleep(0.001)
                time_out = time_out + 1
            else:
                break
        if(time_out == 3000):
            logger.error('@%s: receive data time out'%(self.name))
            return False
        receive_data_temp = self.__axi4lite.read_array(0x24, 2*read_length, 16)
        receive_data = []
        i = 0
        while i < 2*read_length :
            receive_data.append(receive_data_temp[i])
            i = i+2
        return receive_data          
    
    def write_and_read(self,write_data,cs_extend = 0):
        """ SPI write and read access
            
            Args:
                write_data(list): write data list
                cs_extend(float): The extend CS low when SPI access over, cs_extend is 0 to 8, min resolution is 0.5
            Returns:
                receive_data(list): read data list
                if error ,return False
        """                   
        send_cache_depth = self.__axi4lite.read(0x28,1)
        last_append = (int(cs_extend)*16 + 7)
        if(cs_extend > int(cs_extend)):
        	last_append = last_append + 8
        if(send_cache_depth[0] > self.__cache_size):
            logger.error('@%s: send cache not enough'%(self.name))
            return False     
        recieve_cache_depth = self.__axi4lite.read(0x29,1)
        if(recieve_cache_depth[0] > 0):
            logger.error('@%s: receive cache not empty'%(self.name))
            receive_data_temp = self.__axi4lite.read_array(0x24, 2*recieve_cache_depth[0], 16)
            return False      
        tx_data_temp = []             
        for i in range(0,len(write_data)):
            tx_data_temp.append(write_data[i])
            if(i == (len(write_data)-1)):
                tx_data_temp.append(last_append)
            else:
                tx_data_temp.append(0x06)
        self.__axi4lite.write_array(0x20, tx_data_temp, len(tx_data_temp), 16)
        time_out = 0
        while time_out < 3000 :
            recieve_cache_depth = self.__axi4lite.read(0x29,1)
            if(recieve_cache_depth[0] < len(write_data)):
                time.sleep(0.001)
                time_out = time_out + 1
            else:
                break
        if(time_out == 3000):
            logger.error('@%s: receive data time out'%(self.name))
            return False
        receive_data_temp = self.__axi4lite.read_array(0x24, 2*recieve_cache_depth[0], 16)
        receive_data = []
        i = 0
        while i < 2*recieve_cache_depth[0] :
            receive_data.append(receive_data_temp[i])
            i = i+2
        return receive_data          
   
    def write_to_read(self,write_data,read_length,cs_extend = 0):
        """ SPI write to read access
            
            Args:
                write_data(list): write data list
                read_length(int): number of read data
                cs_extend(float): The extend CS low when SPI access over, cs_extend is 0 to 8, min resolution is 0.5
            Returns:
                receive_data(list): read data list
                if error ,return False
        """         
        send_cache_depth = self.__axi4lite.read(0x28,1)
        last_append = (int(cs_extend)*16 + 3)
       	if(cs_extend > int(cs_extend)):
        	last_append = last_append + 8
        if(send_cache_depth[0] + read_length  > self.__cache_size):
            logger.error('@%s: send cache not enough'%(self.name))
            return False     
        recieve_cache_depth = self.__axi4lite.read(0x29,1)
        if(recieve_cache_depth[0] > 0):
            logger.error('@%s: receive cache not empty'%(self.name))
            receive_data_temp = self.__axi4lite.read_array(0x24, 2*recieve_cache_depth[0], 16)
            return False   
        tx_data_temp = []                
        for i in range(0,len(write_data)):
            tx_data_temp.append(write_data[i])
            tx_data_temp.append(0x04)    
        for i in range(0,read_length):
            tx_data_temp.append(0x00)
            if(i == (read_length-1)):
                tx_data_temp.append(last_append) 
            else:
                tx_data_temp.append(0x02) 
        self.__axi4lite.write_array(0x20, tx_data_temp, len(tx_data_temp), 16)
        time_out = 0
        while time_out < 3000 :
            recieve_cache_depth = self.__axi4lite.read(0x29,1)
            if(recieve_cache_depth[0] < read_length):
                time.sleep(0.001)
                time_out = time_out + 1
            else:
                break
        if(time_out == 3000):
            logger.error('@%s: receive data time out'%(self.name))
            return False
        i = 0
        receive_data = []
        receive_data_temp = self.__axi4lite.read_array(0x24, 2*recieve_cache_depth[0], 16)
        while i < 2*read_length :
            receive_data.append(receive_data_temp[i])
            i = i+2
        return receive_data              