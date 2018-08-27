#-*- coding: UTF-8 -*-
__author__ = 'zhiwei.deng'
 
import re
import time
import sys
from ee.common import logger
import command.server.handle_utility as Utility

from ee.common import xavier as Xavier1
sys.path.append('/opt/seeing/app/')
from b31_bp import xavier1 as Xavier2

global agv
agv=sys.argv[1]
Xavier=Xavier1
xavier_module = {"tcp:7801":Xavier1, "tcp:7802":Xavier2}
if agv in xavier_module:
    Xavier=xavier_module[agv]
    
global datalogger_board_name
datalogger_board_name="pbdatalogger"

adc_channel={"chanA":'current',"chanB":"voltage"}
@Utility.timeout(1)
def datalogger_open_handle(params):

    help_info = "datalogger open({<channel>,<mode>})$\r\n\
    \tchannel=(chanA,chanB)\r\n\
    \tmode=(ADC_MASTER,ADC_NORMAL),default ADC_NORMAL$\r\n"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    ''' params analysis '''
    params_count = len(params)
    if params_count != 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    channel = params[0]
    if channel not in ["volt1","volt2","all"]:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")   

    ''' doing '''
    global datalogger_board_name
    if mode == "ADC_MASTER" :
        ''' close '''
        result = Xavier.call('eval',datalogger_board_name,'datalogger_close')
    else:
        ''' open '''
        result = Xavier.call('eval',datalogger_board_name,'datalogger_open',adc_channel[channel])

    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    

    return Utility.handle_done() 

@Utility.timeout(20)
def audio_upload_handle(params):

    help_info = "audio upload(measure_time)$\r\n\
    \tmeasure_time:set audio measure time:(1~2000ms)"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    ''' params analysis '''
    params_count = len(params)
     
    if params_count  !=1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
        result = Xavier.call('eval',datalogger_board_name,'datalogger_close')
    measure_time = int(params[0])
    if    measure_time<1 or measure_time>2000 :
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param measure time  error")       
        ''' open '''
    result = Xavier.call('eval',datalogger_board_name,'audio_upload',measure_time)
    result = Xavier.call('eval',datalogger_board_name,'datalogger_close')
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")  
    return Utility.handle_done() 


@Utility.timeout(1)
def datalogger_close_handle(params):

    help_info = "datalogger close()\r\n"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    ''' params analysis '''
    params_count = len(params)
     
    if params_count != 0:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")


    ''' doing '''
    global datalogger_board_name

    result = Xavier.call('eval',datalogger_board_name,'datalogger_close')

    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    

    return Utility.handle_done() 



@Utility.timeout(1)
def datalogger_reset_handle(params):

    help_info = "datalogger reset()\r\n"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    ''' params analysis '''
    params_count = len(params)
     
    if params_count != 0:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")


    ''' doing '''
    global datalogger_board_name

    result = Xavier.call('eval',datalogger_board_name,'datalogger_reset')

    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    

    return Utility.handle_done() 

@Utility.timeout(1)
def datalogger_samplerate_set_handle(params):

    help_info = "datalogger samplerate set(<channel>, <samplerate>)$\r\n\
            \tchannel:(chanA,chanB) \r\n\
            \tsamplerate:(value)"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''parameters analysis'''
    params_count = len(params)
    if params_count  != 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    channel=params[0]
    samplerate=int(params[1])
    if channel !="chanA" and channel !="chanB":
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")      
    global datalogger_board_name
    result = Xavier.call('eval',datalogger_board_name,'adc_samplerate_set',adc_channel[channel],(samplerate,"Hz"))
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()

@Utility.timeout(1)
def datalogger_samplerate_get_handle(params):

    help_info = "datalogger samplerate get(<channel>)$\r\n\
            \tchannel:(chanA,chanB) \r\n"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''parameters analysis'''
    params_count = len(params)
    if params_count  != 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    channel=params[0]
    if channel !="chanA" and channel !="chanB":
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")      
    global datalogger_board_name
    result = Xavier.call('eval',datalogger_board_name,'adc_samplerate_get',adc_channel[channel])
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done(str(result))

@Utility.timeout(1)
def datalogger_write_handle(params):

    help_info = "datalogger write(<registor>, <data>)$\r\n\
    : registor=(0x00-0xff),data=(0x00-0xfffff)$\r\n"

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    
    '''parameters analysis'''
    params_count = len(params)
    if params_count  != 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    reg_addr = int(params[0],16)

    data = int(params[1],16)


    #doing
    global datalogger_board_name
    result = Xavier.call('eval',datalogger_board_name,'adc_register_write',reg_addr,data)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()



@Utility.timeout(1)
def datalogger_read_handle(params):
    
    help_info = "datalogger read(<reg_addr>)$\r\n\
    \treg_addr:(0x00-0xff)\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    #adc register address
    reg_addr = int(params[0],16)

    #doing
    global datalogger_board_name
    result = Xavier.call('eval',datalogger_board_name,'adc_register_read',reg_addr)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    out_msg = '0x%04x'%(result)
    return Utility.handle_done(out_msg)
    

@Utility.timeout(10)
def datalogger_measure_handle(params):
    
    help_info = "datalogger measure(<channel,count>)$\r\n\
    \tchannel:(voltage,current),count:(1-500)\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    channel = params[0]
    
    #data count
    count = int(params[1],10)

    #doing
    global datalogger_board_name
    result = Xavier.call('eval',datalogger_board_name,'datalogger_measure',adc_channel[channel],count)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    out_msg = 'rms=%f%s,average=%f%s,max=%f%s,min=%f%s'%(result["rms"][0],result["rms"][1],result["average"][0],result["average"][1],result["max"][0],result["max"][1],result["min"][0],result["min"][1])
    return Utility.handle_done(out_msg)