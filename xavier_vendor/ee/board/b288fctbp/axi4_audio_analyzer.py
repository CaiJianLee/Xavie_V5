from __future__ import division
import math
from time import sleep
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.1'

class Axi4AudioAnalyzer(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 65536
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))  
        self.__data_deal = DataOperate() 
        self.__k1_index = 0
        self.__k1_data = 0
        self.__k2_index =0
        self.__k2_data = 0
        self.__decimation_data = 1
        self.__base_frequency = 1000

    def enable(self):
        """enable function"""
        self.disable()
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] | 0x01;
        self.__axi4lite.write(0x10, rd_data,1)
        return None
        
    def disable(self):
        """disable function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] & 0xFE;
        self.__axi4lite.write(0x10, rd_data,1)
        return None

    def upload_enable(self):
        """enable data upload function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] | 0x02;
        self.__axi4lite.write(0x10, rd_data,1)
        return None
        
    def upload_disable(self):
        """disbale data upload function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] & 0xFD;
        self.__axi4lite.write(0x10, rd_data,1)
        return None

    def measure_paramter_set(self,bandwidth_hz,sample_rate,decimation_type,signal_source):
        """ Set measure paramter
            
            Args:
                bandwidth_hz(int): Bandwidth limit, unit is Hz
                sample_rate(int): signal sample rate, unit is Hz
                decimation_type(str): signal decimation type 
                                      'auto' -- automatic detection
                                      '1'/'2'/........
                signal_source(str): 'IIS'/'PDM'/'SPDIF'
            Returns:
                False | True
        """             
        wr_data = self.__data_deal.int_2_list(int(sample_rate/1000),3)
        self.__axi4lite.write(0xF0,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x16,1)      
        freq_resolution = sample_rate/(8192*rd_data[0])
        bandwidth_index = int(bandwidth_hz/freq_resolution)
        if(signal_source == 'IIS'):
            source_data = 0x10
        elif(signal_source == 'SPDIF'):
            source_data = 0x20
        elif(signal_source == 'PDM'):
            source_data = 0x30
        else:
            logger.error('@%s: Signal Source Error'%(self.name))
            return False
        wr_data = self.__data_deal.int_2_list(bandwidth_index,2)
        wr_data[1] = (wr_data[1] & 0x0F ) | source_data
        self.__axi4lite.write(0x11,wr_data,len(wr_data))
        self._decimation_factor_set(decimation_type)
        return True
        
    def measure_start(self):
        """ start measure    
            Args:
                None
            Returns:
                False | True
        """         
        self.__axi4lite.write(0x14, [0x00],1)
        self.__axi4lite.write(0x13, [0x01],1)
        rd_data = [0]
        timeout_cnt = 0
        while (rd_data[0] == 0x00) and timeout_cnt < 3000:
            sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1) 
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 3000):
            logger.error('@%s: wait time out'%(self.name))
            return False    
        self._base_index_find()
        return True


    def _decimation_factor_set(self,decimation_type): 
        if(decimation_type is 'auto'):
            decimation_type_data = 0xFF
        else:
            decimation_type_data = int(decimation_type)
        self.__axi4lite.write(0x15, [decimation_type_data],1)
        self.__axi4lite.write(0x17, [0x01],1)
        rd_data = [0];
        timeout_cnt = 0;
        while (rd_data[0] == 0x00) and timeout_cnt < 3000:
            sleep(0.001)
            rd_data = self.__axi4lite.read(0x17,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 3000):
            logger.error('@%s: wait time out'%(self.name))
            return False
        rd_data = self.__axi4lite.read(0x16,1)
        self.__decimation_data = rd_data[0]
        return True         
    
    def _max_index_find(self):
        rd_data = self.__axi4lite.read(0x20,4)    
        max_index = self.__data_deal.list_2_int(rd_data)
        rd_addr = 32768 + max_index*8
        rd_data = self.__axi4lite.read(rd_addr, 8)
        max_data = self.__data_deal.list_2_int(rd_data)
        return (max_index,max_data)

    def _base_index_find(self):
        (max_index,max_data) = self._max_index_find()
        max_left_index = max_index -1;
        max_right_index = max_index + 1;
        
        rd_addr = 32768 + max_left_index*8
        rd_data = self.__axi4lite.read(rd_addr, 8)
        max_left_data = self.__data_deal.list_2_int(rd_data)
        rd_addr = 32768 + max_right_index*8
        rd_data = self.__axi4lite.read(rd_addr, 8)
        max_right_data = self.__data_deal.list_2_int(rd_data)      
        if(max_left_data > max_right_data):
            second_index = max_left_index
            second_data = max_left_data
        else:
            second_index = max_right_index
            second_data = max_right_data
        
        if(max_index > second_index):
            self.__k1_index = second_index
            self.__k1_data = second_data
            self.__k2_index = max_index
            self.__k2_data = max_data
        else:
            self.__k2_index = second_index
            self.__k2_data = second_data
            self.__k1_index = max_index
            self.__k1_data = max_data
        return None
                   
    def _get_fft_data(self,data_cnt):
        fft_data = []
        for i in range (0,data_cnt):
            rd_addr = 32768 + i*8
            rd_data = self.__axi4lite.read(rd_addr, 8)
            rd_data_int = self.__data_deal.list_2_int(rd_data)
            fft_data.append(rd_data_int)
        return fft_data
             
    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('@%s: Test Register read data error. '%(self.name))
            return False
        return None

            