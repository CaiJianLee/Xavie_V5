from time import sleep
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate



class XadcDevice(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()

    def register_read(self,addr,length):
        rd_data = self.__axi4lite.read(addr,length)
        if(len(rd_data) == 0):
            return False
        return rd_data
    
    
    def register_write(self,addr,data,length):
        if self.__axi4lite.write(addr, data, length) is False:
            return False
        return True
    
    

    
'''  end of file  '''
