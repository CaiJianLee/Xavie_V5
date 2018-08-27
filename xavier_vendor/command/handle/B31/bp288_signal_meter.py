#-*- coding: UTF-8 -*-

import re
import time
import sys
import command.server.handle_utility as Utility
from ee.common import logger
from collections import OrderedDict
from ee.common import xavier as Xavier1
sys.path.append('/opt/seeing/app/')
from b31_bp import xavier1 as Xavier2

global agv
agv=sys.argv[1]
Xavier=Xavier1
xavier_module = {"tcp:7801":Xavier1, "tcp:7802":Xavier2}
if agv in xavier_module:
    Xavier=xavier_module[agv]
    
test_base_board_name="zynq"

protectwavemeasure_channel=["psu1_ocp","psu1_ovp","psu2_ocp","psu2_ovp","psu3_ocp","psu3_ovp" ]
protectwavemeasure_help=""
for i  in protectwavemeasure_channel:
    protectwavemeasure_help+=i+" , "
protectwavemeasure_help=protectwavemeasure_help[:-2]

wave_measure_start=["PSU1_LIMIT","PSU1_Voltage","PSU2_LIMIT","PSU2_Voltage",
                      "PSU3_LIMIT","PSU3_Voltage","PSU1_OCP","PSU1_OVP","PSU2_OCP","PSU2_OVP",
                      "PSU3_OCP","PSU3_OVP" ]  
wave_measure_start_help=""
for i  in wave_measure_start:
    wave_measure_start_help+=i+" , "
wave_measure_start_help=wave_measure_start_help[:-2]
wave_measure_stop=["PSU1_OCP","PSU1_OVP","PSU2_OCP","PSU2_OVP",
             "PSU3_OCP","PSU3_OVP" ]  
wave_measure_stop_help=""
for i  in wave_measure_stop:
    wave_measure_stop_help+=i+" , "
wave_measure_stop_help=wave_measure_stop_help[:-2]

# @Utility.timeout(11)
# def audio_measure_handle(params):
#     help_info = "audio measure({<band>}{<timeout>})$\r\n\
# \tband:(24-95977)Hz,default 20000Hz$\r\n\
# \ttimeout: (1-10000) ms measure timeout time,default 3000 ms.$\r\n"
#     
#     '''  init information '''
#     band = 20000
#     timeout = 3000
#     
#     ''' help '''
#     if Utility.is_ask_for_help(params) is True:
#         return Utility.handle_done(help_info)
#     '''  params analysis '''
#     param_count = len(params)
#     if (param_count !=2):
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error") 
#     band=int(params[0],10)  
#     timeout = int(params[1],10)
#     if band < 24 or band > 95977:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param band error")
#     if timeout < 1 or timeout > 10000:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param timeout error")
#     '''doing'''
#     ret=Xavier.call("eval",test_base_board_name,"audio_measure",band,timeout)
#     if ret is False:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "audio measure fail ")   
#     return Utility.handle_done()

@Utility.timeout(5)
def audio_datalogger_open_handle(params):
    help_info = "audio datalogger open()$\r\n"   
    '''  init information '''  

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=0):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error") 
    '''doing'''
    ret=Xavier.call("eval",test_base_board_name,"audio_datalogger_open")
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "audio datalogger open  fail ")   
    return Utility.handle_done()

@Utility.timeout(5)
def audio_datalogger_close_handle(params):
    help_info = "audio datalogger close()$\r\n"   
    '''  init information '''  
    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    '''doing'''
    ret=Xavier.call("eval",test_base_board_name,"audio_datalogger_close")
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "audio measure fail ")   
    return Utility.handle_done()

@Utility.timeout(11)
def frequency_measure_handle(params):
    help_info = "frequency measure({-option},{<measure_time>}})$\r\n\
\toption:(o,d,f)$\r\n\
\t    d:duty$\r\n\
\t    f:frequency$\r\n\
\t    default: option = f$\r\n\
\tmeasure time:(1-4000)ms,default 300ms$\r\n"
    #\t    v:vpp$\r\n\
    '''  init information '''
    duty = False
    frequency = False
    frequency_value = []
    measure_time = 300
    timeout = 5000 / 10   #5000 ms
    base_param_index = 0
    sample_rate = 125000000
    duty_measure = False
    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count > 2) or(param_count<1):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    
    option= params[base_param_index]
    if option[base_param_index] == '-':
        for index in range(1, len(option)):
            if option[index] == 'd':
                duty_measure =True
            elif option[index] == 'f':
                frequency = True
#           elif option[index] == 'v':
#               amplitude = True
            else:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
        base_param_index = 1
    else:
        frequency = True

    for index in range(base_param_index, param_count):
        if index == base_param_index :
            measure_time = int(params[index],10)
            if measure_time < 1 or measure_time > 4000:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
        else :
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    '''doing'''
    ret=Xavier.call("eval",test_base_board_name,"frequency_measure",'freq',measure_time,sample_rate)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    output_message=''
    # logger.error(str(ret))
    if frequency is  True:
        output_message = output_message + str(round(ret['fre'][0],2)) + ' Hz'
    if duty_measure is  True:
        if frequency is  True:
            output_message = output_message + ','
        output_message = output_message + str(round(ret['duty'],2)) + ' %'
    
    return Utility.handle_done(output_message)

