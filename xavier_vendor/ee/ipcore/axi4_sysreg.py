from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4Sysreg(object):
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
            
    def version_get(self):
        """ Get FPGA version
            
            Args:
                None

            Returns:
                fpga_version(str): fpga version(0.0~15.15)
        """        
        rd_data = self.__axi4lite.read(0x10,1)
        if(rd_data == False):
            return False
        fpga_version_h = (rd_data[0] & 0xF0) >> 4
        if(fpga_version_h < 10):
            fpga_version_h_str = '0' + str(fpga_version_h)
        else:
            fpga_version_h_str = str(fpga_version_h)
        fpga_version_l = (rd_data[0] & 0x0F)
        if(fpga_version_l < 10):
            fpga_version_l_str = '0' + str(fpga_version_l)
        else:
            fpga_version_l_str = str(fpga_version_l)
        fpga_version =fpga_version_h_str + '.' + fpga_version_l_str
        return fpga_version
    
    
    def uct_set(self,uct_second,uct_mircosecond):
        """ Set uct 
            
            Args:
                uct_second(int): second time
                uct_mircosecond(int): mircosecond time(0~999)

            Returns:
                None
        """          
        uct_1 = self.__data_deal.int_2_list(uct_mircosecond, 2)
        uct_2 = self.__data_deal.int_2_list(uct_second, 4)
        wr_data =uct_1 + uct_2 
        self.__axi4lite.write(0x40,wr_data,len(wr_data))      
        self.__axi4lite.write(0x46,[0x01],1)
        return None
        
    def uct_get(self):
        """ Get uct 
            
            Args:
                None

            Returns:
                uct_second(int): second time
                uct_mircosecond(int): mircosecond time
        """            
        self.__axi4lite.write(0x47,[0x01],1)
        rw_addr = 0x48
        rd_data = self.__axi4lite.read(rw_addr,6)
        print(rd_data)
        if(rd_data == False):
            return False
        uct_mircosecond = self.__data_deal.list_2_int(rd_data[0:1])
        uct_second = self.__data_deal.list_2_int(rd_data[2:5])
        return(uct_second,uct_mircosecond)
    
    def external_register_write(self,reg_addr,reg_data):
        """ write external register
            
            Args:
                reg_addr(int): register address, 0x80~0x9F
                reg_data(list): register write data

            Returns:
                None
        """               
        self.__axi4lite.write(reg_addr,reg_data,len(reg_data))
        return None
    
    def external_register_read(self,reg_addr,read_length):
        """ write external register
            
            Args:
                reg_addr(int): register address, 0x80~0x9F
                read_length(int): read data bytes

            Returns:
                reg_data(list): register read data
        """               
        reg_data = self.__axi4lite.read(reg_addr,read_length)
        return reg_data            
    
    