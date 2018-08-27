#-*- coding: UTF-8 -*-
__author__ = 'Neal'

import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger

global i2c_bus_list
i2c_bus_list=None

def get_i2c_bus_list():
    global i2c_bus_list
    i2c_bus_list = {}
    buses = Xavier.call("get_buses")
    for name, bus in buses.iteritems():
        if bus['bus'] == 'i2c':
            i2c_bus_list[name] = bus
    return i2c_bus_list


@Utility.timeout(2)
def i2c_read_handle(params):
    if i2c_bus_list is None:
        get_i2c_bus_list()
    help_info = "i2c read(<bus_name>,<slave_addr>,<read_length>)$\r\n\
\tbus_name=("+",".join(i2c_bus_list) +")$\r\n\
\tslave_addr=(0x00-0x7F), slave device 7 bits address$\r\n\
\read_length=(0-32)$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 3:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error") 

    #bus
    bus_name = params[0]
    if bus_name not in i2c_bus_list:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"bus name param error")

    #slave device address
    slave_addr = int(params[1],16)
    if slave_addr > 0x7f:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"slave device address param error")

    #read data count
    read_length = int(params[2])
    if read_length > 32 or read_length < 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"read length bytes param error")
    
    #doing
    result = Xavier.call("i2c_read",bus_name, slave_addr, read_length)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    elif len(result) != read_length:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error: read data length error")
    
    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


@Utility.timeout(2)
def i2c_write_handle(params):
    if i2c_bus_list is None:
        get_i2c_bus_list()

    help_info = "i2c write(<bus_name>,<slave_addr>,<write_length>,<write_content>)$\r\n\
\tbus_name=("+",".join(i2c_bus_list)  +")$\r\n\
\tslave_addr=(0x00-0x7F), slave device 7 bits address$\r\n\
\write_length=(0-32)$\r\n\
\twrite_content: format =[data_1,data_2,...,data_n], data_n=(0x00-0xff)$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  < 4:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    #bus
    bus_name = params[0]
    if bus_name not in i2c_bus_list:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"bus name param error")

    #slave device address
    slave_addr = int(params[1],16)
    if slave_addr > 0x7f:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"slave device address param error")

    #write data count
    write_length = int(params[2])
    if write_length > 32 or write_length < 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"write length bytes param error")
    
    #write datas
    if(params_count != (write_length+3)):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    write_datas=[]
    for index  in range(3,3+write_length):
        write_datas.append(int(params[index],16))

    #doing
    result = Xavier.call("i2c_write",bus_name, slave_addr, write_datas)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    return Utility.handle_done()


@Utility.timeout(2)
def i2c_rdwr_handle(params):
    if i2c_bus_list is None:
        get_i2c_bus_list()
    help_info = "i2c rdwr(<bus_name>,<slave_addr>,<write_length>,<write_content>,<read_length>)$\r\n\
\tbus_name=("+",".join(i2c_bus_list)  +")$\r\n\
\tslave_addr=(0x00-0x7F), slave device 7 bits address$\r\n\
\twrite_length=(1-32)$\r\n\
\twrite_content: format =[data_1,data_2,...,data_n], data_n=(0x00-0xff)$\r\n\
\tread_length=(1-32)$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  < 4:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    #bus
    bus_name = params[0]
    if bus_name not in i2c_bus_list:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"bus name param error")

    #slave device address
    slave_addr = int(params[1],16)
    if slave_addr > 0x7f:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"slave device address param error")

    #write data count
    write_length = int(params[2])
    if write_length > 32 or write_length < 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"write length bytes param error")
    
    #write datas
    if(params_count != (write_length+3+1)):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    write_datas=[]
    for index  in range(3,3+write_length):
        write_datas.append(int(params[index],16))

    #read length
    read_length=int(params[write_length+3])

    #doing
    result = Xavier.call("i2c_rdwr",bus_name, slave_addr, write_datas,read_length)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    elif len(result) != read_length:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error: read data length error")
    
    #packet result
    out_msg = ''
    for data in result:
        out_msg += '0x%02x,'%(data)

    return Utility.handle_done(out_msg[:-1])


def i2c_config_handle(params):
    if i2c_bus_list is None:
        get_i2c_bus_list()
    help_info = "i2c config(<bus_name>,<frequency>)$\r\n\
\tbus_name=("+",".join(i2c_bus_list) +")$\r\n\
\tfrequency=(1~)Hz $\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in i2c_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            frequency = int(params[index])
            if frequency < 1:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s frequency error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("i2c_config",bus_name, frequency)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()

def i2c_crol_handle(params):
    if i2c_bus_list is None:
        get_i2c_bus_list()
    help_info = "i2c crol(<bus_name>,<state>)$\r\n\
\tbus_name=("+",".join(i2c_bus_list) +")$\r\n\
\tstate=(0,1)$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    base_param_index = 0
    params_count = len(params)
    
    for index in range(base_param_index, params_count):
        if index == base_param_index + 0:
            bus_name = params[index]
            if bus_name not in i2c_bus_list:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s bus_name error"%index)
        elif index == base_param_index + 1:
            state = int(params[index])
            if state not in [0,1]:
                return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param %s state error"%index)
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"error ,params should less than %s "%index)

    #doing
    result = Xavier.call("i2c_crol",bus_name, state)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    return Utility.handle_done()