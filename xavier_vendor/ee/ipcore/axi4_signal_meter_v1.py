from __future__ import division
import time
import math
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.1.0'

class Axi4SignalMeter(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 1024
        self.__axi4lite=Axi4lite(self.name,self.reg_num)  
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))    
        self.__data_deal = DataOperate() 
        self.__measure_state = 0 
        self.__sample_rate = 125000000
        
    def enable(self):
        """  Enable function        """         
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFE) | 0x00;
        self.__axi4lite.write(0x10, [wr_data],1) 
        wr_data = (rd_data[0] & 0xFE) | 0x01;
        self.__axi4lite.write(0x10, [wr_data],1) 
        return None
        
    def disable(self):
        """  Disable function        """        
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFE) | 0x00;
        self.__axi4lite.write(0x10, [wr_data],1) 
        return None
        
    def amplitude_interval_set(self,test_interval_ms):
        """  when measuring VPP, test_interval_ms is the measured time period for each measuring
        
            Args:
                test_interval_ms(int): the time of measured time period

            Returns:
                None
        """                         
        wr_data = self.__data_deal.int_2_list(test_interval_ms, 2)
        self.__axi4lite.write(0x18, wr_data, len(wr_data))
        return None
        
    def upframe_enable(self,upframe_mode='DEBUG'):
        """  set the parameter of data frame, and enable frame upload function
        
            Args:
                upframe_mode(str): 'BYPASS' is upload data all the time
                                   'DEBUG' is only upload the data within the measure time

            Returns:
                None
        """
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFD) | 0x02;
        if(upframe_mode == 'BYPASS'):
            wr_data = (wr_data & 0xF7) | 0x08;
        elif(upframe_mode == 'DEBUG'):
            wr_data = (wr_data & 0xF7) | 0x00;
        self.__axi4lite.write(0x10, [wr_data],1)
        return None
        
    def upframe_disable(self):
        """  disable frame upload function
        
            Args:
                None
            Returns:
                None
        """             
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFD) | 0x00;
        self.__axi4lite.write(0x10, [wr_data],1)   
        return None
        
    def measure_start(self,time_ms,sample_rate):
        """  start measure access
        
            Args:
                time_ms(int): measure time, unit is ms
                sample_rate(int): data sample rate, unit is SPS
            Returns:
                True | False
        """         
        self.__sample_rate = sample_rate
        wr_data = self.__data_deal.int_2_list(time_ms, 2)
        self.__axi4lite.write(0x11,wr_data,len(wr_data)) 
        self.__axi4lite.write(0x14, [0x00],1)
        self.__axi4lite.write(0x13, [0x01],1) 
        rd_data = self.__axi4lite.read(0x14,1)
        timeout = 0
        while (rd_data[0] != 0x01) and (timeout < (time_ms + 1000)):
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x14,1)
            timeout = timeout + 1
        if(timeout == (time_ms + 1000)): 
            logger.error('@%s: Measure time out'%(self.name))
            self.__measure_state = 0
            return False
        self.__measure_state = 1
        return True

    def frequency_measure(self,measure_type):
        """  get the frequency of input signal
        
            Args:
                measure_type(str): select the method of frequency measurent
                                'HP' is high precision measurement, it can be use when FPGA IP enable the frequency measurent function
                                'LP' is low precision measurement, it can be use when FPGA IP enable the duty measurent function
            Returns:
                freq(float): the frequency of input signal, unit is Hz
        """ 
        if(self.__measure_state == 0):
            return(0,'Hz')
        if(measure_type == 'HP'):
            freq = self._frequency_hp_measure()
        elif(measure_type == 'LP'):
            freq = self._frequency_lp_measure()
        else:   
            logger.error('@%s: Measure type error'%(self.name))
            return False
        return(freq,'Hz')
        
    def duty_measure(self):
        """  get the duty of input signal
        
            Args:
                None
            Returns:
                duty(float): the duty of input signal, unit is %, 1%~99%
        """         
        if(self.__measure_state == 0):
            rd_data = self.__axi4lite.read(0x10,1)
            if(rd_data[0] & 0x04 == 0x04):
                return(100,'%')
            else:
                return(0,'%')   
        rd_data = self.__axi4lite.read(0x50, 8)
        duty_all = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x58, 8)
        duty_high = self.__data_deal.list_2_int(rd_data)
        
        duty = (duty_high/duty_all)*100
        return(duty,'%')      
    
    def amplitude_measure(self):
        """  get the amplitude of input signal
        
            Args:
                None
            Returns:
                amp_data(float): the normalized average amplitude of input signal, unit is V, 0V~2V
                max_data(float): the normalized max level of input signal, unit is V,-1V ~ +1V
                min_data(float): the normalized min level of input signal, unit is V,-1V ~ +1V
        """         
        rd_data = self.__axi4lite.read(0x70, 8)
        amp_max = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x78, 8)
        amp_min = self.__data_deal.list_2_int(rd_data) 
        rd_data = self.__axi4lite.read(0x80, 4)
        amp_cnt = self.__data_deal.list_2_int(rd_data) 
        max_data = amp_max/(amp_cnt*pow(2,15))
        min_data = amp_min/(amp_cnt*pow(2,15))
        amp_data = max_data-min_data
        return (amp_data,'V',max_data,'V',min_data,'V')
        
    def rms_measure(self):
        """  get the RMS of input signal
        
            Args:
                None
            Returns:
                rms_data(float): the normalized rms of input signal, unit is V, 0V~1V
                max_data(float): the normalized average level of input signal, unit is V, -1V~+1V

        """         
        rd_data = self.__axi4lite.read(0x90, 8)
        rms_square_sum = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x98, 8)
        rms_sum = self.__data_deal.list_2_int(rd_data)     
        rd_data = self.__axi4lite.read(0xA0, 4)
        rms_cnt = self.__data_deal.list_2_int(rd_data)
        rms_data = math.sqrt(rms_square_sum/rms_cnt)/pow(2,15)
        avg_data = (rms_sum/rms_cnt)/pow(2,15)
        return (rms_data,'V',avg_data,'V')
        
    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('@%s: Test Register read data error. '%(self.name))
            return False
        return None  
        
    def _frequency_hp_measure(self):
        rd_data = self.__axi4lite.read(0x15,2)
        sys_divide = self.__data_deal.list_2_int(rd_data)
        if(sys_divide == 0):
            sys_divide = 1
        rd_data = self.__axi4lite.read(0x20, 8)
        freq_x_sum = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x28, 8)
        freq_y_sum = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x30, 8)
        freq_xy_sum = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x38, 8)
        freq_xx_sum = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x40, 4)
        freq_N = self.__data_deal.list_2_int(rd_data)   
        k_1  = freq_N*freq_xy_sum - freq_y_sum * freq_x_sum
        k_2  = freq_N*freq_xx_sum - freq_x_sum * freq_x_sum 
        freq = sys_divide*self.__sample_rate*k_2/k_1
        return freq
        
    def _frequency_lp_measure(self):
        rd_data = self.__axi4lite.read(0x50, 8)
        duty_all = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x60, 4)
        duty_N = self.__data_deal.list_2_int(rd_data)
        freq = duty_N*self.__sample_rate/duty_all
        return freq
                  