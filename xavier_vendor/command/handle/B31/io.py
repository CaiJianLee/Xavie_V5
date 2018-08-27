#-*- coding: UTF-8 -*-
__author__ = 'zhenhua'

import re
import time
import command.server.handle_utility as Utility

from collections import OrderedDict
from ee.common import logger

from ee.common import xavier as Xavier1
import sys
sys.path.append('/opt/seeing/app/')
from b31_bp import xavier1 as Xavier2
global agv
agv=sys.argv[1]
Xavier=Xavier1
xavier_module = {"tcp:7801":Xavier1, "tcp:7802":Xavier2}
if agv in xavier_module:
    Xavier=xavier_module[agv]
    

global io_relevant_config
global board_id
io_relevant_config=None
board_id=None

def _get_board_id():
    global board_id
    board_id = Xavier.call("get_base_board_name")

def _get_io_relevant_config():
    global io_relevant_config
    io_relevant_config = {}
    bit_dict={}
    chip_dict={}
    io_chip_dict = Xavier.call('get_extendio')
    for name, description in io_chip_dict[board_id].items():
        if "bit" in name:
            bit_dict[name] = description
        elif "cp" in name:
            chip_dict[name] = description

    bit_sorted_list = _chips_bits_sort("bits",bit_dict)
    chip_sorted_list = _chips_bits_sort("chips",chip_dict)

    io_relevant_config["chips_num"] = len(chip_dict)
    io_relevant_config["min_bit_num"] = bit_sorted_list[0]
    io_relevant_config["max_bit_num"] = bit_sorted_list[len(bit_dict)-1]
    io_relevant_config["min_chip_num"] = chip_sorted_list[0]
    io_relevant_config["max_chip_num"] = chip_sorted_list[len(chip_dict)-1]

def _chips_bits_sort(types, original_dict):
    num_list = []
    if "chips" == types:
        match_str = r'cp(\w+)'
    elif "bits" == types:
        match_str = r'bit(\w+)'

    for key, value in original_dict.items():
        if value is False:
            original_dict[key] = "????"
        regular_expression = re.match(match_str, key)
        types_number = int(regular_expression.group(1), 10)
        num_list.append(types_number)
    num_list.sort()
    return num_list


def io_set(io_dict):
    '''set cat9555 pin output state
    Arguments:
        io_dict {"bit1":0, "bit2":1} --

    Returns:
        bool -- [True:sucess,False:fail]
    '''
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    if True == Xavier.call('io_set', board_id, io_dict):
        return True
    else:
        return False

def io_read(io_list):
    '''read cat9555 pin state
    Arguments:
        io_list ["bit1", "bit2"] --

    Returns:
        sucess: result_dict eg.{"bit1":0, "bit2":0}
        fail  : False
    '''
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    result_dict = Xavier.call('io_get', board_id, *io_list)
    if "error" not in result_dict:
        return result_dict
    else:
        return False

