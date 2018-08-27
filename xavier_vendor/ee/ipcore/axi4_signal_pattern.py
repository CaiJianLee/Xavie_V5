from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate
import time
import os

__version__ = '1.0.0'

class Axi4SignalPattern(object):
    
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
    
    def config_calibration(self,gain,offset):
        """  config calibration
        
            Args:
                gain(float): 0~1.9999, Linear calibration gain parameter, 
                offset(float): -0.9999~0.9999, the ratio of the output range
                               Linear calibration offset parameter
            
            Returns:
                None
        """      
        wr_data = self.__data_deal.int_2_list(int(gain*pow(2,17)),3)
        self.__axi4lite.write(0x20,wr_data,len(wr_data))
        wr_data = self.__data_deal.int_2_list(int(-offset*pow(2,17)),3)
        self.__axi4lite.write(0x24,wr_data,len(wr_data))
        return None
        
    def pattern_output_enable(self,pattern_len,delay_time,timeout=10000):
        """  pattern signal output enable
        
            Args:
                pattern_len(int): pattern data length
                delay_time(int): 0~500us, After the signal is triggered, the delay time of the output pattern signal.

            Returns:
                None
        """      
        self.enable()
        wr_data = self.__data_deal.int_2_list(int(pattern_len),4)
        self.__axi4lite.write(0x30,wr_data,len(wr_data))
        wr_data = self.__data_deal.int_2_list(int(delay_time*1000/8),2)
        self.__axi4lite.write(0x34,wr_data,len(wr_data))
        # detect start and wait triggered
        self.__axi4lite.write(0x11,[0x01],1)
        return None
    
    def pattern_output_state(self,timeout=10000):
        """  query pattern signal output state
        
            Args:
                timeout(int): ms, Timeout waiting for the trigger signal.

            Returns:
                True | False
        """
        # query state
        timeout_cnt = 0
        rd_data = self.__axi4lite.read(0x13,1)
        while (rd_data[0] != 0x01) and (timeout_cnt < (timeout + 1000)):
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x13,1)
            timeout_cnt = timeout_cnt + 1
        
        # read pattern count
        # time.sleep(0.100)
        # rd_data = self.__axi4lite.read(0x30,4)
        # print("pattern len:", rd_data)
        # rd_data = self.__axi4lite.read(0x3C,4)
        # print("pattern cnt:", rd_data)
        # if(rd_data != [0, 80, 8, 0]):
        #     exit(0)
        
        if(timeout_cnt == (timeout + 1000)): 
            logger.error('@%s: Measure time out'%(self.name))
            return False
        return True
    
      