from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate
import time
__version__ = '1.0.0'

class Axi4TimeDetect_v1(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        rd_data = self.__axi4lite.read(0x04,4)
        self.__clk_frequency = self.__data_deal.list_2_int(rd_data) 
    
    
    def disable(self):
        """  Disable function        """        
        self.__axi4lite.write(0x10,[0x00],1)
        return None

    def enable(self):
        """  Enable function        """         
        self.__axi4lite.write(0x10,[0x00],1)
        self.__axi4lite.write(0x10,[0x01],1)

        return None
        
    def measure_disbale(self):
        """  Disable function        """         
        self.__axi4lite.write(0x11,[0x00],1)
           
    
    def measure_enable(self):
        """  Enable function        """ 
        self.__axi4lite.write(0x11,[0x00],1)
        time.sleep(0.01)        
        self.__axi4lite.write(0x11,[0x01],1)               
    def start_edge_set(self,start_edge_type='A-POS'):
        """ Set width measure start_edge_type
            
            Args:
                start_edge_type(str): 'A-POS'  -- signal A posedge
                                      'A-NEG'  -- signal A negedge
                                      'B-POS'  -- signal B posedge
                                      'B-NEG'  -- signal B negedge
									  'A-PORN'  -- signal A posedge or A negedge
									  'B-PORN'  -- signal B posedge or B negedge
            Returns:
                None
        """
        self.__axi4lite.write(0x12,[0x00],1)        
        if(start_edge_type == 'A-POS'):
            start_edge_data = 0x00
        elif(start_edge_type == 'A-NEG'):
            start_edge_data = 0x01
        elif(start_edge_type == 'B-POS'):
            start_edge_data = 0x02
        elif(start_edge_type == 'B-NEG'):
            start_edge_data = 0x03
        elif(start_edge_type == 'A-PORN'):
            start_edge_data = 0x04	
        elif(start_edge_type == 'B-PORN'):
            start_edge_data = 0x05		
        else:
            logger.error('@%s: Parameter Error'%(self.name)) 
            return False  
        wr_data =  start_edge_data;    
        self.__axi4lite.write(0x12, [wr_data], 1)
        return None
 
    def stop_edge_set(self,stop_edge_type='B-POS'):
        """ Set width measure stop_edge_type
            
            Args:
                stop_edge_type(str): 'A-POS'  -- signal A posedge
									 'A-NEG'  -- signal A negedge
                                     'B-POS'  -- signal B posedge
                                     'B-NEG'  -- signal B negedge
									 'A-PORN'  -- signal A posedge or A negedge
									 'B-PORN'  -- signal B posedge or B negedge
            Returns:
                None
        """
        self.__axi4lite.write(0x13,[0x00],1)        
        if(stop_edge_type == 'B-POS'):
            stop_edge_data = 0x00
        elif(stop_edge_type == 'B-NEG'):
            stop_edge_data = 0x01
        elif(stop_edge_type == 'A-POS'):
            stop_edge_data = 0x02
        elif(stop_edge_type == 'A-NEG'):
            stop_edge_data = 0x03
        elif(stop_edge_type == 'A-PORN'):
            stop_edge_data = 0x04	
        elif(stop_edge_type == 'B-PORN'):
            stop_edge_data = 0x05	
        else:
            logger.error('@%s: Parameter Error'%(self.name)) 
            return False 
        wr_data =  stop_edge_data;     
        self.__axi4lite.write(0x13, [wr_data], 1)       
        return None    
        
    def detect_time_get(self,detect_time_ms):
        """ get  measure data
            
            Args:
                None
            Returns:
                detect_data(float): the data is start_edge_type to stop_edge_type time, unit is us
                                 
        """      

        rd_data = self.__axi4lite.read(0x20, 1)
        detect_time_out=0
        while rd_data[0]!=0x01 and (detect_time_out<detect_time_ms+1000):
            time.sleep(0.001)
            detect_time_out+=1 
            rd_data = self.__axi4lite.read(0x20, 1)
        if(detect_time_out== detect_time_ms+1000): 
            logger.error('@%s: Detect time out'%(self.name))
            return False  
        else:
            rd_data=self.__axi4lite.read(0x24,4)
            detect_time=self.__data_deal.list_2_int(rd_data)
            clk_period = 1000.0/self.__clk_frequency
            detect_data= clk_period*detect_time
            self.__axi4lite.write(0x11,[0x00],1)   
        return ('detect_time',detect_data,'us') 

       
            
        
        
        
        
        
        
        
        
        
