#-*- coding: UTF-8 -*-
__author__ = 'zhenhua'

import re
import time
import command.server.handle_utility as Utility

from ee.common import xavier as Xavier

global eeprom_id_list
eeprom_id_list=None

def get_eeprom_id_list():
    global eeprom_id_list
    eeprom_id_list = []
    eeprom_dict = Xavier.call('get_eeprom')
    for board_name in eeprom_dict.keys():
        eeprom_id_list.append(board_name)

@Utility.timeout(1)
def eeprom_write_handle(params):
    if eeprom_id_list is None:
        get_eeprom_id_list()
    help_info = "eeprom write(<board-name>,<type>,<address>,<count>,<content>)$\r\n\
\tboard-name:(" + ",".join(eeprom_id_list) + ")$\r\n\
\ttype:(at01,at02,at04,at08,at16,at128,at256,at512,$\r\n\
\t\tcat01,at02,cat04,cat08,cat16)$\r\n\
\taddress:(0x0000-0xHHHH)v\r\n\
\tcount:(1-100)$\r\n\
\tcontent=(HH,HH,...HH)$\r\n"

    #help
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    param_count = len(params)
    if param_count < 5 :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param length error" )
    content = []
    for index in range(0,param_count):
        if index == 0:
            board_name = params[index]
        elif index == 1:
            type = params[index]
        elif index == 2:
            address = int(params[index], 16)
        elif index == 3:
            length = int(params[index],10)
        else :
            if len(content) < length:
                content += [int(params[index],16)]
            else :
                return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"num of data error" )

    if board_name not in eeprom_id_list:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] - 1,"param error" )
    if length < 0 or length > 100:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] - 2,"read data is too long" )
    if length != len(content):
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] - 3,"num of data error" )
    if Xavier.call('eeprom_write', board_name, address, content) is True:
        return Utility.handle_done()
    else:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_execute_failure"],"message execute failed")

@Utility.timeout(1)
def eeprom_read_handle(params):
    if eeprom_id_list is None:
        get_eeprom_id_list()
    help_info = "eeprom read(<board-name>,<type>,<address>,<count>) $\r\n\
\tboard-name:(" +  ",".join(eeprom_id_list) + ")$\r\n\
\ttype:(at01,at02,at04,at08,at16,at128,at256,at512,$\r\n\
\t\tcat01,cat02,cat04,cat08,cat16)$\r\n\
\taddress =(0x00-0xHHHH)$\r\n\
\tcount = (1-100)$\r\n"

    #help
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    param_count = len(params)
    if param_count != 4 :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,"param length error" )

    for index in range(0,param_count):
        if index == 0:
            board_name = params[0]
        elif index == 1:
            type = params[index]
        elif index == 2:
            address = int(params[index], 16)
        elif index == 3:
            length = int(params[index],10)
        else :
            return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] - index,"param error" )

    if board_name not in eeprom_id_list:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] - 1,"param error" )
    result = Xavier.call('eeprom_read', board_name, address, length)
    if  result is False:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_execute_failure"],"read failed" )
    msg = ""
    for index in range(0,len(result)):
        msg += "%02x"%(result[index])
        if index != len(result) - 1:
            msg += ","

    return Utility.handle_done(msg)

@Utility.timeout(1)
def eeprom_string_write_handle(params):
    if eeprom_id_list is None:
        get_eeprom_id_list()
    help_info = "eeprom string write(<board-name>,<type>,<address>,\"<string>\")$\r\n\
\tboard-name:(" +  ",".join(eeprom_id_list)  + ")$\r\n\
\ttype:(at01,at02,at04,at08,at16,at128,at256,at512,$\r\n\
\t\tcat01,cat02,cat04,cat08,cat16)$\r\n\
\taddress =(0x00-0xHHHH)$\r\n\
\tstring: a string $\r\n"

    #help
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    param_count = len(params)
    if param_count < 4 :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param length error" )

    buf = ""
    for index in range(0,param_count):
        if index == 0:
            board_name = params[0]
        elif index == 1:
            type = params[1]
        elif index == 2:
            address = int(params[index], 16)
        elif index >= 3:
            if buf != "":
                buf += ","
            buf += params[index]

        else :
            return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"] ,"param error" )

    if board_name not in eeprom_id_list:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param board_name error" )
    if len(buf) > 200:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"write data is too long" )
    content = []
    for index in range(0,len(buf)):
        if (buf[index] != '\"') and (buf[index] != '\0') :
            content += [ord(buf[index])]

    if Xavier.call('eeprom_write', board_name, address, content) is True:
        return Utility.handle_done()
    else:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_execute_failure"],"message execute failed")

@Utility.timeout(1)
def eeprom_string_read_handle(params):
    if eeprom_id_list is None:
        get_eeprom_id_list()
    help_info = "eeprom string read(<board-name>,<type>,<address>,<count>) $\r\n\
\tboard-name:(" +  ",".join(eeprom_id_list)  + ")$\r\n\
\ttype:(at01,at02,at04,at08,at16,at128,at256,at512,$\r\n\
\t\tcat01,cat02,cat04,cat08,cat16)$\r\n\
\taddress =(0x00-0xHHHH)$\r\n\
\tcount=(1-100)$\r\n"

    #help
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    param_count = len(params)
    if param_count != 4 :
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param length error" )

    for index in range(0,param_count):
        if index == 0:
            board_name = params[0]
        elif index == 1:
            type = params[1]
        elif index == 2:
            address = int(params[index], 16)
        elif index == 3:
            length = int(params[index],10)
        else :
            return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param error" )

    if board_name not in eeprom_id_list:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"param board_name error" )
    if length < 0 or length > 100:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_parameter_invalid"],"read data is too long" )

    result = Xavier.call('eeprom_read', board_name, address, length)
    if  result is False:
        return Utility.handle_error(Utility.handle_errorno["handle_errno_execute_failure"],"read failed" )
    msg = ""
    msg += '\"'
    for index in range(0,len(result)):
        if result[index] >= 0x00 or result[index] <= 0x7F:
            msg += chr(result[index])
        else:
            msg += " "
    msg += '\"'
    msg += '\0'

    return Utility.handle_done(msg)
