from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4Ad760x():
    
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
        return None
        
    def disable(self):
        """Disable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        return None
        
    def ad760x_reset(self):
        """ad760x reset function"""
        rd_data = self.__axi4lite.read(0x10,1)
        rd_data[0] = rd_data[0] | 0x80;
        self.__axi4lite.write(0x11, rd_data, 1)
        time.sleep(0.001)
        rd_data[0] = rd_data[0] & 0x7F;
        self.__axi4lite.write(0x11, rd_data, 1)
        return None

    def ad760x_single_sample(self,os,v_range):
        """ ad760x single sample
            
            Args:
                os(int): Oversampling set(0~7)
                v_range(string): adc reference voltage set('5V' or '10V')

            Returns:
                voltages(list): [ch0_volt,ch1_volt,...,ch7_volt],  unit is V
        """
        # ctrl reg cfg
        # 0x10 [0]--module_en;[4]--continuous_sample_en
        # 0x11 [2:0]--os;[3]--v_range;[7]--rst_pin_ctrl
        rd_data = self.__axi4lite.read(0x10,2)
        self.__axi4lite.write(0x10, [0x00], 1)
        rd_data[0] = 0x01
        if(v_range == '10V'):
            rd_data[1] = (rd_data[1] & 0xF0) | ((1<<3) | os)
        else:
            rd_data[1] = (rd_data[1] & 0xF0) | os
        self.__axi4lite.write(0x10, rd_data, 2)
        # start sample
        self.__axi4lite.write(0x12, [0x01], 1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x13,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 100:
            time.sleep(0.00001)
            rd_data = self.__axi4lite.read(0x13,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 100):
            logger.error('ad760x sample timeout')
            return False
        #ch0:0x20-0x23;ch1:0x24-0x27;ch2:0x28-0x2B;ch3:0x2C-0x2Fch4:0x30-0x33;ch5:0x34-0x37;ch6:0x38-0x3B;ch7:0x3C-0x3F 
        voltages = []
        volt_reg_addr = 0x20
        for i in range(8):
            rd_data = self.__axi4lite.read(volt_reg_addr,4)
            volt_temp = self.__data_deal.list_2_int(rd_data)
            if(v_range == '10V'):
                volt_temp = volt_temp/pow(2,32)*20
            else:
                volt_temp = volt_temp/pow(2,32)*10
            volt_reg_addr = volt_reg_addr + 0x04
            voltages.append(volt_temp)
        return voltages
    
    def ad760x_continuous_sample(self,os,v_range,sample_rate):
        """ ad760x_continuous_sample enable, and it must invoking the "disable" function to stop the ad760x_continuous_sample.
            When this function enable, the "ad760x_single_sample" function can't used.
            
            os & sample_rate limit description:
                os == 0: sample_rate 2000~200000Hz
                os == 1: sample_rate 2000~100000Hz
                os == 2: sample_rate 2000~50000Hz
                os == 3: sample_rate 2000~25000Hz
                os == 4: sample_rate 2000~12500Hz
                os == 5: sample_rate 2000~6250Hz
                os == 6: sample_rate 2000~3125Hz
                os == 7: invalid, out of commission
            
            Args:
                os(int): Oversampling set(0~7)
                v_range(string): adc reference voltage set('5V' or '10V')
                sample_rate(int): sample_rate set, 2000~200000Hz

            Returns:
                None
        """
        # ctrl reg cfg
        # 0x10 [0]--module_en;[4]--continuous_sample_en
        # 0x11 [2:0]--os;[3]--v_range;[7]--rst_pin_ctrl
        # 0x14~0x15 [15:0] -- sample_rate
        rd_data = self.__axi4lite.read(0x10,2)
        self.__axi4lite.write(0x10, [0x00], 1)
        rd_data[0] = 0x11
        if(v_range == '10V'):
            rd_data[1] = (rd_data[1] & 0xF0) | ((1<<3) | os)
        else:
            rd_data[1] = (rd_data[1] & 0xF0) | os
        self.__axi4lite.write(0x10, rd_data, 2)
        # cfg sample rate
        wr_data = self.__data_deal.int_2_list(int((125000000/sample_rate)-2),2)
        self.__axi4lite.write(0x14, wr_data, 2)
        
        # start sample
        self.__axi4lite.write(0x12, [0x01], 1)
        
        # Until use disable function to stop continuous sample mode.
        
        return None
    