# @Utility.timeout(11)
# def ppulse_measure_handle(params):
#     help_info = "frequency measure(<measure_time>})$\r\n\
# \tmeasure time:(1-4000)ms,default 300ms$\r\n"
#     #\t    v:vpp$\r\n\
#     '''  init information '''
#     frequency_value = []
#     measure_time = 300
#     timeout = 5000 / 10   #5000 ms
#     sample_rate = 125000000
#     duty_measure = False
#     ''' help '''
#     if Utility.is_ask_for_help(params) is True:
#         return Utility.handle_done(help_info)
#     
#     '''  params analysis '''
#     param_count = len(params)
#     if (param_count !=1):
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")   
#     measure_time = int(params[0],10)
#     if measure_time < 1 or measure_time > 4000:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
#     '''doing'''
#     ret=Xavier.call("eval",test_base_board_name,"frequency_measure",'ppulse',measure_time,sample_rate)
#     if ret is False:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
#     if ret['fre'][0]==0:
#         return Utility.handle_done(" 0nS")
#     ppulse_wide=1.0/ret['fre'][0]*ret['duty']*10000000
#     output_message =str( ppulse_wide)+"nS"  
#     return Utility.handle_done(output_message)

@Utility.timeout(11)
def delay_measure_handle(params):
    help_info = "delay time measure{<channel>,<mesure_time>})$\r\n\
\tchannel :(ppulse)$\r\n\
\tmeasure time:(1-30000)ms,default 300ms$\r\n\
"
    #\t    v:vpp$\r\n\
    '''  init information '''
    frequency_value = []
    measure_time = 300
    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=2):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")   
    measure_time = int(params[1],10)
    if measure_time < 1 or measure_time > 30000:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param measure time error")
    '''doing'''
    channel = params[0]  
    if channel !='psu1' and  channel !='psu2' and channel !='psu3'  and channel !='ppulse' :
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")        
    ret=Xavier.call("eval",test_base_board_name,"delay_time_measure",channel,measure_time)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    output_message = str(ret[1])+"uS"  
    return Utility.handle_done(output_message)

@Utility.timeout(11)
def protectwavemeasure_handle(params):
    help_info = "protect wave measure{<channel>,<mesure_time>})$\r\n\
\tchannel :("+protectwavemeasure_help+")\r\n\
\tmeasure time:(1-30000)ms,default 300ms$\r\n\
"
    #\t    v:vpp$\r\n\
    '''  init information '''
    measure_time = 300
    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=2):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")   
    measure_time = int(params[1],10)
    if measure_time < 1 or measure_time > 30000:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param measure time error")
    '''doing'''
    channel = params[0]  
    if channel not in protectwavemeasure_channel :
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")        
    ret=Xavier.call("eval",test_base_board_name,"protectwavemeasure_fun",channel,measure_time)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    output_message = str(ret[1])+"uS"  
    return Utility.handle_done(output_message)

@Utility.timeout(11)
def wave_measure_start_handle(params):
    help_info = "wave measure start(<start_select><stop_select>)\r\n\
    \t start_select:("+wave_measure_start_help+")\r\n\
    \t stop_select:("+wave_measure_stop_help+")\r\n"
    #\t    v:vpp$\r\n\
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=2):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")   
    start_select = params[0]  
    if start_select not in wave_measure_start :  
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param start_select error")
    stop_select = params[1]  
    if stop_select not in wave_measure_stop :  
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param stop_select error")
    ret=Xavier.call("eval",test_base_board_name,"wave_measure_start",start_select,stop_select)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    return Utility.handle_done()

@Utility.timeout(11)
def wave_measure_get_handle(params):
    help_info = "wave measure get{<timeout>})$\r\n\
\t timeout:(1-3000)ms\r\n\
"
    #\t    v:vpp$\r\n\
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=1):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")  
    measure_time = int(params[0],10)
    if measure_time < 1 or measure_time > 3000:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param measure time error")
    '''doing'''        
    ret=Xavier.call("eval",test_base_board_name,"wave_measure_get",measure_time)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    output=str(ret[1])+'uS'
    return Utility.handle_done(output)

@Utility.timeout(11)
def protect_flag_status_handle(params):
    help_info = "protect flag{<channel>,<gpio>})$\r\n\
\tchannel :(psu1,psu2,psu3)$\r\n\
\tgpio:(ocp,ovp)$\r\n\
"

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if (param_count !=2):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")   
    
    channel = params[0]  
    if channel !='psu1' and  channel !='psu2' and channel !='psu3':
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")   
    gpio_name = params[1]
    if gpio_name !='ocp' and  gpio_name !='ovp' :
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param gpio name  error")
    '''doing'''     
    ret=Xavier.call("eval",test_base_board_name,"protect_flag_status",channel,gpio_name)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'], "get value fail ")
    output_message =gpio_name+'=' +str(ret[0][1]) 
    return Utility.handle_done(output_message)
