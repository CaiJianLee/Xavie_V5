import os
import time
import commands

class SeGpioFaultError(Exception):
    pass

class GPIO():
    ''' gpio_direction:out,in, high, low, gpio_value:1--> high, 0-->low '''
    def __init__(self, gpio_num, gpio_dir):
        self.gpio_num = gpio_num
        self._gpio_dir = gpio_dir
        self.__write_export()
        self.write_diretion(gpio_dir)
        
    def __del__(self):
        self.__write_unexport()
        
    def __write_export(self):
        gpiostr = "echo " + str(self.gpio_num) + " > /sys/class/gpio/export"
        if os.system(gpiostr):
            raise SeGpioFaultError()
    
    def __write_unexport(self):
        gpiostr = "echo " + str(self.gpio_num) + " > /sys/class/gpio/unexport"
        os.system(gpiostr)
        
    def write_diretion(self, gpiodir):
        gpiostr = "echo " + str(gpiodir) +" > /sys/class/gpio/gpio" + str(self.gpio_num) + "/direction"
        os.system(gpiostr)
    
    def read_diretion(self):
        gpiostr = "cat /sys/class/gpio/gpio" + str(self.gpio_num) + "/direction"
        return commands.getoutput(gpiostr)
        
    def write_value(self, value):
        gpiostr = "echo " + str(value) +" > /sys/class/gpio/gpio" + str(self.gpio_num) + "/value"
        os.system(gpiostr)
        
    def read_value(self):
        gpiostr = "cat /sys/class/gpio/gpio" + str(self.gpio_num) + "/value"
        return commands.getoutput(gpiostr)