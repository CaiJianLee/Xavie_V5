#-*- coding: UTF-8 -*-
__author__ = 'yongjiu'

import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger

global spi_bus_list
spi_bus_list=None

def get_spi_bus_list():
    global spi_bus_list
    spi_bus_list = {}
    buses = Xavier.call("get_buses")
    for name, bus in buses.iteritems():
        if bus['bus'] == 'spi':
            spi_bus_list[name] = bus
    return spi_bus_list


@Utility.timeout(5)
def spi_read_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi read(<bus_name>,<read_length>{,<cs_extend>})$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\tread_length=(0-32)$\r\n\
\tcs_extend: (0-8), default =0 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' default info '''
    cs_extend = 0
    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            read_length = int(params[index])
            if read_length not in range(0,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s read_length error"%index)
        elif index == base_param_index + 2:
            cs_extend = int(params[index])
            if cs_extend not in range(0,8+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s cs_extend error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_read",bus_name, read_length, cs_extend)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    elif len(result) != read_length:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error: read data length error")

    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


@Utility.timeout(5)
def spi_write_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi write(<bus_name>,<write_len>,<write_datas>{,<cs_extend>})$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\twrite_len: (1-32) $\r\n\
\twrite_datas:(0x1f,0x33,...) hex $\r\n\
\tcs_extend: (0-8), default =0 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' default info '''
    cs_extend = 0

    ''' parameters analysis '''
    base_param_index = 0
    write_datas = []
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            write_len = int(params[index])
            if write_len not in range(1,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write_len error"%index)
            if params_count < write_len + index + 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"the num of write_datas error")
        elif index in range(base_param_index + 2, base_param_index + 2 + write_len):
            try:
                write_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("write datas error :" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write data error"%index)
        elif index == base_param_index + 2 + write_len :
            cs_extend = int(params[index])
            if cs_extend not in range(0,8+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s cs_extend error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_write",bus_name, write_datas, cs_extend)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()


@Utility.timeout(5)
def spi_write_and_read_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi write and read(<bus_name>,<write_len>,<write_datas>{,<cs_extend>})$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\twrite_len: (1-32) $\r\n\
\twrite_datas:(0x1f,0x33,...) hex $\r\n\
\tcs_extend: (0-8), default =0 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' default info '''
    cs_extend = 0

    ''' parameters analysis '''
    base_param_index = 0
    write_datas = []
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            write_len = int(params[index])
            if write_len not in range(1,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write_len error"%index)
            if params_count < write_len + index + 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"the num of write_datas error")
        elif index in range(base_param_index + 2, base_param_index + 2 + write_len):
            try:
                write_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("write datas error :" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write data error"%index)
        elif index == base_param_index + 2 + write_len :
            cs_extend = int(params[index])
            if cs_extend not in range(0,8+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s cs_extend error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_write_and_read",bus_name, write_datas, cs_extend)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


@Utility.timeout(5)
def spi_write_to_read_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi write to read(<bus_name>,<write_len>,<write_datas>,<read_len>{,<cs_extend>})$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\twrite_len: (1-32) $\r\n\
\twrite_datas:(0x1f,0x33,...) hex $\r\n\
\tread_len:(0-32) $\r\n\
\tcs_extend: (0-8), default =0 $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' default info '''
    cs_extend = 0

    ''' parameters analysis '''
    base_param_index = 0
    write_datas = []
    params_count = len(params)
    if params_count < 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            write_len = int(params[index])
            if write_len not in range(1,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write_len error"%index)
            if params_count < write_len + index + 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"the num of write_datas error")
        elif index in range(base_param_index + 2, base_param_index + 2 + write_len):
            try:
                write_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("write datas error :" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write data error"%index)
        elif index == base_param_index + 2 + write_len :
            read_len = int(params[index])
            if read_len not in range(0,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s read_len error"%index)
        elif index == base_param_index + 2 + write_len +1:
            cs_extend = int(params[index])
            if cs_extend not in range(0,8+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s cs_extend error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_write_to_read",bus_name, write_datas ,read_len, cs_extend)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    elif len(result) != read_len:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error: read data length error")

    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


def spi_config_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi config(<bus_name>,<clk_frequency>,<clk_type>{,<wait_time_us>,<spi_clk_polarity>})$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\tclk_frequency:(0-100 000 000)Hz $\r\n\
\tclk_type:(pos or neg), $\r\n\
\t          'pos' --sclk posedge send data, sclk negedge receive data$\r\n\
\t          'neg' --sclk negedge send data, sclk posedge receive data$ \r\n\
\twait_time_us: the wait time for new spi access, default=1 $\r\n\
\tspi_clk_polarity(str): $\r\n\
\t          'high' --when CS is high, the SCLK is high $\r\n\
\t          'low'  --when CS is high, the SCLK is low $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    wait_time_us = 1
    spi_clk_polarity = 'high'
    params_count = len(params)

    if params_count < 3:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            clk_frequency = int(params[index])
            if clk_frequency < 0:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s clk_frequency error"%index)
        elif index == base_param_index + 2:
            clk_type = params[index]
            if clk_type not in {"pos", "neg"}:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s clk_type error"%index)
        elif index == base_param_index + 3:
            wait_time_us = int(params[index])
            if wait_time_us not in range(0,10000):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s wait_time_us error"%index)
        elif index == base_param_index + 4:
            spi_clk_polarity = params[index]
            if spi_clk_polarity not in ['high','low']:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s spi_clk_polarity error"%index)

        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_config",bus_name, clk_frequency ,clk_type, wait_time_us, spi_clk_polarity)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()

def spi_disable_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi disable(<bus_name>)$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n"
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
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_disable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()

def spi_enable_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi enable(<bus_name>)$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n"
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
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_enable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()