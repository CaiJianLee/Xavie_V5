#-*- coding: UTF-8 -*-
from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4PowerPwmCore():
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 8192
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
    
    def read_adc_sample_data(self):
        """ read_adc_sample_data
            
            Args:
                None

            Returns:
                adc_value: the normalized min level of input signal, unit is V,-1V ~ +1V
                              the true voltage value needs to be multiplied by the reference range.
        """
        # 0x38~0x3B [31:0]--adc_data:
        rd_data = self.__axi4lite.read(0x38,4)
        adc_value = self.__data_deal.list_2_int(rd_data)/pow(2,31);
        return adc_value
        
    def power_pwm_output_disable(self):
        """Disable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        return None

    def power_pwm_output_enable(self,pwm_mode,pid_en,adc_dec_param,p_param,i_param,d_param,pwm0_duty,pwm1_duty,pwm_minimum_duty=0.05,pwm_maximum_duty=0.95,pwm_error_duty=0.01,adc_tran_pwm_param=72):
        """ power_pwm_en
            
            Args:
                pwm_mode(bool): 0-singal,1-double
                pid_en(bool): For enable PID modulation.
                adc_dec_param(int): 0~65535, ADC sampling decimation coefficient.
                p_param(float): -0.9999~+0.9999, PID proportional parameters.
                i_param(float): -0.9999~+0.9999, PID integral parameter.
                d_param(float): -0.9999~+0.9999, PID differential parameter.
                pwm0_duty(float): 0.05~0.95, pwm0_param = pwm0_duty * 624, pwm0 duty parameter.
                pwm1_duty(float): 0.05~0.95, pwm0_param = pwm0_duty * 624, pwm1 duty parameter.
                pwm_minimum_duty(float): 0.05~0.95, pwm_minimum_param = pwm_minimum_duty * 624, for PID modulation, limit minimum PWM duty output
                pwm_maximum_duty(float): 0.05~0.95, pwm_minimum_param = pwm_maximum_duty * 624, for PID modulation, limit maximum PWM duty output
                pwm_error_duty(float): 0.05~0.95, pwm_error_param = pwm_maximum_duty * 624, For PID modulation, The error exceeding this value will start the PID modulation
                adc_tran_pwm_param(int): (3.5*5/24)*(adc/2^15)*(125000/200) ≈> adc/72 => adc_tran_pwm_param = 72
                                        3.5 => Attenuation coefficient,
                                        5   => ADC input range,+-5V
                                        24  => Voltage output range
                                        125000 => FPGA IP base frequency, KHZ
                                        200 => PWM frequency, KHZ
            Returns:
                None
        """ 
        self.power_pwm_output_disable()
        # cfg param
        wr_data = self.__data_deal.int_2_list(int(adc_dec_param),2)
        self.__axi4lite.write(0x20,wr_data,2)
        wr_data = self.__data_deal.int_2_list(int(p_param*pow(2,17)),3)
        self.__axi4lite.write(0x24,wr_data,3)
        wr_data = self.__data_deal.int_2_list(int(i_param*pow(2,17)),3)
        self.__axi4lite.write(0x28,wr_data,3)
        wr_data = self.__data_deal.int_2_list(int(d_param*pow(2,17)),3)
        self.__axi4lite.write(0x2C,wr_data,3)
        wr_data = self.__data_deal.int_2_list(int(pwm0_duty*624),2)
        self.__axi4lite.write(0x30,wr_data,2)
        wr_data = self.__data_deal.int_2_list(int(pwm1_duty*624),2)
        self.__axi4lite.write(0x34,wr_data,2)
        wr_data = self.__data_deal.int_2_list(int(pwm_minimum_duty*624),2)
        self.__axi4lite.write(0x40,wr_data,2)
        wr_data = self.__data_deal.int_2_list(int(pwm_maximum_duty*624),2)
        self.__axi4lite.write(0x44,wr_data,2)
        wr_data = self.__data_deal.int_2_list(int(pwm_error_duty*624),2)
        self.__axi4lite.write(0x48,wr_data,2)
        
        # # start pwm
        # self.__axi4lite.write(0x11,[0x01],1)
        # cfg mode info
        wr_data = 0x01 | pwm_mode<<4 | pid_en<<5;
        self.__axi4lite.write(0x10, [wr_data], 1)
        return None
    
