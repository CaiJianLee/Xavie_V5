#-*- coding: UTF-8 -*-
import re
import time
import sys
import command.server.handle_utility as Utility
from ee.common import logger
from ee.common import xavier as Xavier1
sys.path.append('/opt/seeing/app/')
from b31_bp import xavier1 as Xavier2

global agv
agv=sys.argv[1]
Xavier=Xavier1
xavier_module = {"tcp:7801":Xavier1, "tcp:7802":Xavier2}
if agv in xavier_module:
    Xavier=xavier_module[agv]
    
test_base_board_name = "zynq"

global batt_value
batt_value={"current":1,"voltage":1,}#current unit mA,mV

global vbus_value
vbus_value={"current":1,"voltage":1,}#current unit mA,mV

dac_list=[ "psu1_ocp" , "psu1_ovp",  "psu1_ocp_ad5601" , "psu1_ovp_ad5601", "psu1_current",  "psu1_voltage",
           "psu2_ocp", "psu2_ovp","psu2_ocp_ad5601", "psu2_ovp_ad5601","psu2_current", "psu3_ocp","psu3_ocp_ad5601","psu3_ovp", "psu2_voltage","psu3_ovp_ad5601",  "psu3_current" ,"psu3_voltage", "base_board"]
help_str=''
for i in dac_list:
    help_str=help_str+i+',\r\n\t    '

# global calibration_var  
# def _calibration_init():
#     global calibration_var  
#     """从eeprom读取数据的程序"""
# _calibration_init()#这个函数模块一
#      

def dac_voltage_set_handle(params):
    help_info = "dac set(<channel>,<value>)$\r\n\
    \t channel("+help_str+")\tvalue: (if ad5761: (0~10000)  unit:mv,else :(0~5000)  unit:mv) $\r\n"
    ''' params init '''    
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
 
    ''' parametr analysis '''
    if len(params)!=2:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],\
                                    "param length error" )        
    channel=params[0]
    if channel not in dac_list:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "channel parameter error" )         
    volt_value=float(params[1])
    if channel=="psu3_voltage" or channel=="psu2_voltage" :
        if volt_value<0 or volt_value>10000:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],\
                                    "param voltage value error" + str(volt_value))   
    elif channel=="base_board" :
        if volt_value<0 or volt_value>3300:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],\
                                    "param voltage value error" + str(volt_value))   
    else:
        if volt_value<0 or volt_value>5000:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],\
                                    "param voltage value error" + str(volt_value))   
    ret=Xavier.call("eval",test_base_board_name,"voltage_set",channel,volt_value)
    if ret==False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")    
    return Utility.handle_done()
def dac_5761_write_register_handle(params):
    help_info = "ad5761 register write(<addr>,<data>)$\r\n\
    \t addr:register address $\r\n\
    \t data:2byte data\r\n"
    ''' params init '''    
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
 
    ''' parametr analysis '''
    if len(params)!=2:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],\
                                    "param length error" )        
    addr=int(params[0],16)      
    data=int(params[1],16) 
    ret=Xavier.call("eval",test_base_board_name,"ad5761_write_register",addr,data)
    if ret==False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")    
    return Utility.handle_done()
