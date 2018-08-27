from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4WidthMeasure(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        self.__sysclk_period = 8
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        rd_data = self.__axi4lite.read(0x0C,4)
        self.__clk_frequency = self.__data_deal.list_2_int(rd_data)
    
    edge_list = {0:'A-POS',1:'A-NEG',2:'B-POS',3:'B-NEG'}
    
    
    def enable(self):
        """  Enable function        """         
        self.__axi4lite.write(0x10,[0x00],1)
        self.__axi4lite.write(0x10,[0x01],1)
        return None
        
    def disable(self):
        """  Disable function        """        
        self.__axi4lite.write(0x10,[0x00],1)
        return None
    
    def measure_enable(self):
        """  Enable function        """         
        self.__axi4lite.write(0x11,[0x01],1)        
        
    def measure_disbale(self):
        """  Enable function        """         
        self.__axi4lite.write(0x11,[0x00],1)              
    
    def start_point_set(self,edge_list=['A-POS']):
        """ Set width measure start point
            
            Args:
                edge_list(list): 'A-POS'  -- signal A posedge
                                 'A-NEG'  -- signal A negedge
								 'B-POS'  -- signal B posedge
                                 'B-NEG'  -- signal B negedge
            Returns:
                None
        """      	
        edge_data = 0
        for edge_sel in edge_list:
            if(edge_sel == 'A-POS'):
                edge_data = edge_data | 0x01
            elif(edge_sel == 'A-NEG'):
                edge_data = edge_data | 0x02
            elif(edge_sel == 'B-POS'):
                edge_data = edge_data | 0x04
            elif(edge_sel == 'B-NEG'):
                edge_data = edge_data | 0x08
            else:
                logger.error('@%s: Parameter Error'%(self.name)) 
                return False  
        self.__axi4lite.write(0x12, [edge_data], 1)
        return None
 
    def stop_point_set(self,edge_list=['A-POS']):
        """ Set width measure stop point
            
            Args:
                edge_list(list): 'A-POS'  -- signal A posedge
                                 'A-NEG'  -- signal A negedge
								 'B-POS'  -- signal B posedge
                                 'B-NEG'  -- signal B negedge
            Returns:
                None
        """       	
        edge_data = 0
        for edge_sel in edge_list:
            if(edge_sel == 'A-POS'):
                edge_data = edge_data | 0x01
            elif(edge_sel == 'A-NEG'):
                edge_data = edge_data | 0x02
            elif(edge_sel == 'B-POS'):
                edge_data = edge_data | 0x04
            elif(edge_sel == 'B-NEG'):
                edge_data = edge_data | 0x08
            else:
                logger.error('@%s: Parameter Error'%(self.name)) 
                return False  
        self.__axi4lite.write(0x13, [edge_data], 1)       
        return None    
        
    def width_get(self):
        """ get width measure data
            
            Args:
                None
            Returns:
                width_data(list): the unit list is [width_time, stop_point, start_point]
                                  width_time is the width measure time, unit is ns
                                  and the width measure is form start_point to stop_point,
                                  start_point and stop_ponit is 'A-POS'/'B-POS'/'A-NEG'/'B-NEG'
                                  e.g : [[1100,'A-NEG','A-POS'],[1200,'A-NEG','A-POS'],[1000,'A-NEG','A-POS']]
        """       	
        rd_data = self.__axi4lite.read(0x24, 4)   
        width_data_cnt = self.__data_deal.list_2_int(rd_data)
        rd_dta = self.__axi4lite.read_array(0x20, width_data_cnt*4, 32)
        clk_period = 1000000/self.__clk_frequency
        width_data = []
        for i in range(width_data_cnt):
            rd_data_temp = rd_dta[i*4:i*4+3]
            width_data_temp = self.__data_deal.list_2_int(rd_data_temp)
            data_a = (width_data_temp >> 4)*clk_period
            data_b = width_data_temp%4
            data_c = width_data_temp%16 >>2
            width_data.append([data_a,self.edge_list[data_c],self.edge_list[data_b]])
        return width_data
            
            
        
        
        
        
        
        
        
        
        