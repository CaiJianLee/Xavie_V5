"""AD717X ADC Chip driver

    AD7175 and AD7177 can be driven by this driver code.

"""
from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

__version__ = '1.0.0'

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
        #logger.info('channel: ',sample_channel,'rd_data: 0x%08x 0x%06x'%(reg_data,sample_data))
        return (sample_channel,sample_data)

    def code_2_mvolt(self,code,mvref,bits):
        """ Adc sample code conversion to mVolt
        
        Args:
            code: sample code
            mvref:(value,unit)
            bits: ADC sample bits
                AD7175: 24 or 16 bits
                AD7177: 32 or 24 bits
        Returns:
            volt: (value,uinit)
                
        """
        volt = code
        volt -= 0x800000
        bits = bits-1
        volt /= 1<<bits
        volt *= mvref[0]

        return (volt,mvref[1])

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
    
    def frame_channel_and_samplerate_set(self,channel_no,samplerate):
        """ Frame channel number and sample rate set.

            Only used in continue sample wor mode

            Args:
                channel_no: channel number
                samplerate: ADC sample rate
        """
        wr_data = [0,0,0,0]
        wr_data[0] = samplerate%256;
        wr_data[1] = (samplerate>>8)%256
        wr_data[2] = (samplerate>>16)%256
        wr_data[3] = channel_no*16
        state = self.__axi4lite.write(0xF0,wr_data,len(wr_data))
        return state
   
    def data_analysis(self,data_count):
        """ Adc sample data analysis
        
        Args:
            data_count(int): sample data count
        Returns:
            get_data(list): sample data list
                
        """        
        rd_data = self.__axi4lite.read(0x26,1)
        if((rd_data[0] & 0x04) != 0x04):
            logger.warning('AD717X is not in continuous sample mode')
            return False

        wr_data = self.__data_deal.int_2_list(data_count, 2)
        self.__axi4lite.write(0x61, wr_data, len(wr_data))
        self.__axi4lite.write(0x60, [0x01], 1)
        rd_data = [0x00]
        while(rd_data[0] & 0x01 == 0x00):
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x63,1)
        get_data = [];
        for i in range(0,data_count):
            #rw_addr = i + 0x1000;
            rw_addr = i*4 + 0x1000;
            rd_data = self.__axi4lite.read(rw_addr, 4)
            #rd_int = self.__data_deal.list_2_int(rd_data)
            rd_int = rd_data[0] | (rd_data[1] << 8) | (rd_data[2] << 16) |\
                          (rd_data[3] << 24)
            #rd_int = rd_int - 0x8000
            get_data.append(rd_int)
        return get_data

    def _test_register(self,test_data):
        wr_data = self.__data_deal.int_2_list(test_data,4)
        self.__axi4lite.write(0x00,wr_data,len(wr_data))
        
        rd_data = self.__axi4lite.read(0x00,len(wr_data))
        test_out = self.__data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            logger.error('Register test failure')
            return False        
        return True            