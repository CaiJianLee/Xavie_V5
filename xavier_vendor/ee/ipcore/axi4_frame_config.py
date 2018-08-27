from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4Frame(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        self.__sysclk_period = 8
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
    
    def enable(self):
        """  Enable function        """         
        self.__axi4lite.write(0x10,[0x00],1)
        self.__axi4lite.write(0x10,[0x01],1)
        return None
        
    def disable(self):
        """  Disable function        """        
        self.__axi4lite.write(0x10,[0x00],1)
        return None
    
    def frame_state_set(self,frame_state = 'close',frame_time = 100):
        """ set frame out state
            
            Args:
                frame_state(str): 'close' -- close frame output
                                  'always_open' -- always open frame output
                                  'open' -- open frame output for a while
                frame_time(int):  frame output time, unit is ms, for 1~30000000
            Returns:
                True|False
        """         
        if frame_state == 'close':
            self.__axi4lite.write(0x12,[0x00],1)
        elif frame_state == 'always_open':
            wr_data = [0xFF,0xFF,0xFF,0xFF]
            self.__axi4lite.write(0x14, wr_data, len(wr_data))
            self.__axi4lite.write(0x12,[0x01],1)
        elif frame_state == 'open':
            frame_time_cnt = int(frame_time*1000000/self.__sysclk_period)
            wr_data = self.__data_deal.int_2_list(frame_time_cnt, 4)
            print(wr_data)
            self.__axi4lite.write(0x14, wr_data, len(wr_data))
            self.__axi4lite.write(0x12,[0x01],1)
        else:
            logger.error('@%s: Parameter Error'%(self.name)) 
            return False
        return True
    
    def frame_config_set(self,frame_type=0x10,chip_number = 0,payload_width = 4,uct_insert = 'TS',config_list=[0,0,0,0,0,0,0,0,0,0]):
        """ set frame parameter
            
            Args:
                frame_type(int): frame informatin type, 0~255
                chip_number(int):  Chip number, 0~15
                payload_width(int): 1 -- payload is 1 byte
                                    2 -- payload is 2 byte
                                    4 -- payload is 4 byte
                uct_insert(str):  'TS' -- insert uct time
                                  'NG' -- not insert uct time
                                  user config_list[4:9] to uct time
                config_list(list): Frame Customize parameters,list length is 10, the unit of list is from 0 to 255
            Returns:
                None
        """             
        if uct_insert == 'TS':
            self.__axi4lite.write(0x11,[0x01],1)
        else:
            self.__axi4lite.write(0x11,[0x00],1)
        config_data = []
        config_data.append(frame_type)
        data_temp = (payload_width-1)*16+chip_number
        config_data.append(data_temp)
        config_data.extend(config_list)
        self.__axi4lite.write(0x20, config_data, len(config_data))
        return None
        
            
        
            
