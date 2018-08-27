#-*- coding: UTF-8 -*-
import re
import time
import command.server.handle_utility as Utility
from ee.common import logger
import sys
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
mcu_io_min=1
mcu_io_max=7

gpio_translation=[
                  "LEVEL_SHIFTER_EN"]
swd_gpio=["UUT1_MCU_RESET_L"]
swd_gpio_help=""
for key in swd_gpio:
    swd_gpio_help+=key+'\r\n'
    
@Utility.timeout(2)
def mcu_io_set_handle(params):
    help_info = "mcu io set({<count>,<content>})$\r\n\
        \tcount: (1-32) $\r\n\
        \tcontent=(LEVEL_SHIFTER_EN=Y),Y=(0,1)\r\n" 
    if Utility.is_ask_for_help(params) is True:
       return Utility.handle_done(help_info)  
    ioes = {}
    ''' params analysis '''
    params_count = len(params)
    param_count = int(params[0],10)
    if param_count < 1 or param_count > 32:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")    

    if params_count != param_count + 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
       
    for index in range(1, param_count+1):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'(.+)=(\w+)',params[index])
        
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
        if regular_expression.group(1) in gpio_translation:
            ioes[regular_expression.group(1)]=int(regular_expression.group(2) ,10)
        else:
            regular_expression = re.match( r'uut(\w)_gpio(\w+)=(\w+)', params[index])
            ''' 提取成功匹配的值 '''
            if regular_expression is None:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
            channel = int(regular_expression.group(1), 10)
            bit_number = int(regular_expression.group(2), 10)
            bit_state =( int(regular_expression.group(3), 10)) & 0x01
            if channel<=0 or channel>4:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error") 
            if bit_number >=mcu_io_min and bit_number <=mcu_io_max:
                ioes['uut'+str(channel)+"_"+'gpio' + str(bit_number)] = bit_state
            else:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
  #  logger.error(str(ioes))
    '''    doing    '''
    if(Xavier.call("eval",test_base_board_name,"mcu_io_set",ioes)):
       pass
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    return Utility.handle_done()

@Utility.timeout(2)
def swd_rst_ctrl_set_handle(params):
    help_info = "swd rst ctrl set(<channel>,<status>)$\r\n\
        \tchannel:"+swd_gpio_help+"\
        \tstatus=(H,L)\r\n" 
    if Utility.is_ask_for_help(params) is True:
       return Utility.handle_done(help_info)  
    ''' params analysis '''
    params_count = len(params)
    if params_count !=2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")    
    channel=params[0]
    if channel  not in swd_gpio :
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param channel error")    
    status=params[1]
    if (status!='H' )and(status!='L' ):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param status error")                  
    if(Xavier.call("eval",test_base_board_name,"swdrstctrl",channel,status)):
       pass
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    return Utility.handle_done()
       
       
       

