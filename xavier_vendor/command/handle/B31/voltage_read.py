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

#  
# def adc_voltage_read_handle(params):
#     help_info = "adc voltage read()$\r\n"
#     ''' params init '''
#     ''' help '''    
#     if Utility.is_ask_for_help(params) is True:
#         return Utility.handle_done(help_info)
#   
#     ''' parametr analysis '''
#     params_count = len(params)
#     if params_count !=0:
#         return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
#                                         "param length error" )         
#     ret=Xavier.call("eval",test_base_board_name,"adc_voltage_read")
#     if ret is False:
#         return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
#                                          "execute  error")
#     output_str=str(ret)+"mV"
#     return Utility.handle_done(output_str)

def ad7175_voltage_read_handle(params):
    help_info = "ad7175 voltage read(<channel>)$\r\n\
      \t channel:(chan0,chan1)\r\n"
    ''' params init '''
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)    
    ''' parametr analysis '''
    params_count = len(params)
    if params_count !=1:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "param length error" )         
    channel=params[0]
    if channel !="chan0" and channel !="chan1":
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "channel param error" )            
    ret=Xavier.call("eval",test_base_board_name,"ad7175_voltage_measure",channel)
    if ret is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],\
                                         "execute  error")
    output_str=str(ret[0])+"mV"
    return Utility.handle_done(output_str)

     
