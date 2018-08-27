#-*- coding: UTF-8 -*-
__author__ = 'yongjiu'

import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger

global hdq_bus_list
hdq_bus_list=None

def get_hdq_bus_list():
    global hdq_bus_list
    hdq_bus_list = {}
    buses = Xavier.call("get_buses")
    for name, bus in buses.iteritems():
        if bus['bus'] == 'hdq':
            hdq_bus_list[name] = bus
    return hdq_bus_list


@Utility.timeout(2)
def hdq_slave_read_handle(params):
    if hdq_bus_list is None:
        get_hdq_bus_list()
    help_info = "hdq slave read(<bus_name>)$\r\n\
\tbus_name=("+",".join(hdq_bus_list) +")$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error") 

    #bus
    bus_name = params[0]
    if bus_name not in hdq_bus_list:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"bus name param error")

    #doing
    addr, data = Xavier.call("hdq_slave_read",bus_name)
    if False in (addr, data):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    #packet result
    out_msg = 'addr:%s, data:%s'%(addr, data)

    return Utility.handle_done(out_msg)


@Utility.timeout(2)
def hdq_slave_write_handle(params):
    if hdq_bus_list is None:
        get_hdq_bus_list()

    help_info = "hdq slave write(<bus_name>,<slave_addr>,<write_data)$\r\n\
\tbus_name=("+",".join(hdq_bus_list)  +")$\r\n\
\tslave_addr=(0x00-0x7F), slave device 7 bits address$\r\n\
\twrite_data=(0x00-0xff)$\r\n"
    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 3:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    #bus
    bus_name = params[0]
    if bus_name not in hdq_bus_list:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"bus name param error")

    #slave device address
    slave_addr = int(params[1],16)
    if slave_addr > 0x7f:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"slave device address param error")

    #write data count
    write_data = int(params[2])
    if write_data > 0xff or write_data < 0:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"write data bytes param error")

    #doing
    addr = Xavier.call("hdq_slave_write",bus_name, slave_addr, write_data)
    if addr is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

    #packet result
    out_msg = 'receive addr:0x%02x'%addr
    return Utility.handle_done(out_msg)
