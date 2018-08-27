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

average_times={
               1:0x0,4:0x1,16:0x2,64:0x3,128:0x4,256:0x5,512:0x6,1024:0x7,
               }
conversion_times={
               140:0x0,204:0x1,332:0x2,588:0x3,1100:0x4,2116:0x5,4156:0x6,8244:0x7,
               }
average_times_info=''
for key in average_times.keys():
    average_times_info+=str(key)+','
conversion_times_info=''    
for key in conversion_times.keys():
    conversion_times_info+=str(key)+','
    
ina231_channel={'psu1':"psu1_ina231",'psu2':"psu2_ina231",'psu3':"psu1_ina231", }

@Utility.timeout(5)
def ina231_register_read_handle(params):
    help_info = "ina231 register read(<channel>,<addr>)$\r\n\
    \tchannel:(psu1,psu2,psu3)"
    ''' params init '''
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
  
    ''' parametr analysis '''
    params_count = len(params)
    if params_count !=2:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param length error" ) 
    channel=params[0] 
    if channel not  in ina231_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param channel error" ) 
    addr=int(params[1],16)
    ret=Xavier.call("eval",test_base_board_name,"ina231_register_read",ina231_channel[channel],addr)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")
    output_str=str(ret)
    return Utility.handle_done(output_str)

@Utility.timeout(5)
def ina231_register_write_handle(params):
    help_info = "ina231 register write(<channel>,<addr>,<data1>,<data2>)$\r\n\
    \tchannel :(psu1,psu2,psu3)\r\n"
    ''' params init '''
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)    
    ''' parametr analysis '''
    params_count = len(params)
    if params_count !=4:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param length error" )  
    channel=params[0]
    if channel not  in ina231_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param channel error" )      
    addr=int(params[1],16)
    write_content=[]
    write_content.append(int(params[2],16))
    write_content.append(int(params[3],16))
    ret=Xavier.call("eval",test_base_board_name,"ina231_register_write",ina231_channel[channel],addr,write_content)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")
    output_str=str(ret)
    return Utility.handle_done()

@Utility.timeout(5)
def ina231_voltage_read_handle(params):
    help_info = "ina231 voltage read(<channel>,<sample_res>)$\r\n\
        \tchannel :(psu1,psu2,psu3)\r\n\
        \tsample_res: sample_register "
    ''' params init '''
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
  
    ''' parametr analysis '''
    params_count = len(params)
    if params_count !=2:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param length error" )      
    channel=params[0]
    if channel not  in ina231_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param channel error" )      
    res=float(params[1])
    ret=Xavier.call("eval",test_base_board_name,"shunt_and_bus_voltage_read",ina231_channel[channel],res)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")
    output_str=str(ret[0])+"mA"+str(ret[1])+"mV"
    return Utility.handle_done(output_str)

@Utility.timeout(5)
def ina231_config_handle(params):
    help_info = "ina231 config(<channel>,<average>,<vbus_conversion_time>,<shunt_conversion_time>)$\r\n\
    \t average("+average_times_info+"us)\r\n\
    \tvbus_conversion_time: ("+average_times_info+"us)\r\n\
    \tshunt_conversion_time: ("+conversion_times_info+"us)\r\n"
    ''' params init '''
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
  
    ''' parametr analysis '''
    params_count = len(params)
    if params_count !=4:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param length error" ) 
    channel=params[0]
    if channel not  in ina231_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param channel error" )      
    average=int(params[1])
    vbus_conversion_time=int(params[2])
    shunt_conversion_time=int(params[3])
    if average  not in average_times   :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param average error" ) 
        
    if vbus_conversion_time  not in conversion_times   :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param vbus_conversion_time error" ) 
        
    if shunt_conversion_time  not in conversion_times   :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param shunt_conversion_time error" )    
    ret=Xavier.call("eval",test_base_board_name,"ina231_config",ina231_channel[channel],average,vbus_conversion_time,shunt_conversion_time)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")
    return Utility.handle_done()
     
