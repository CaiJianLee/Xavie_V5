#-*- coding: UTF-8 -*-
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
def spi_slave_read_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi slave read(<bus_name>,<address>,<read_length>)$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\taddress=hex address,0xXXXX $\r\n\
\tread_length=(0-32) $\r\n"
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
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            address = int(params[index], 16)
            if address not in range(0,0xffff+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s address error"%index)
        elif index == base_param_index + 2:
            read_length = int(params[index])
            if read_length not in range(0,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s read_length error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_slave_read",bus_name, address, read_length)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    elif len(result) != read_length:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error: read data error")

    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


@Utility.timeout(5)
def spi_slave_write_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi slave write(<bus_name>,<address>,<write_len>,<write_datas>)$\r\n\
\tbus_name=("+",".join(spi_bus_list) +")$\r\n\
\taddress: (0xHHHH),hex data $\r\t\n\
\twrite_len: (1-32) $\r\n\
\twrite_datas:(0x1f,0x33,...) hex $\r\n"
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
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)

        elif index == base_param_index + 1 :
            address = int(params[index], 16)
            if address not in range(0,0xffff+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s address error"%index)

        elif index == base_param_index + 2:
            write_len = int(params[index])
            if write_len not in range(1,32+1):
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write_len error"%index)
            if params_count < write_len + index + 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"the num of write_datas error")
        elif index in range(base_param_index + 3, base_param_index + 3 + write_len):
            try:
                write_datas.append(int(params[index], 16))
            except Exception as e:
                logger.error("write datas error :" + repr(e))
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s write data error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_slave_write",bus_name, address, write_datas)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()

@Utility.timeout(5)
def spi_slave_config_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi slave config(<bus_name>,<spi_clk_cpha_cpol>,<spi_byte_cfg>)$\r\n\
\tspi_clk_cpha_cpol: 'Mode_0' --CPHA=0, CPOL=0,  when CS is high, the SCLK is low,  first edge sample $\r\n\
\t                   'Mode_1' --CPHA=0, CPOL=1,  when CS is high, the SCLK is high, first edge sample $\r\n\
\t                   'Mode_2' --CPHA=1, CPOL=0,  when CS is high, the SCLK is low,  second edge sample $\r\n\
\t                   'Mode_3' --CPHA=1, CPOL=1,  when CS is high, the SCLK is high, second edge sample $\r\n\
\tspi_byte_cfg:      '1'    --spi slave receive data or send data is 1byte $\r\n\
\t                   '2'    --spi slave receive data or send data is 2byte $\r\n\
\t                   '3'    --spi slave receive data or send data is 3byte $\r\n\
\t                   '4'    --spi slave receive data or send data is 4byte $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)

    if params_count < 3:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    for index in range(params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in spi_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            tspi_clk_cpha_cpol = params[index]
            if tspi_clk_cpha_cpol not in {"Mode_0","Mode_1","Mode_2","Mode_3"}:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s tspi_clk_cpha_cpol error"%index)
        elif index == base_param_index + 2:
            spi_byte_cfg = params[index]
            if spi_byte_cfg not in ["1","2","3","4"]:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s spi_byte_cfg error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("spi_slave_config",bus_name, tspi_clk_cpha_cpol ,spi_byte_cfg)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()

def spi_slave_disable_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi slave disable(<bus_name>)$\r\n\
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
    result = Xavier.call("spi_slave_disable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()

def spi_slave_enable_handle(params):
    if spi_bus_list is None:
        get_spi_bus_list()
    help_info = "spi slave enable(<bus_name>)$\r\n\
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
    result = Xavier.call("spi_slave_enable",bus_name)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()