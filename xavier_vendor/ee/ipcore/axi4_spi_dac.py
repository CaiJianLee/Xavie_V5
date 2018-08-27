from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4SpiDac(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4_clk_frequency = 125000000
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))    
        self.__data_deal = DataOperate()
        self.__sclk_frequency = 10000000
        
    def enable(self):
        """enable function"""        
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
        
    def disable(self):
        """disable function"""        
        self.__axi4lite.write(0x10, [0x00], 1)
        return None

    def dac_mode_set(self,dac_mode):
        """ set dac mode data
            
            Args:
                dac_mode(int): dac mode data

            Returns:
                None
        """           
        wr_data = [dac_mode]
        self.__axi4lite.write(0x11, wr_data, len(wr_data))
        return None
    
    def spi_sclk_frequency_set(self,sclk_freq_hz):
        """ set spi bus sclk frequency
            
            Args:
                sclk_freq_hz(int): spi bus sclk frequency, unit is Hz

            Returns:
                None
        """                   
        self.__sclk_frequency = sclk_freq_hz
        freq_hz_ctrl = int(sclk_freq_hz*pow(2,32)/self.__axi4_clk_frequency)
        wr_data = self.__data_deal.int_2_list(freq_hz_ctrl, 4)
        self.__axi4lite.write(0x24, wr_data, len(wr_data))
        return None
        
    def sample_rate_set(self,sample_rate): 
        """ set dac sample rate
            
            Args:
                sample_rate(int): DAC sample rate, unit is SPS

            Returns:
                None
        """             
        freq_hz_ctrl = int(sample_rate*pow(2,32)/self.__sclk_frequency)  
        wr_data = self.__data_deal.int_2_list(freq_hz_ctrl, 4)
        self.__axi4lite.write(0x20, wr_data, len(wr_data)) 
        return None
        
    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('@%s: Test Register read data error. '%(self.name))
            return False
        return None
    
    def _set_axi4_clk_frequency(self,clk_frequency):
        self.__axi4_clk_frequency = clk_frequency
        return None        