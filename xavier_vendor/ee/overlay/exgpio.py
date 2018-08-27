#-*- coding: UTF-8 -*-
import ee.common.utility as Utility
from ee.common import logger
from ee.ipcore.axi4_gpio import Axi4Gpio
__author__='zhenhua'


def set(device_name, gpio_out):
    """ set gpio level
        
        Args:
            device_name: str type, device name.
            gpio_out(list): the unit of list is (gpio_number,gpio_level)
                            gpio_number for 0 to 127
                            set gpio_level to 1, the gpio output high level
                            set gpio_level to 0, the gpio output low level
        Returns:
            Success return NONE,
            False otherwise.
        eg:
          Set the gpio2 a value of 0(output):
            set("XAI$_GPIO",((2,0),))  
          Set the gpio2 gpio3 a value of 0(output):
            set("XAI$_GPIO",((2,0),(3,0)))
    """         
    try:
        path=Utility.get_dev_path() + '/' + device_name
        gpio_device=Axi4Gpio(path)
        return gpio_device.gpio_set(gpio_out)
    except Exception as e:
        logger.error("error: gpio set False:" + repr(e))
        return False
        
def get(device_name, gpio_input):
    """ get gpio state
        
        Args:
            device_name: str type, device name.
            gpio_input(list)        :   the unit of list is (gpio_number,gpio_level)
                                        gpio_number for 0 to 127
                                        set gpio_level to 255
        Returns:
            success return gpio_input_data(list)   :   the unit of list is (gpio_number,gpio_level)
                                        gpio_number for 0 to 127
                                        when gpio is high level, the gpio_level is 1
                                        when gpio is low level, the gpio_level is 0
            False otherwise.
    """   
    try:
        path=Utility.get_dev_path() + '/' + device_name
        gpio_device=Axi4Gpio(path)
        return gpio_device.gpio_get(gpio_input)
    except Exception as e:
        logger.error("error: gpio get False:" + repr(e))
        return False
    
def dir_set(device_name, gpio_ctrl):
    """ set gpio to input or output
        
        Args:
            device_name: str type, device name.
            gpio_ctrl(list): the unit of list is (gpio_number,gpio_ctrl)
                            gpio_number for 0 to 127
                            set gpio_ctrl to 1, the gpio is set to input
                            set gpio_ctrl to 0, the gpio is set to output
        Returns:
            Success return NONE,
            False otherwise.
        eg:
          Set the direction of the gpio2 to 0(output):
            dir_set("XAI$_GPIO",((2,0),))  
          Set the direction of the gpio2 gpio3 to 0(output):
            dir_set("XAI$_GPIO",((2,0),(3,0)))
    """   
    try:
        path=Utility.get_dev_path() + '/' + device_name
        gpio_device=Axi4Gpio(path)
        return gpio_device.gpio_ctrl(gpio_ctrl)
    except Exception as e:
        logger.error("error: gpio dir set False:" + repr(e))
        return False