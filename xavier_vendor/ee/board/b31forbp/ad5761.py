# -*- coding:utf-8 -*-
__author__='jingyong.xiao'

'''AD5761  single channel, 16-bit serial input, voltage output'''
from ee.ipcore.axi4_spi import Axi4Spi
from ee.common import logger
import time
import math

reg_addr = {
    "write_to_input_reg":       0x1,
    "dac_update_from_input_reg": 0x2,
    "write_and_update_dac_reg":  0x3,
    "write_to_control_reg":     0x4,
    "software_data_reset":      0x7,
    "disable_daisy_chain_reg":  0x9,
    "readback_input_reg":       0xa,
    "readback_dac_reg":         0xb,
    "readback_control_reg":     0xc,
    "software_full_reset":      0xf,
}

ra_dict = {
    0x0 : {'m': 8,  'c': 4},      # -10V ~ 10V
    0x1 : {'m': 4,  'c': 0},      # 0V ~ 10V
    0x2 : {'m': 4, 'c':  2},      # -5V ~ 5V
    0x3 : {'m': 2,  'c': 0},      # 0V ~ 5V
    0x4 : {'m': 4,  'c': 1},      # -2.5V ~ 7.5V
    0x5 : {'m': 2.4, 'c': 1.2}, # -3V ~ 3V
    0x6 : {'m': 6.4,  'c': 0},   # 0V ~ 16V
    0x7 : {'m': 8,  'c': 0},      # 0V ~ 20V

}

class AD5761():

    def __init__(self,device_name, vref = 2500, control_reg_data = 0x061):
        self.__spi_device = Axi4Spi(device_name)
        self.__spi_device.disable()
        self.__spi_device.enable()
        # warning: 看芯片手册，这个应该配置为neg而不是pos。
        # 由于fpga底层搞反了，所以这里暂时配置为了pos
        self.__spi_device.config(100000,'pos', 10)

        self.__m = ra_dict[control_reg_data & 0x7]['m']
        self.__c = ra_dict[control_reg_data & 0x7]['c']

        if 0x20 == (control_reg_data & 0x20):
            self.__vref = 2500.0 # use internal 2.5V voltage reference
        else:
            self.__vref = vref  # use external voltage reference
        self.write_control_register(control_reg_data)

       
    def write_control_register(self, reg_data):
        self.write_register(reg_addr['software_full_reset'], 0)
        time.sleep(0.05)
        return self.write_register(reg_addr['write_to_control_reg'], reg_data)
                
    def write_register(self,reg_addr,reg_data):
        '''write to registers
            args:
                reg_addr:Low four bit valid,bit 4 is 0
                reg_data:2 bytes
            returns:
                if success:
                    True
                if failed:
                    False
        '''
        write_data = [reg_addr & 0x0F, reg_data >> 8 & 0xFF, reg_data & 0xFF]
        return self.__spi_device.write(write_data)
        
    def read_register(self,reg_addr):
        '''read from registers
            args:
                reg_addr:Low four bit valid,bit 4 is 0
            returns:
                if success:2 bytes
                    0x0000~0xffff
                if failed:
                    False
        '''
        if not self.write_register(reg_addr, 0x0):
            return False
        read_data_list = self.__spi_device.read(3)
        if not read_data_list:
            return False
        if reg_addr != (read_data_list[0] & 0x0F):
            logger.error('The read back adrress is not equal to the address that you want to read!')
            return False
        return (read_data_list[1] << 8) | read_data_list[2]

        
    def output_voltage(self,volt):
        '''Set output voltage
            args:
                volt: input voltage at specified range
            returns:
                if success:
                    True
                if failed:
                    False
        '''
        dac_data = int((volt / self.__vref + self.__c) / self.__m * (2**16) )

        if dac_data > 2**16 - 1:
            dac_data = 0xFFFF
        elif dac_data < 0:
            dac_data = 0
        return self.write_register(reg_addr["write_and_update_dac_reg"], dac_data)
       
    def readback_output_voltage(self):
        '''readback output voltage
            args:
                null
            returns:
                if success:
                    voltage
                if failed:
                    False
        '''
    
        ret = self.read_register(reg_addr["readback_dac_reg"])
        if not ret:
            return False
            
        voltage = self.__vref * (self.__m * ret / (math.pow(2,16) - 1) - self.__c )
        return voltage

