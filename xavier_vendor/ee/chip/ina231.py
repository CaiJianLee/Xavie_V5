#from __future__ import division
import time
import copy
from ee.ipcore.axi4_iic import Axi4I2c
from ee.common import logger
from ee.profile.profile import Profile
from ee.ipcore.axi4_gpio import Axi4Gpio
import ctypes
import time
__version__="1.0"

average_times={
               1:0x0,4:0x1,16:0x2,64:0x3,128:0x4,256:0x5,512:0x6,1024:0x7,
               }
conversion_times={
               140:0x0,204:0x1,332:0x2,588:0x3,1100:0x4,2116:0x5,4156:0x6,8244:0x7,
               }

mode={"Power_down":0x0,"Shunt_voltage_triggered":0x1,"Bus voltage, triggered":0x2,"Bus_voltage_triggered":0x3,
      "Shunt_and_bus_triggered":0x4,"Power_down":0x5,"Bus_voltage_continuous":0x6,"Shunt_and_bus_continuous":0x7,
      }

class INA231(object):
    def __init__(self,iic_bus,addr):
        self.device = Axi4I2c(iic_bus)
        self.device.config(100000)
        self.addr=addr
    def register_read(self,reg_addr):
        write_content=[reg_addr,]     
        return self.device.rdwr(self.addr,write_content,2);
    
    def register_write(self,reg_addr,reg_data):
        write_content=[]
        write_content.append(reg_addr)
        write_content+=reg_data
        return self.device.write(self.addr,write_content)
    
    def average_set(self,times):
        temp=self.register_read(0)
        temp[0]=((temp[0]&0x7f)&0xf1)|(times<<1)
        return self.register_write(0,temp)
    
    def bus_conversion_time_set(self,conv_time):
        temp=self.register_read(0)
        temp[0]=((temp[0]&0x7f)&0xfe)|(conv_time>>2)
        temp[1]=(temp[1]&0x3f)|((conv_time&0xfb)<<6)
        return self.register_write(0,temp)
    
    def shunt_conversion_time_set(self,conv_time):
        temp=self.register_read(0)
        temp[0]=temp[0]&0x7f
        temp[1]=(temp[1]&0xc7)|(conv_time<<3)
        return self.register_write(0,temp)
    def conversion_mode_set(self,conv_mode):
        temp=self.register_read(0)
        if temp is False:
            return False
        temp[0]=temp[0]&0x7f
        temp[1]=(temp[1]&0xf8)|mode[conv_mode]
        return self.register_write(0,temp)  
    
    def conversion_ready_flag(self):
        ret=self.register_read(6)
        if ret is False:
            return False
        flag=ret[1]&0x08
        if flag !=0:
            return True
        else:
            return False
        
    def shun_voltage_list_to_value(self,vdata):
        temp=(vdata[0]<<8)|vdata[1]
        shunt_value1=ctypes.c_int16(temp).value
        shunt_value=shunt_value1*2.5
        return shunt_value
    
    def bus_voltage_list_to_value(self,vdata):
        temp=(vdata[0]<<8)|vdata[1]
        shunt_value1=ctypes.c_int16(temp).value
        shunt_value=shunt_value1*1.25
        return shunt_value
        
            
    def shunt_and_bus_voltage_read(self,res):
        self.conversion_mode_set('Shunt_and_bus_triggered')
        shunt_voltage=0
        bus_voltage=0
        for i in range(1000):
            if self.conversion_ready_flag() is True:
                break
            if i==1000:
                return False
        ret=self.register_read(1)
        if ret is False:
            return False
        shunt_v=self.shun_voltage_list_to_value(ret)
        if shunt_v is False:
            return False
        shunt_curent=shunt_v/res*1000           
        ret=self.register_read(2)
        if ret is False:
            return False
        bus_v=self.bus_voltage_list_to_value(ret)
        return [shunt_curent,bus_v]
                
            
            

        
    

    
    
