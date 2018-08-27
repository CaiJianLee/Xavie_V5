from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

__version__ = '1.1.0'

class Axi4Ad717x(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 8192
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        
    def enable(self):
        """Enable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        self.__axi4lite.write(0x10,[0x01],1)
        
    def disable(self):
        """Disable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        
    def register_read(self,reg_addr):
        """ Read value from ADC chip register
            
            Args:
                reg_addr: ADC chip register address(0x00-0xff)

            Returns:
                register value: (0x00-0xffffffff)
        """
        rd_data = self.__axi4lite.read(0x26,1)
        if(rd_data[0] & 0x01 == 0x00):
            logger.warning('AD717X Bus is busy now')
            return False

        com_data = (0x3F & reg_addr) | 0x40;
        wr_data = [com_data,0x01]
        self.__axi4lite.write(0x24, wr_data, len(wr_data))
        rd_data = [0x00]
        timeout_cnt = 0
        while(rd_data[0] & 0x01 == 0x00) and (timeout_cnt < 1000):
            time.sleep(0.001)
            timeout_cnt = timeout_cnt + 1
            rd_data = self.__axi4lite.read(0x26,1)
        if(timeout_cnt == 1000):
            logger.warning('AD717X read register wait timeout')
            return False

        rd_data = self.__axi4lite.read(0x28,4)
        rd_data = rd_data[0] | (rd_data[1] << 8) | (rd_data[2] << 16) |\
                      (rd_data[3] << 24)
        return rd_data
    
    def register_write(self,reg_addr,reg_data):
        """ Write value to ADC chip register
            
            Args:
                reg_addr: ADC chip reg (0x00-0xff)
                reg_data: register value(0x00-0xffffffff)

            Returns:
                True | False
        """
        rd_data = self.__axi4lite.read(0x26,1)
        if(rd_data[0] & 0x01 == 0x00):
            logger.warning('AD717X Bus is busy now')
            return False

        wr_data = self.__data_deal.int_2_list(reg_data, 4)
        com_data = (0x3F & reg_addr);
        wr_data.append(com_data)
        wr_data.append(0x01)
        self.__axi4lite.write(0x20, wr_data, len(wr_data))
        rd_data = [0x00]
        timeout_cnt = 0
        while(rd_data[0] & 0x01 == 0x00) and (timeout_cnt < 1000):
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x26,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 1000):
            logger.warning('AD717X write register wait finish timeout')
            return False

        return True

    def single_sample_code_get(self):
        """ ADC chip single sample
            
            Returns:
                (channel,sample_code)
        """
        rd_data = self.register_read(0x01)
        wr_data = rd_data & 0xFF0F | 0x0000
        self.register_write(0x01, wr_data)
        rd_data = self.register_read(0x01)
        if((rd_data & 0x00F0) != 0):
            logger.warning("AXI4 AD717X 0x01 ==%s"%(hex(rd_data)))
            return False

        wr_data = rd_data & 0xFF0F | 0x0010
        self.register_write(0x01, wr_data)
        reg_data = self.register_read(0x04)
        rd_data = self.__axi4lite.read(0x26, 1)
        if(rd_data[0] & 0x08 == 0x08):
            sample_channel = (reg_data & 0x0000000F)
            sample_data = (reg_data & (0xFFFFFF00)) >> 8
        else:
            sample_channel = 'Null'
            sample_data = reg_data & (0x00FFFFFF)
        return (sample_channel,sample_data)

    def continue_sample_mode(self):
        """ ADC chip work in continue sample mode,cpu can not control the bus
            
            Returns:
                True | False
        """
        rd_data = self.register_read(0x01)
        wr_data = rd_data & 0xFF0F | 0x0000
        self.register_write(0x01, wr_data)
        rd_data = self.register_read(0x02)
        reg_data = rd_data & 0xFF7F | 0x0080
        rd_data = self.__axi4lite.read(0x26,1)
        if(rd_data[0] & 0x01 == 0x00):
            logger.warning('Error:    AD717X Bus is busy now')
            return False

        wr_data = self.__data_deal.int_2_list(reg_data, 4)
        com_data = (0x3F & 0x02);
        wr_data.append(com_data)
        wr_data.append(0x01)
        self.__axi4lite.write(0x20, wr_data, len(wr_data))
        return True
        
    def single_sample_mode(self):
        """ ADC chip exit continue sample mode,cpu can control the bus
        """
        wr_data = [0x44,0x01]
        state = self.__axi4lite.write(0x24, wr_data, len(wr_data))
        return state
        
    def reset(self):
        """ Reset ADC chip
        """
        wr_data = [0xFF,0x01]
        state = self.__axi4lite.write(0x24, wr_data, len(wr_data))
        return state
    
    def chip_id_set(self,chip_id):
        """ set chip_id
            
            Args:
                chip_id(int): chip id, 0~8
            Returns:
                True|False
        """  
        wr_data = [chip_id]
        state = self.__axi4lite.write(0x13,wr_data,len(wr_data))
        return state
   
    def continue_sample_capture(self):
        """ read continue sampld data
            
            Args:
                None
            Returns:
                sample_data(list): sample data
        """
        rd_data = self.__axi4lite.read(0x26,1)
        sample_state = rd_data[0] & 0x04
        if(sample_state == 0):
            logger.warning('AD717X not in continue sample mode')
            return False
        self.__axi4lite.write(0x11, [0x01], 1)
        rd_data = self.__axi4lite.read(0x12,1)
        if(rd_data[0]&0x02 == 0x00):
            logger.warning('AD717X capture fifo reset failt')
            return False
        self.__axi4lite.write(0x11, [0x00], 1)  
        time_out = 0
        while time_out <300:
            rd_data = self.__axi4lite.read(0x12,1)
            if rd_data[0]&0x01 == 0x01:
                break
            else:
                time_out = time_out + 1
                time.sleep(0.01)
        if time_out == 3000:
            logger.error('@%s: capture data time out'%(self.name)) 
            return False        
        receive_list = self.__axi4lite.read_array(0x60, 2048, 32)       
        return receive_list     