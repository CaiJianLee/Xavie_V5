#-*- coding: UTF-8 -*-
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger

global swd_bus_list
swd_bus_list=None

def get_swd_bus_list():
    global swd_bus_list
    swd_bus_list = {}
    buses = Xavier.call("get_buses")
    for name, bus in buses.iteritems():
        if bus['bus'] == 'swd':
            swd_bus_list[name] = bus
    return swd_bus_list


@Utility.timeout(5)
def swd_read_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd read(<bus_name>,<request_data>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n\
\trequst_data:(0x00~0xff) hex, 1 byte, eg:0xB7 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            request_data = int(params[index], 16)
            if request_data not in range(0, 0xff + 1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s request_data error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_read",bus_name, request_data)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    #packet result
    out_msg = 'data:0x%08x, ack:0x%02x, parity:0x%02x'%(result[0],result[1],result[2])
    return Utility.handle_done(out_msg)


@Utility.timeout(5)
def swd_write_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd write(<bus_name>,<request_data>,<write_data>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n\
\trequest_data:(0x00~0xff) hex, 1 byte $\r\n\
\twrite_data:(0x00~0xffffffff) hex, less than 4 bytes$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 3:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            request_data = int(params[index], 16)
            if request_data not in range(0, 0xff):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s request_data error"%index)
        elif index == base_param_index + 2:
            write_data = int(params[index], 16)
            if write_data < 0 or write_data > 0xffffffff:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write_data:%s error"%(index, hex(write_data)))
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_write",bus_name, request_data, write_data)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    out_msg = 'ack:0x%02x'%result
    return Utility.handle_done(out_msg)


@Utility.timeout(5)
def swd_freq_set_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd freq set(<bus_name>,<freq>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n\
\tfreq: (0~ ) Hz $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)
    ''' parameters analysis '''
    base_param_index = 0
    write_datas = []
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            freq = int(params[index])
            if freq < 0 :
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s freq error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_freq_set",bus_name, freq)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()


@Utility.timeout(5)
def swd_rst_set_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd rst set(<bus_name>,<level>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n\
\tlevel: (0 ,1) $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            level = int(params[index])
            if level == 0:
                level = 'L'
            elif level == 1:
                level ='H'
            else:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s level error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_rst_set",bus_name, level)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    #packet result
    return Utility.handle_done()

def swd_timing_generate_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd timing generate(<bus_name>,<data_len>,<data_1,data_2,...data_n>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n\
\tdata_len: (1- ) $\r\n\
\tdata:(0x1f,0x33,...) hex $\r\n\
\t     data, bit order: first_byte_bit0-->bit7,second_byte_bit0-->bit7,...,last_byte_bit0-->bit7 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    write_datas = []
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            data_len = int(params[index])
            if data_len < 1 :
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s data_len error"%index)
            if params_count < data_len + index + 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"the num of write_datas error")
        elif index in range(base_param_index + 2, base_param_index + 2 + data_len):
            try:
                write_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("write datas error :" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write data error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_timing_generate",bus_name, write_datas)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()


def swd_disable_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd disable(<bus_name>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_disable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()

def swd_enable_handle(params):
    if swd_bus_list is None:
        get_swd_bus_list()
    help_info = "swd enable(<bus_name>)$\r\n\
\tbus_name=("+",".join(swd_bus_list) +")$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in swd_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("swd_enable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()
