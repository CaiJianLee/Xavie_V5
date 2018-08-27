from __future__ import division
from ee.bus.axi4lite import Axi4lite
from ee.common import logger
from ee.common.data_operate import DataOperate

__version__ = '1.0.0'

class Axi4Gpio(object):
    def __init__(self,name):
        self.name = name
        self.reg_num = 256
        self.__axi4lite=Axi4lite(self.name,self.reg_num)   
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))   
        self.__data_deal = DataOperate()
        
    def reset(self):
        """  All gpio reset to 0        """  
        wr_data = [0x00,0x00,0x00,0x00,0xFF,0xFF,0xFF,0xFF]
        reg_addr = 0x10
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))
        reg_addr = 0x20
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))
        reg_addr = 0x30
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))
        reg_addr = 0x40
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))
        
    def gpio_set(self,gpio_out):
        """ set gpio level
            
            Args:
                gpio_out(list): the unit of list is (gpio_number,gpio_level)
                                gpio_number for 0 to 127
                                set gpio_level to 1, the gpio output high level
                                set gpio_level to 0, the gpio output low level
            Returns:
                NONE
        """         
        ch0_data = []
        ch1_data = []
        ch2_data = []
        ch3_data = []
        for gpio_out_temp in gpio_out:
            gpio_out_temp = list(gpio_out_temp)
            if(gpio_out_temp[0] < 32):
                ch0_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 64):
                gpio_out_temp[0] = gpio_out_temp[0]-32
                ch1_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 96):
                gpio_out_temp[0] = gpio_out_temp[0]-64
                ch2_data.append(gpio_out_temp)
            else:
                gpio_out_temp[0] = gpio_out_temp[0]-96
                ch3_data.append(gpio_out_temp)
        if(len(ch0_data) >0):
            self._gpio_output_set('ch0',ch0_data)
        if(len(ch1_data) >0):
            self._gpio_output_set('ch1',ch1_data)
        if(len(ch2_data) >0):
            self._gpio_output_set('ch2',ch2_data)    
        if(len(ch3_data) >0):
            self._gpio_output_set('ch3',ch3_data)    
        return None
        
    def gpio_ctrl(self,gpio_ctrl):   
        """ set gpio to input or output
            
            Args:
                gpio_ctrl(list): the unit of list is (gpio_number,gpio_ctrl)
                                gpio_number for 0 to 127
                                set gpio_ctrl to 1, the gpio is set to input
                                set gpio_ctrl to 0, the gpio is set to output
            Returns:
                NONE
        """             
        ch0_data = []
        ch1_data = []
        ch2_data = []
        ch3_data = []
        for gpio_out_temp in gpio_ctrl:
            gpio_out_temp = list(gpio_out_temp)
            if(gpio_out_temp[0] < 32):
                ch0_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 64):
                gpio_out_temp[0] = gpio_out_temp[0]-32
                ch1_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 96):
                gpio_out_temp[0] = gpio_out_temp[0]-64
                ch2_data.append(gpio_out_temp)
            else:
                gpio_out_temp[0] = gpio_out_temp[0]-96
                ch3_data.append(gpio_out_temp)
        if(len(ch0_data) >0):
            self._gpio_ctrl_set('ch0',ch0_data)
        if(len(ch1_data) >0):
            self._gpio_ctrl_set('ch1',ch1_data)
        if(len(ch2_data) >0):
            self._gpio_ctrl_set('ch2',ch2_data)        
        if(len(ch3_data) >0):
            self._gpio_ctrl_set('ch3',ch3_data)    
        return None
    
    def gpio_get(self,gpio_input,gpio_type='in'):
        """ get gpio state
            
            Args:
                gpio_input(list)        :   the unit of list is (gpio_number,gpio_level)
                                            gpio_number for 0 to 127
                                            set gpio_level to 255
                gpio_type(str)          :   select the gpio type
                                            'in'  --- select input gpio
                                            'out' --- select output gpio
            Returns:
                gpio_input_data(list)   :   the unit of list is (gpio_number,gpio_level)
                                            gpio_number for 0 to 127
                                            when gpio is high level, the gpio_level is 1
                                            when gpio is low level, the gpio_level is 0
        """         
        ch0_data = []
        ch1_data = []
        ch2_data = []
        ch3_data = []
        for gpio_out_temp in gpio_input:
            gpio_out_temp = list(gpio_out_temp)         
            if(gpio_out_temp[0] < 32):
                ch0_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 64):
                gpio_out_temp[0] = gpio_out_temp[0]-32
                ch1_data.append(gpio_out_temp)
            elif(gpio_out_temp[0] < 96):
                gpio_out_temp[0] = gpio_out_temp[0]-64
                ch2_data.append(gpio_out_temp)
            else:
                gpio_out_temp[0] = gpio_out_temp[0]-96
                ch3_data.append(gpio_out_temp)
        gpio_input_data = []
        if(len(ch0_data) >0):
            ch0_data_get = self._gpio_input_get('ch0',ch0_data)
            gpio_input_data.extend(ch0_data_get)
        if(len(ch1_data) >0):
            ch1_data_get = self._gpio_input_get('ch1',ch1_data)
            gpio_input_data.extend(ch1_data_get)
        if(len(ch2_data) >0):
            ch2_data_get = self._gpio_input_get('ch2',ch2_data)
            gpio_input_data.extend(ch2_data_get)
        if(len(ch3_data) >0):
            ch3_data_get = self._gpio_input_get('ch3',ch3_data)
            gpio_input_data.extend(ch3_data_get)            
        return gpio_input_data 
 
    def _gpio_output_set(self,gpio_channel,gpio_out):
        if(gpio_channel == 'ch0'):
            reg_addr = 0x10
        elif(gpio_channel == 'ch1'):
            reg_addr = 0x20
        elif(gpio_channel == 'ch2'):
            reg_addr = 0x30
        elif(gpio_channel == 'ch3'):
            reg_addr = 0x40  
        else:
            logger.error('@%s:    GPIO Channel set rror'%(self.name))
            return False
        rd_data = self.__axi4lite.read(reg_addr,4)
        reg_data_int = self.__data_deal.list_2_int(rd_data)
        if(reg_data_int < 0):
            reg_data_int = reg_data_int + pow(2,32)
        reg_data_int_shift = reg_data_int
        for gpio_out_temp in gpio_out:
            reg_data_int_shift = self.__data_deal.cyclic_shift('R', reg_data_int_shift, 32, gpio_out_temp[0])
            if(gpio_out_temp[1] == 1):
                reg_data_int_shift = reg_data_int_shift & 0xFFFFFFFE | 0x00000001
            elif(gpio_out_temp[1] == 0):
                reg_data_int_shift = reg_data_int_shift & 0xFFFFFFFE
            else:
                logger.error('@%s:    GPIO output set error'%(self.name))
                return False  
            reg_data_int_shift = self.__data_deal.cyclic_shift('L', reg_data_int_shift, 32, gpio_out_temp[0])
        wr_data = self.__data_deal.int_2_list(reg_data_int_shift, 4)
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))

    def _gpio_ctrl_set(self,gpio_channel,gpio_ctrl):
        if(gpio_channel == 'ch0'):
            reg_addr = 0x14
        elif(gpio_channel == 'ch1'):
            reg_addr = 0x24
        elif(gpio_channel == 'ch2'):
            reg_addr = 0x34
        elif(gpio_channel == 'ch3'):
            reg_addr = 0x44  
        else:
            logger.error('@%s:    GPIO Channel set error'%(self.name))
            return False
        rd_data = self.__axi4lite.read(reg_addr,4)
        reg_data_int = self.__data_deal.list_2_int(rd_data)
        if(reg_data_int < 0):
            reg_data_int = reg_data_int + pow(2,32)
        reg_data_int_shift = reg_data_int
        for gpio_ctrl_temp in gpio_ctrl:
            reg_data_int_shift = self.__data_deal.cyclic_shift('R', reg_data_int_shift, 32, gpio_ctrl_temp[0])
            if(gpio_ctrl_temp[1] == 1):
                reg_data_int_shift = reg_data_int_shift & 0xFFFFFFFE | 0x00000001
            elif(gpio_ctrl_temp[1] == 0):
                reg_data_int_shift = reg_data_int_shift & 0xFFFFFFFE
            else:
                logger.error('@%s:    GPIO control set error'%(self.name))
                return False        
            reg_data_int_shift = self.__data_deal.cyclic_shift('L', reg_data_int_shift, 32, gpio_ctrl_temp[0])
        wr_data = self.__data_deal.int_2_list(reg_data_int_shift, 4)
        self.__axi4lite.write(reg_addr, wr_data, len(wr_data))
  
        
    def _gpio_input_get(self,gpio_channel,gpio_input,gpio_type='in'):
        if(gpio_type == 'in'):
            if(gpio_channel == 'ch0'):
                reg_addr = 0x18
            elif(gpio_channel == 'ch1'):
                reg_addr = 0x28
            elif(gpio_channel == 'ch2'):
                reg_addr = 0x38
            elif(gpio_channel == 'ch3'):
                reg_addr = 0x48  
            else:
                logger.error('@%s:    GPIO Channel set error'%(self.name))
                return False
        else:
            if(gpio_channel == 'ch0'):
                reg_addr = 0x10
            elif(gpio_channel == 'ch1'):
                reg_addr = 0x20
            elif(gpio_channel == 'ch2'):
                reg_addr = 0x30
            elif(gpio_channel == 'ch3'):
                reg_addr = 0x40  
            else:
                logger.error('@%s:    GPIO Channel set error'%(self.name))
                return False            
        rd_data = self.__axi4lite.read(reg_addr,4)
        reg_data_int = self.__data_deal.list_2_int(rd_data)
        if(reg_data_int < 0):
            reg_data_int = reg_data_int + pow(2,32)
        if(len(gpio_input) > 32):
            logger.error('@%s:    GPIO number set error'%(self.name))
            return False
        for gpio_input_index in range(0,len(gpio_input)):
            reg_data_int_shift = self.__data_deal.cyclic_shift('R', reg_data_int, 32, gpio_input[gpio_input_index][0])
            if((reg_data_int_shift & 0x00000001) == 0x00000001):
                gpio_input[gpio_input_index] = (gpio_input[gpio_input_index][0],1)
            else:
                gpio_input[gpio_input_index] = (gpio_input[gpio_input_index][0],0)
            reg_data_int_shift = self.__data_deal.cyclic_shift('L', reg_data_int, 32, gpio_input[gpio_input_index][0])
        return gpio_input 
    
            
        
            
