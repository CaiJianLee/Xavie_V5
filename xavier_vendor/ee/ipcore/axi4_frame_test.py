from time import sleep
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class AXI4_Frame_Test(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        
    def _test_register(self,test_data):
        wr_data=self.__data_deal.int_2_list(test_data,16)
        self.__axi4lite.write(0x00,wr_data,len(wr_data));
        rd_data = self.__axi4lite.read(0x00,8);
        check_data = self.__data_deal.list_2_int(rd_data)
        if(check_data != test_data):
            logger.error('@ %s: Test Register read data error.'%(self.name))
            return False
        #print('Peripherals register test pass')
        return True
    
    def enable(self):
        self.__axi4lite.write(0x10,[0x00],1)
        self.__axi4lite.write(0x10,[0x01],1)
        return True
        
    def disbale(self):
        self.__axi4lite.write(0x10,[0x00],1)
        return True
    
    def frame_gen_set(self,frame_id,frame_length):
        wr_data_int = frame_length * pow(2,16) + frame_id;
        wr_data = self.__data_deal.int_2_list(wr_data_int, 4)
        self.__axi4lite.write(0x2C,wr_data,len(wr_data))
        return True
    
    def frame_test_start(self):
        self.__axi4lite.write(0x11,[0x01],1)
        return True
    
    def frame_test_stop(self):
        self.__axi4lite.write(0x11,[0x00],1)
        return True
     
    def tx_state_get(self):
        rd_data = self.__axi4lite.read(0x20, 4)
        frame_count = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x24,8)
        frame_time_cnt = self.__data_deal.list_2_int(rd_data)
        frame_time = float(frame_time_cnt) *8 /1000000000
        return(frame_time,frame_count)
    
    def rx_state_get(self):
        rd_data = self.__axi4lite.read(0x30, 4)
        frame_count = self.__data_deal.list_2_int(rd_data)
        rd_data = self.__axi4lite.read(0x34,8)
        frame_time_cnt = self.__data_deal.list_2_int(rd_data)
        frame_time = float(frame_time_cnt) *8 /1000000000
        rd_data = self.__axi4lite.read(0x3C, 4)
        error_count = self.__data_deal.list_2_int(rd_data)
        return(frame_time,frame_count,error_count)        
        
    
            
    
            
    
    