from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4SignalSource(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 1024
        self.__axi4lite=Axi4lite(self.name,self.reg_num) 
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num)) 
        self.__data_deal = DataOperate()  
        self.__step_index = 0
            
    def enable(self):
        """enable function"""   
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFE) | 0x00
        self.__axi4lite.write(0x10, [wr_data],1) 
        wr_data = (rd_data[0] & 0xFE) | 0x01
        self.__axi4lite.write(0x10, [wr_data],1)         
        return None
        
    def disable(self):
        """disable function""" 
        rd_data = self.__axi4lite.read(0x10,1)
        wr_data = (rd_data[0] & 0xFE) | 0x00
        self.__axi4lite.write(0x10, [wr_data],1) 
        return None   
    
    def signal_type_set(self,signal_type):
        """ set output signal type
            
            Args:
                signal_type(str): 'sine'--sine wave output
                                  'square' -- square output
                                  'AWG' -- arbitrary waveform output

            Returns:
                True | False
        """          
        self.__axi4lite.write(0x11, [0x00],1)
        rd_data = self.__axi4lite.read(0x10,1)
        if(signal_type == 'sine'):
            signal_type_flag = 0x10
        elif(signal_type == 'square'):
            signal_type_flag = 0x00
        elif(signal_type == 'AWG'):
            signal_type_flag = 0x40            
        else:
            logger.error('@%s: signal type set error'%(self.name))
            return False
        wr_data = (rd_data[0] & 0x0F) | signal_type_flag;
        self.__axi4lite.write(0x10, [wr_data],1) 
        return True
        
    def signal_time_set(self,signal_time):
        """ set output signal duration
            
            Args:
                signal_time(int): signal output duration, unit is us

            Returns:
                True | False
        """     
        self.__axi4lite.write(0x11, [0x00],1)
        wr_data = self.__data_deal.int_2_list(signal_time, 4)
        self.__axi4lite.write(0x40,wr_data,len(wr_data))
        return True
    
    def swg_paramter_set(self,sample_rate,signal_frequency,vpp_scale,square_duty,offset_volt = 0):  
        """ set standard waveform(sine or square) parameter
            
            Args:
                sample_rate(int): external DAC sample rate, unit is SPS
                signal_frequency(int): output signal frequency, unit is Hz
                vpp_scale(float): full scale ratio, (0.000~0.999)
                square_duty(float): duty of square, (0.001~0.999)
                offset_volt(flaot): offset volt,(-0.99999~0.99999)
            Returns:
                None
        """             
        self.__axi4lite.write(0x11, [0x00],1)
        freq_ctrl  = int(pow(2,32) * signal_frequency / sample_rate)
        wr_data = self.__data_deal.int_2_list(freq_ctrl, 4)
        self.__axi4lite.write(0x20,wr_data,len(wr_data))
        vpp_ctrl = int((pow(2,16)-1) * vpp_scale)
        wr_data = self.__data_deal.int_2_list(vpp_ctrl, 2)
        self.__axi4lite.write(0x24,wr_data,len(wr_data))
        duty_ctrl = int((sample_rate/signal_frequency)*square_duty)
        wr_data = self.__data_deal.int_2_list(duty_ctrl, 4)
        self.__axi4lite.write(0x28,wr_data,len(wr_data))
        offset_volt_hex = int(offset_volt*pow(2,23))
        wr_data = self.__data_deal.int_2_list(offset_volt_hex, 3)
        self.__axi4lite.write(0x2C, wr_data, len(wr_data))
        return None 
        
        
    def signal_output(self):
        """signal output enable"""   
        self.__axi4lite.write(0x11, [0x01],1)
        return None 
    
    def _awg_step_set(self,sample_rate,start_volt,stop_volt,duration_ms):
        self.__axi4lite.write(0x11, [0x00],1)
        sample_cycle = 1000/sample_rate;
        duration_step = duration_ms/sample_cycle;
        duration_step_cnt = int(duration_step/pow(2,16)) + 1
        volt_step = (stop_volt-start_volt)/duration_step_cnt
        for i in range(0,duration_step_cnt):
            wr_data = []
            start_volt_temp = i *volt_step + start_volt
            step_duration_temp = int(duration_step/duration_step_cnt)
            step_ovlt_temp = volt_step*pow(2,16)/step_duration_temp
            start_volt_hex = int(start_volt_temp*pow(2,15))
            step_ovlt_hex = int(step_ovlt_temp*pow(2,15))
            wr_list = self.__data_deal.int_2_list(step_duration_temp, 2)
            wr_data.extend(wr_list)
            wr_list = self.__data_deal.int_2_list(step_ovlt_hex, 4)
            wr_data.extend(wr_list)
            wr_list = self.__data_deal.int_2_list(start_volt_hex, 2)
            wr_data.extend(wr_list)
            wr_data.append(self.__step_index)
            self.__axi4lite.write(0x30, wr_data, len(wr_data))
            self.__axi4lite.write(0x39, [0x01], 1)
            self.__step_index = self.__step_index + 1
        return None
        
    def awg_parameter_set(self,sample_rate,awg_step):
        """ set arbitrary waveform parameter
            
            Args:
                sample_rate(int): external DAC sample rate, unit is SPS
                awg_step(list): arbitrary waveform step, list unit is (start_volt,stop_volt,duration_ms)
                                start_volt(float) -- step start volt (-1 ~ +1)
                                stop_volt(float) -- step stop volt (-1 ~ +1)
                                duration_ms(float) -- durarion time
            Returns:
                None
        """          
        self.__step_index = 0
        for awg_step_temp in awg_step:
            self._awg_step_set(sample_rate, awg_step_temp[0], awg_step_temp[1], awg_step_temp[2])
        self.__axi4lite.write(0x3A, [(self.__step_index - 1)], 1)
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
        
            
        
            
