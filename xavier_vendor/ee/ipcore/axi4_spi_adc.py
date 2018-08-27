from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4SpiAdc(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4_clk_frequency = 125000000
        self.__axi4lite=Axi4lite(self.name,self.reg_num) 
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))             
        self.__data_deal = DataOperate()
           
    def enable(self):
        """enable function"""          
        self.__axi4lite.write(0x10, [0x00], 1)
        self.__axi4lite.write(0x10, [0x01], 1)
        return None
        
    def disable(self):
        """disable function"""         
        self.__axi4lite.write(0x10, [0x00], 1)
        return None
        
    def sample_rate_set(self,sample_rate): 
        """ set adc sample rate
            
            Args:
                sample_rate(int): ADC sample rate, unit is SPS

            Returns:
                None
        """                     
        freq_hz_ctrl = int(sample_rate*pow(2,32)/self.__axi4_clk_frequency)  
        wr_data = self.__data_deal.int_2_list(freq_hz_ctrl, 4)
        self.__axi4lite.write(0x20, wr_data, len(wr_data)) 
        return None
    
    def sample_data_get(self):
        """ get sample data
            
            Args:
                None

            Returns:
                sample_volt(float): normalize volt (-1~+1)
        """           
        rd_data = self.__axi4lite.read(0x24,4)
        sample_data = self.__data_deal.list_2_int(rd_data)
        sample_volt = sample_data/pow(2,31)
        return sample_volt
        
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