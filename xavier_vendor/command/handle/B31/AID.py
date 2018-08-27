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
AID_channel=['AID_1','AID_2']
@Utility.timeout(5)
def aid_init_handle(params):
    help_info = "aid init(<channel>) $\r\n\
    \tchannel=(AID_1,AID_2)\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    if len(params)!=1:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],\
                                    "param length error" )        
    channel=params[0]
    if channel not in AID_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "channel parameter error" )
    ''' doing '''
    result = Xavier.call('eval',test_base_board_name,'aid_init',channel)   
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute aid config error") 

    return Utility.handle_done()

@Utility.timeout(2)
def aid_disable_handle(params):
    help_info = "aid disable(<channel>) $\r\n\
        \tchannel=(AID_1,AID_2)\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    if len(params)!=1:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],\
                                    "param length error" )        
    channel=params[0]
    if channel not in AID_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "channel parameter error" )
    ''' doing '''
    result = Xavier.call('eval',test_base_board_name,'aid_disable',channel)
    
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute aid disable error") 

    return Utility.handle_done()


@Utility.timeout(2)
def aid_config_handle(params):
    help_info = "aid config(<chanenl>,<data_index>, <req_len>, <req_datas:data1,data2,...>, <resp_len>, <resp_datas:data1,data2,...>) $\r\n\
\tchannel=(AID_1,AID_2)\r\n\
\tdata_index:(0-63)$\r\n\
\treq_len: length of req_datas $\r\n\
\treq_datas:(0x00,0x01,...) hex %$\r\n\
\tresp_len: length of resp_datas $\r\n\
\tresp_datas:(0x00,0x01,... ) hex $\r\n" 

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' default info '''
    base_param_index = 1
    req_datas = []
    resp_datas = []
    ''' parameter analysis'''
    params_count = len(params)
 
    channel=params[0]
    if channel not in AID_channel:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,\
                                        "channel parameter error" )
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            data_index = int(params[index])
            if data_index not in range(0,64):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s data_index error"%(index+1))
        elif index == base_param_index + 1:
            req_len = int(params[index])
            if req_len not in range(0,64):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s req_len error"%(index+1))
        elif index in range(base_param_index + 2, base_param_index +2 + req_len):
            try:
                req_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("req data error:" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s req data error"%(index+1))
        elif index == base_param_index + 2 + req_len:
            resp_len = int(params[index])
            if resp_len not in range(0,64):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s resp_len error"%(index+1))
        elif index in range(base_param_index + 3 + req_len, base_param_index + 3 + req_len + resp_len):
            try:
                resp_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("req data error:" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s req data error"%(index+1)) 
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param len error")

    ''' doing '''
    result = Xavier.call('eval',test_base_board_name,'aid_data_config', channel,data_index, req_datas, resp_datas)
    
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute aid config error") 

    return Utility.handle_done()

