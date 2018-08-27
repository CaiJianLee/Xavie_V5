from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4SampleMultiplex(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 1024
        self.__axi4lite=Axi4lite(self.name,self.reg_num) 
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))  
        self.__data_deal = DataOperate()  
            
    def enable(self):
        """  Enable function        """            
        self.__axi4lite.write(0x10, [0x00],1) 
        self.__axi4lite.write(0x10, [0x01],1)    
        return None
        
    def disable(self):
        """  Disable function        """    
        self.__axi4lite.write(0x10, [0x00],1)      
        return None
        
    def measure_time_set(self,time_ms): 
        """ Set measure time
            
            Args:
                time_ms(int): mircosecond of measure

            Returns:
                None
        """                
        wr_data = self.__data_deal.int_2_list(time_ms,2)
        self.__axi4lite.write(0x11, wr_data, len(wr_data)) 
        return None
        
    def measure_state_get(self):
        """ Get measure state
            
            Args:
                None

            Returns:
                measure_state(str): 'BUSY' | 'IDLE'
        """                
        rd_data = self.__axi4lite.read(0x13, 1)
        if(rd_data[0] & 0x10 == 0x00):
            measure_state = 'BUSY'
        else:
            measure_state = 'IDLE'
        return measure_state
    
    def measure_start(self):
        """ Start measure
            
            Args:
                None

            Returns:
                False | True
        """         
        measure_state = self.measure_state_get()
        if(measure_state == 'BUSY'):
            logger.error('@%s: bus busy...'%(self.name))
            return False
        self.__axi4lite.write(0x13, [0x01],1)
        return True
         
    def sample_parameter_set(self,sample_rate,switch_wait_ns,switch_sample_count,frame_type = 0x20,frame_channel = 0x0):
        """ Set sample parameter
            
            Args:
                sample_rate(int): ADC Chip sample rate, unit is Hz
                switch_wait_ns(int): The waiting time after switching the sampling channel, unit is ns
                switch_sample_count(int): The number of sampled data after switching the sampling channel 
                frame_type(int): The upload frame type.
                frame_channel(int): freame channel (0~15)
            Returns:
                None
        """    
        sample_cycle = 1000000000/sample_rate;
        ch_wait = int(switch_wait_ns/sample_cycle)-3;
        data_temp = ch_wait + switch_sample_count*pow(2,16) + frame_channel*pow(2,28) 
        wr_data = self.__data_deal.int_2_list(data_temp,4)
        self.__axi4lite.write(0x1c,wr_data,len(wr_data))         
        frame_sample_rate = int(1000000/((ch_wait+3)*sample_cycle));
        wr_data = self.__data_deal.int_2_list(frame_sample_rate,3)
        wr_data.append(frame_type)
        self.__axi4lite.write(0x14,wr_data,len(wr_data))  
        return None
    
    def sample_channel_set(self,ch_sel):
        """ Set sample channel
            
            Args:
                ch_sel(list): select the sample channle

            Returns:
                None
        """         
        if(len(ch_sel) == 0):
            logger.error('@%s: CH Sel Error'%(self.name))
            return
        wr_data = [(len(ch_sel) - 1)]
        self.__axi4lite.write(0x18, wr_data,len(wr_data))
        rw_addr = 0x40
        for i in ch_sel:
            wr_data = [i];
            self.__axi4lite.write(rw_addr, wr_data,len(wr_data))
            rw_addr = rw_addr + 1
        return None    
            
    def channel_attached_set(self,ch_attached):
        """ Set extra information for each sample channel
            
            Args:
                ch_attached(list): extra information for each sample channel

            Returns:
                None
        """             
        if(len(ch_attached) == 0):
            logger.error('@%s: CH Sel Error'%(self.name))
            return
        rw_addr = 0x80
        for i in ch_attached:
            wr_data = [i];
            self.__axi4lite.write(rw_addr, wr_data,len(wr_data))
            rw_addr = rw_addr + 1
        return None
             
    def interrupt_time_get(self,clk_freq,ch_num):
        """ get the posedge time and negedge time of trigger signal
            
            Args:
                clk_freq(int): the frequency of reference clock, unit is Hz 
                ch_num(int): the channel number of trigger

            Returns:
                pos_time(int): trigger posedge time
                neg_time(int): trigger negedge time
        """                    
        if((ch_num > 64) | (ch_num <0)):
            logger.error('@%s: CH Num Error'%(self.name))
            return
        clk_cycle = 1000000000/clk_freq;
        wr_data = self.__data_deal.int_2_list(ch_num, 1)
        self.__axi4lite.write(0x20,wr_data,len(wr_data)) 
        rd_data = [0,0,0,0]
        rd_data = self.__axi4lite.read(0x24, len(rd_data))
        pos_time = self.__data_deal.list_2_int(rd_data) * clk_cycle
        rd_data = self.__axi4lite.read(0x28, len(rd_data))
        neg_time = self.__data_deal.list_2_int(rd_data) * clk_cycle
        return (pos_time,neg_time)        
            
    def trigger_clear(self):
        """ clear the trigger for signal       """          
        self.__axi4lite.write(0x2C, [0x0,0x0], 2)     
        return None   
            
    def posedge_trigger_set(self):
        """ set the posedge trigger for signal       """    
        rd_data = self.__axi4lite.read(0x2C,1)
        rd_data[0] = rd_data[0] | 0x01
        self.__axi4lite.write(0x2C, rd_data,1)
        return None  
        
    def negedge_trigger_set(self):
        """ set the negedge trigger for signal       """        
        rd_data = self.__axi4lite.read(0x2C,1)
        rd_data[0] = rd_data[0] | 0x02
        self.__axi4lite.write(0x2C, rd_data,1)   
        return None
               
    def high_spread_trigger_set(self):
        """ set the high level insufficient trigger for signal       """            
        rd_data = self.__axi4lite.read(0x2C,1)
        rd_data[0] = rd_data[0] | 0x04
        self.__axi4lite.write(0x2C, rd_data,1)   
               
    def low_spread_trigger_set(self):
        """ set the low level insufficient trigger for signal       """    
        rd_data = self.__axi4lite.read(0x2C,1)
        rd_data[0] = rd_data[0] | 0x08
        self.__axi4lite.write(0x2C, rd_data,1)          
              
    def high_thresdhold_level_set(self,normalize_volt):
        """ set the threasdhold for posedge triggger
            
            Args:
                normalize_volt(long): normalize volt. -1 ~ +1

            Returns:
                None
        """                 
        threshold_level = int(normalize_volt * pow(2,15))
        if(threshold_level < 0 ):
            threshold_level = threshold_level + pow(2,16);
        wr_data = self.__data_deal.int_2_list(threshold_level, 2)
        self.__axi4lite.write(0x30, wr_data, 2)
        return None
        
    def volt_normalize(self,signal_volt,signal_full_scale):
        """ Calculate VPP normalization
            
            Args:
                signal_volt(float): the volt of signal, unit is mv
                signal_full_scale(float): the full scale vpp of signal output, unit is mv
            Returns:
                volt_scale(float): normalized volt, (-1.00 ~ +1.00)
        """  
        volt_scale = signal_volt*2/signal_full_scale
        return(volt_scale) 
        
    def set_low_thresdhold_level(self,normalize_volt):
        """ set the threasdhold for negedge triggger
            
            Args:
                normalize_volt(long): normalize volt. -1 ~ +1

            Returns:
                None
        """           
        threshold_level = int(normalize_volt * pow(2,15))
        if(threshold_level < 0 ):
            threshold_level = threshold_level + pow(2,16);
        wr_data = self.__data_deal.int_2_list(threshold_level, 2)
        self.__axi4lite.write(0x34, wr_data, 2)    
        return None       
            
    def set_high_spread_time(self,spread_ms):   
        """ set the threasdhold for high level insufficient triggger
            
            Args:
                normalize_volt(long): normalize volt. -1 ~ +1

            Returns:
                None
        """          
        read_data = self.__axi4lite.read(0x14, 3)
        sample_rate = self.__data_deal.list_2_int(read_data)
        sample_cycle = 1000000/sample_rate;
        spread_cnt = int(spread_ms*1000000 / sample_cycle)
        wr_data = self.__data_deal.int_2_list(spread_cnt, 2)
        self.__axi4lite.write(0x32, wr_data, 2) 
        return None
            
    def set_low_spread_time(self,spread_ms):   
        """ set the threasdhold for low level insufficient triggger
            
            Args:
                normalize_volt(long): normalize volt. -1 ~ +1

            Returns:
                None
        """        
        read_data = self.__axi4lite.read(0x14, 3)
        sample_rate = self.__data_deal.list_2_int(read_data)
        sample_cycle = 1000000/sample_rate;
        spread_cnt = int(spread_ms*1000000 / sample_cycle)
        wr_data = self.__data_deal.int_2_list(spread_cnt, 2)
        self.__axi4lite.write(0x36, wr_data, 2)       
        return None      
            
    def trigger_state_get(self,channel_num):
        """ get trigger state of each channel
            
            Args:
                channel_num(list): the number of channel

            Returns:
                state_out(list): the state of channel
        """          
        read_data = self.__axi4lite.read(0x38,2)
        state_data = self.__data_deal.list_2_int(read_data)
        state_out = []
        for i in range(channel_num):
            state_temp = state_data >>i
            if((state_temp%2) == 1):
                state_out.append('T')
            else:
                state_out.append('N')
        return state_out
            
    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('@%s: Test Register read data error. '%(self.name))
            return False
        return None            
            
            
            
            
            
            
            
            
            
            
            
            