@Utility.timeout(1)
def io_set_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io set({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX=Y,..bitX=Y),X=("+str(io_relevant_config["min_bit_num"])\
 +"-" + str(io_relevant_config["max_bit_num"]) +"),Y=(0,1)\r\n "
    #start_param = time.time()
    ''' help '''
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
        regular_expression = re.match( r'bit(\w+)=(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        bit_number = int(regular_expression.group(1), 10)
        bit_state =( int(regular_expression.group(2), 10)) & 0x01
        if bit_number >= io_relevant_config["min_bit_num"] and bit_number <= io_relevant_config["max_bit_num"]:
            ioes['bit' + str(bit_number)] = bit_state
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    '''    doing    '''
    if(Xavier.call('io_set', board_id, ioes)):
        return Utility.handle_done()
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")

@Utility.timeout(1)
def io_read_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io read({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX,..bitX),X=("+str(io_relevant_config["min_bit_num"])\
 +"-" + str(io_relevant_config["max_bit_num"]) +")\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    result_dict = OrderedDict()
    operation_bit = []
    output_str = ""

    ''' parametr analysis '''
    param_count = int(params[0],10)
    if not (param_count >= 1 and param_count <= 32):
         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    for index in range(1, param_count+1):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'bit(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        bit_number = int(regular_expression.group(1), 10)
        if bit_number >= io_relevant_config["min_bit_num"] and bit_number <= io_relevant_config["max_bit_num"]:
            operation_bit.append("bit" + str(bit_number))
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    '''    doing    '''
    result_dict = Xavier.call('io_get', board_id, *operation_bit)

    if(result_dict.has_key("error")):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    else:
        # output_str = _chips_bits_sort_str("bits",result_dict)
        for i in range(0, len(operation_bit)):
            output_str += operation_bit[i]+"="+str(result_dict[operation_bit[i]])
            if i != len(operation_bit)-1:
                output_str += ","

        return Utility.handle_done(output_str)


@Utility.timeout(1)
def io_dir_set_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io dir set({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX=Y,..bitX=Y),X=("+str(io_relevant_config["min_bit_num"])\
 +"-" + str(io_relevant_config["max_bit_num"]) +"),Y=(0,1)\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ioes_dir = {}

    ''' parametr analysis '''
    param_count = int(params[0],10)
    if not (param_count >= 1 and param_count <= 32):
         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    for index in range(1, param_count+1):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'bit(\w+)=(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''

        bit_number = int(regular_expression.group(1), 10)
        bit_state =( int(regular_expression.group(2), 10)) & 0x01
        if bit_number >= io_relevant_config["min_bit_num"] and bit_number <= io_relevant_config["max_bit_num"]:
            ioes_dir['bit' + str(bit_number)] = bit_state
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    '''    doing    '''
    if(Xavier.call('io_dir_set', board_id, ioes_dir)):
        return Utility.handle_done()
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute  error")

@Utility.timeout(1)
def io_dir_read_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io dir read({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX,..bitX),X=("+str(io_relevant_config["min_bit_num"])\
 +"-" + str(io_relevant_config["max_bit_num"]) +")\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    result_dict = OrderedDict()
    operation_bit = []
    output_str = ""

    ''' parametr analysis '''
    param_count = int(params[0],10)
    if not (param_count >= 1 and param_count <= 32):
         return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    for index in range(1, param_count+1):
       '''  用正则表达式匹配字符串 '''
       regular_expression = re.match( r'bit(\w+)', params[index])

       '''  判断是否匹配成功 '''
       if regular_expression is None:
           return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

       '''   提取成功匹配的值 '''
       bit_number = int(regular_expression.group(1), 10)
       if bit_number >= io_relevant_config["min_bit_num"] and bit_number <= io_relevant_config["max_bit_num"]:
           operation_bit.append("bit" + str(bit_number))
       else:
           return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    '''    doing    '''
    result_dict = Xavier.call('io_dir_get', board_id, *operation_bit)
    if(result_dict.has_key("error")):
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute  error")
    else:
        # output_str = _chips_bits_sort_str("bits",result_dict)
        for i in range(0, len(operation_bit)):
            output_str += operation_bit[i]+"="+str(result_dict[operation_bit[i]])
            if i != len(operation_bit)-1:
                output_str += ","

        return Utility.handle_done(output_str)

@Utility.timeout(1)
def io_chip_set_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io chip set({<content>})$\r\n\
\tcontent=(cpX=0xHHHH,..cp=0xHHHH),X=("+str(io_relevant_config["min_chip_num"])\
 +"-" + str(io_relevant_config["max_chip_num"]) +",255),255=all; HHHH=(0000-FFFF),Hex data\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    operation_chip = []
    operation_value = []

    ''' parametr analysis '''
    param_count = len(params)

    for index in range(0, param_count):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'cp(\w+)=(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        chip_number = int(regular_expression.group(1), 10)
        chip_state = int(regular_expression.group(2), 16)

        if(chip_number == 255):
            break

        if chip_number >= io_relevant_config["min_chip_num"] and chip_number <= io_relevant_config["max_chip_num"]:
            register_status = [0,0]
            register_status[0] =chip_state & 0xff
            register_status[1] = (chip_state >> 8) & 0xff

        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
        operation_chip.append("cp"+str(chip_number))
        operation_value.append(register_status)

    if chip_number == 255:
        operation_chip = []
        operation_value = []
        register_status = [0,0]
        register_status[0] =chip_state & 0xff
        register_status[1] = (chip_state >> 8) & 0xff
        for index in range(1, io_relevant_config["chips_num"] + 1):
            operation_chip.append("cp"+str(index))
            operation_value.append(register_status)

    '''     doing    '''
    if(Xavier.call('io_chip_set', board_id, operation_chip, operation_value)):
        pass
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute  error")

    return Utility.handle_done()

@Utility.timeout(1)
def io_chip_read_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io chip read({<content>})$\r\n\
\tcontent=(cpX,..cpX),X=("+str(io_relevant_config["min_chip_num"])\
 +"-" + str(io_relevant_config["max_chip_num"]) +",255),255=all\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parametr analysis '''
    param_count = len(params)

    operation_chip = []
    output_str = ''
    count = 1
    length = len(params)

    for index in range(0, param_count):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'cp(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        chip_number = int(regular_expression.group(1), 10)
        if chip_number == 255:
            break

        if chip_number >= io_relevant_config["min_chip_num"] and chip_number <= io_relevant_config["max_chip_num"]:
            operation_chip.append(params[index])
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    if chip_number == 255:
        operation_chip = []
        for index in range(1, io_relevant_config["chips_num"] + 1):
            operation_chip.append("cp"+str(index))

        '''    doing    '''
        result_dict = Xavier.call('io_chip_get', board_id, *operation_chip)
        # output_str = _chips_bits_sort_str("chips",result_dict)

        for key,value in result_dict.items():
            if value is False:
                output_str = output_str + key + '=' + "????"
            else:
                output_str = output_str + key + '=' + str(hex(value))

            if count != io_relevant_config["max_chip_num"]:
                output_str = output_str + ','
                count = count + 1

    else:
        '''    doing    '''
        result_dict = Xavier.call('io_chip_get', board_id, *operation_chip)
        # output_str = _chips_bits_sort_str("chips",result_dict)

        for key,value in result_dict.items():
            if value is False:
                output_str = output_str + key + '=' + "????"
            else:
                output_str = output_str + key + '=' + str(hex(value))

            if count != io_relevant_config["max_chip_num"]:
                output_str = output_str + ','
                count = count + 1

    return Utility.handle_done(output_str)

@Utility.timeout(1)
def io_chip_dir_set_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io chip dir set({<content>})$\r\n\
\tcontent=(cpX=0xHHHH,..cp=0xHHHH),X=("+str(io_relevant_config["min_chip_num"])\
 +"-" + str(io_relevant_config["max_chip_num"]) +",255),255=all; HHHH=(0000-FFFF),Hex data\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    operation_chip = []
    operation_value = []

    ''' parametr analysis '''
    param_count = len(params)

    for index in range(0, param_count):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'cp(\w+)=(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        chip_number = int(regular_expression.group(1), 10)
        chip_state = int(regular_expression.group(2), 16)

        if(chip_number == 255):
            break

        if chip_number >= io_relevant_config["min_chip_num"] and chip_number <= io_relevant_config["max_chip_num"]:
            '''  设置指定chip的状态  '''
            register_status = [0,0]
            register_status[0] =chip_state & 0xff
            register_status[1] = (chip_state >> 8) & 0xff
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        operation_chip.append("cp"+str(chip_number))
        operation_value.append(register_status)

    if chip_number == 255:
        operation_chip = []
        operation_value = []
        register_status = [0,0]
        register_status[0] =chip_state & 0xff
        register_status[1] = (chip_state >> 8) & 0xff
        for index in range(1, io_relevant_config["chips_num"] + 1):
            operation_chip.append("cp"+str(index))
            operation_value.append(register_status)

    if(Xavier.call('io_chip_dir_set', board_id, operation_chip, operation_value)):
        pass
    else:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute  error")

    return Utility.handle_done()

@Utility.timeout(1)
def io_chip_dir_read_handle(params):
    if board_id is None:
        _get_board_id()
    if io_relevant_config is None:
        _get_io_relevant_config()

    help_info = "io chip dir read({<content>})$\r\n\
\tcontent=(cpX,..cpX),X=("+str(io_relevant_config["min_chip_num"])\
 +"-" + str(io_relevant_config["max_chip_num"]) +",255),255=all\r\n "

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parametr analysis '''
    param_count = len(params)

    operation_chip = []
    output_str = ''
    count = 1
    length = len(params)

    for index in range(0, param_count):
        '''  用正则表达式匹配字符串 '''
        regular_expression = re.match( r'cp(\w+)', params[index])

        '''  判断是否匹配成功 '''
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        '''   提取成功匹配的值 '''
        chip_number = int(regular_expression.group(1), 10)
        if chip_number == 255:
            break

        if chip_number >= io_relevant_config["min_chip_num"] and chip_number <= io_relevant_config["max_chip_num"]:
            operation_chip.append(params[index])
        else:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

    if chip_number == 255:
        operation_chip = []
        for index in range(1, io_relevant_config["chips_num"] + 1):
            operation_chip.append("cp"+str(index))

        '''    doing    '''
        result_dict = Xavier.call('io_chip_dir_get', board_id, *operation_chip)
        # output_str = _chips_bits_sort_str("chips",result_dict)

        for key,value in result_dict.items():
            if value is False:
                output_str = output_str + key + '=' + "????"
            else:
                output_str = output_str + key + '=' + str(hex(value))

            if count != io_relevant_config["max_chip_num"]:
                output_str = output_str + ','
                count = count + 1

    else:
        '''    doing    '''
        result_dict = Xavier.call('io_chip_dir_get', board_id, *operation_chip)
        # output_str = _chips_bits_sort_str("chips",result_dict)

        for key,value in result_dict.items():
            if value is False:
                output_str = output_str + key + '=' + "????"
            else:
                output_str = output_str + key + '=' + str(hex(value))

            if count != io_relevant_config["max_chip_num"]:
                output_str = output_str + ','
                count = count + 1

    return Utility.handle_done(output_str)


