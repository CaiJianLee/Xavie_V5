from __future__ import division
import math
from time import sleep
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.1'

class Axi4FftAnalyzer(object):
    
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
        self.__all_power = 0
        self.__fft_power_data = []
        self.__sample_rate = 0
        self.__freq_resolution = 0
        self.__bandwidth_index = 0
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

    def measure_paramter_set(self,bandwidth_hz,sample_rate,decimation_type):
        """ Set measure paramter
            
            Args:
                bandwidth_hz(int): Bandwidth limit, unit is Hz
                sample_rate(int): signal sample rate, unit is Hz
                decimation_type(str): signal decimation type 
                                      'auto' -- automatic detection
                                      '1'/'2'/........
            Returns:
                False | True
        """
        self._decimation_factor_set(decimation_type)     
        self.__sample_rate = sample_rate/self.__decimation_data
        self.__freq_resolution = sample_rate/(8192*self.__decimation_data)
        self.__bandwidth_index = int(bandwidth_hz/self.__freq_resolution)
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
        self._get_fft_data()
        self._base_index_find()
        return True
    
    def thdn_measure(self):
        """ measure thd+n
            
            Args:
                None
            Returns:
                thdn_data(float): thd+n
        """         
        fundamental_power = 0
        for i in range(self.__k1_index-4,self.__k2_index+4):
            fundamental_power = fundamental_power + self.__fft_power_data[i]
        thdn_data = 10*math.log10((self.__all_power-fundamental_power)/fundamental_power)
        return (thdn_data,'dB')
    
    def singal_measure(self):
        """ measure frequency and vpp
            
            Args:
                None
            Returns:
                amp_data(float): Normalized amplitude (0.000~0.999)
                freq_data(float): signal frequency, unit is Hz
        """         
        k1_data = math.sqrt(self.__k1_data)
        k2_data = math.sqrt(self.__k2_data)
        b_data = (k2_data - k1_data)/(k2_data + k1_data) 
        a_data = 2.95494514*pow(b_data,1) + 0.17671943*pow(b_data,3) + 0.09230694*pow(b_data,5)
        amp_data = (k1_data + k2_data)*(3.20976143+0.9187393*pow(a_data,2)+0.14734229*pow(a_data,4))/8192
        amp_data = amp_data/4096
        freq_data = (0.5+a_data+self.__k1_index)*(self.__sample_rate/8192)
        self.__base_frequency = freq_data
        return(amp_data,'V',freq_data,'Hz')
    
    def vpp_measure(self,signal_frequency):
        """ measure the amplitude of the input frequency signal
            
            Args:
                signal_frequency(int): measure signal frequency, unit is hz
            Returns:
                amp_data(float): Normalized amplitude (0.000~0.999)
        """         
        k1_index = int(signal_frequency/self.__freq_resolution)
        k2_index = k1_index + 1
        k1_data = self.__fft_power_data[k1_index]
        k2_data = self.__fft_power_data[k2_index]
        k1_data = math.sqrt(k1_data)
        k2_data = math.sqrt(k2_data)
        b_data = (k2_data - k1_data)/(k2_data + k1_data) 
        a_data = 2.95494514*pow(b_data,1) + 0.17671943*pow(b_data,3) + 0.09230694*pow(b_data,5)
        amp_data = (k1_data + k2_data)*(3.20976143+0.9187393*pow(a_data,2)+0.14734229*pow(a_data,4))/8192 
        amp_data = amp_data/4096  
        return (amp_data,"V")     
    
    def thd_measure(self,harmonic_num):
        """ measure thd
            
            Args:
                harmonic_num(int): harmonic num, <11
            Returns:
                amp_data(float): Normalized amplitude (0.000~0.999)
                thd_data(float): thd data
        """         
        harmonic_freq = []
        harmonic_vpp = []
        harmonic_power = []
        
        harmonic_all_power = 0
        for i in range(1,harmonic_num):
            freq_data = i*self.__base_frequency
            harmonic_freq.append(freq_data)
            k1_index = int(freq_data/self.__freq_resolution)
            k2_index = k1_index+1
            power_temp = 0
            for j in range(k1_index-4,k2_index+4):
                power_temp = power_temp + self.__fft_power_data[j]
            harmonic_power.append(power_temp)
            harmonic_all_power = harmonic_all_power + power_temp
            k1_data = self.__fft_power_data[k1_index]
            k2_data = self.__fft_power_data[k2_index]
            if((k1_data != 0) or (k2_data != 0)):
                k1_data = math.sqrt(k1_data)
                k2_data = math.sqrt(k2_data)
                b_data = (k2_data - k1_data)/(k2_data + k1_data) 
                a_data = 2.95494514*pow(b_data,1) + 0.17671943*pow(b_data,3) + 0.09230694*pow(b_data,5)
                amp_data = (k1_data + k2_data)*(3.20976143+0.9187393*pow(a_data,2)+0.14734229*pow(a_data,4))/8192
            else:
                amp_data = 0
            harmonic_vpp.append(amp_data)     
        thd_data = 10*math.log10((harmonic_all_power-harmonic_power[0])/harmonic_power[0])
        harmonic_all_amp_square = 0
        for i in range(1,harmonic_num-1):
            harmonic_all_amp_square = harmonic_all_amp_square + pow(harmonic_vpp[i],2)
        thd_data1 = 20*math.log10(math.sqrt(harmonic_all_amp_square)/harmonic_vpp[0])
        return(thd_data,'dB',thd_data1,'dB')

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
    
    def _base_index_find(self):
        max_data = max(self.__fft_power_data)
        max_index = self.__fft_power_data.index(max_data)
        max_left_index = max_index -1
        max_left_data = self.__fft_power_data[max_left_index]
        max_right_index = max_index + 1
        max_right_data = self.__fft_power_data[max_right_index]
             
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
        self.__all_power = sum(self.__fft_power_data[8:self.__bandwidth_index])
        return None

    def _get_fft_data(self):
        fft_data = []
        self.__fft_power_data = []
        rd_data = self.__axi4lite.read(0x84,4)
        fft_data_cnt = self.__data_deal.list_2_int(rd_data)
        if(fft_data_cnt != 0):
            fft_data = self.__axi4lite.read_array(0x80, fft_data_cnt*4, 32)
            for i in range(int(fft_data_cnt/2)):
                self.__fft_power_data.append(self.__data_deal.list_2_int(fft_data[i*8:i*8+6]))
        # print(self.__fft_power_data)
        return self.__fft_power_data
             
    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('@%s: Test Register read data error. '%(self.name))
            return False
        return None
 