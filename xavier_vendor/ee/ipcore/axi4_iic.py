from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.1'

class Axi4I2c(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4_clk_frequency = 125000000
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        self.config()
        rd_data = self.__axi4lite.read(0x12,2)
        self._cache_size = self.__data_deal.list_2_int(rd_data)
        
    def config(self,bit_rate_hz=400000):
        """ config ii2 master
            
            Args:
                bit_rate_hz(int): iic bus bit rate, unit is Hz

            Returns:
                None
        """                
        self.disable()
        bit_rate_ctrl = bit_rate_hz*8*pow(2,32)/self.__axi4_clk_frequency
        wr_data = self.__data_deal.int_2_list(int(bit_rate_ctrl), 4)
        self.__axi4lite.write(0x20, wr_data, len(wr_data))
        self.enable()
        return None

    def write(self,dev_addr,data):
        """ iis write 
            
            Args:
                dev_addr(int): iic slave address
                data(list): iic write data, length < 65

            Returns:
                False | True
        """          
        op_code = dev_addr * 2;
        send_data = [op_code] + data;
        send_list = []
        for i in range(0,len(send_data)):
            send_list.append(send_data[i])
            if i == 0:
                send_list.append(0x80)
            elif i == (len(send_data) - 1):
                send_list.append(0x20)
            else:
                send_list.append(0x00)
        receive_list = self._iic_control(send_list)
        if receive_list == False:
            self.enable()
            return False
        i = 0
        while(i < len(receive_list)):
            if(receive_list[i+1] & 0x01 == 0x01):
                logger.error('@%s: receive no ACK'%(self.name)) 
                return False
            i = i+ 2
        return True
       
    def read(self,dev_addr,length):
        """ iis read 
            
            Args:
                dev_addr(int): iic slave address
                length(int): iic read data length, length < 65

            Returns:
                receive_list_out(list): iic read data
                if error, return False
        """                  
        op_code = dev_addr * 2 + 0x01;
        send_list = [op_code,0x80]
        for i in range(0,length):
            send_list.append(0x00)
            if i == (length - 1) :
                send_list.append(0x70)
            else:
                send_list.append(0x40)
        receive_list = self._iic_control(send_list)   
        if receive_list == False:
            self.enable()
            return False
        i = 0
        receive_list_out = []
        while i < len(receive_list):
            receive_list_out.append(receive_list[i])
            if(i != len(receive_list)-2):
                if (receive_list[i+1] & 0x01) == 0x01:
                    logger.error('@%s: receive no ACK'%(self.name)) 
                    return False
            i = i+2
        i = 0
        while i  >= 0:
            del receive_list_out[i]
            i = i-1
        return receive_list_out        
    
    def rdwr(self,dev_addr,write_data_list,read_length):
        """ iis write and read
            
            Args:
                dev_addr(int): iic slave address
                write_data_list(list): iic write data, length < 65
                read_length(int): iic read data length, length < 65
                the length of write_data_list + read_length < 65
            Returns:
                receive_list_out(list): iic read data
                if error, return False
        """             
        op_code = dev_addr * 2;
        send_data = [op_code] + write_data_list;
        send_list=[]
        for i in range(0,len(send_data)):
            send_list.append(send_data[i])
            if i == 0:
                send_list.append(0x80)
            else:
                send_list.append(0x00)
        op_code = dev_addr * 2 + 0x1
        send_list.append(op_code)   
        send_list.append(0x80)
        for i in range(0,read_length):
            send_list.append(0x00)
            if i == (read_length - 1) :
                send_list.append(0x70)
            else:
                send_list.append(0x40)   
        receive_list = self._iic_control(send_list)  
        if receive_list == False:
            self.enable()
            return False 
        i = 0
        receive_list_out = []
        while i < len(receive_list)-1 :
            receive_list_out.append(receive_list[i])
            if(i != len(receive_list)-2 ):
                if (receive_list[i+1] & 0x01) == 0x01:
                    logger.error('@%s: receive no ACK'%(self.name)) 
                    return False
            i = i+2
        i = 1+len(write_data_list)
        while i  >= 0:
            del receive_list_out[i]
            i = i-1
        return receive_list_out     
                     
    def _iic_control(self,send_list):
        time_out = 0
        send_cache_depth = self.__axi4lite.read(0x1C,1)
        if(send_cache_depth[0] >0):
            logger.error('@%s: send cache not empty'%(self.name))
            return False
        recieve_cache_depth = self.__axi4lite.read(0x1E,1)
        if(recieve_cache_depth[0] > 0):
            logger.error('@%s: receive cache not empty'%(self.name))
            return False
        if(len(send_list) > self._cache_size*2):
            logger.error('@%s: send data too much'%(self.name))
            return False
        self.__axi4lite.write_array(0x14, send_list, len(send_list), 16)      
        while time_out <3000:
            recieve_cache_depth = self.__axi4lite.read(0x1E,1)
            if recieve_cache_depth[0] == (len(send_list))/2:
                break
            else:
                time_out = time_out + 1
                time.sleep(0.001)
        if time_out == 3000:
            logger.error('@%s: receive data enough'%(self.name)) 
            return False          
        receive_bytes_cnt = 2*recieve_cache_depth[0]
        receive_list = self.__axi4lite.read_array(0x18, receive_bytes_cnt, 16)
        return receive_list
            
        
    def _axi4_clk_frequency_set(self,clk_frequency):
        self.__axi4_clk_frequency = clk_frequency
         
    def enable(self):
        """enable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
    
    def disable(self):
        """disable function"""
        self.__axi4lite.write(0x10, [0x00], 1)
        return None