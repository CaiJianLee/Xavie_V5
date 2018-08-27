#-*- coding: UTF-8 -*- 
__author__ = 'xiaojingyong'
import re
import time
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger


board_name = 'fpgaio'

@Utility.timeout(1)
def gpio_set_handle(params):
    help_info = "gpio set({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX=Y,..bitX=Y),X=(1~272),Y=(0,1)\r\n "

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''

    params_count = len(params)
    bit_count = int(params[0],10)

    num_val_list = []

    if bit_count < 1 or bit_count > 32:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    if params_count != bit_count + 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    for index in range(1, bit_count+1):
        regular_expression = re.match( r'bit(\w+)=(\w+)', params[index])

        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        bit_number = int(regular_expression.group(1), 10)
        bit_state = int(regular_expression.group(2), 10) & 0x1

        num_val_list.append([bit_number, bit_state])

    '''doing'''
    result = Xavier.call('eval', board_name, 'set_io', num_val_list)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
   
    return Utility.handle_done()



def gpio_read_handle(params):
    help_info = "gpio read({<count>,<content>})$\r\n\
\tcount: (1-32) $\r\n\
\tcontent=(bitX,..bitX),X=(1~272)\r\n "

    ''' help '''    
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''

    read_io_list = []

    params_count = len(params)
    bit_count = int(params[0],10)


    if bit_count < 1 or bit_count > 32:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    if params_count != bit_count + 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    for index in range(1, bit_count+1):
        regular_expression = re.match( r'bit(\w+)', params[index])
        if regular_expression is None:
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")

        bit_number = int(regular_expression.group(1), 10)
        read_io_list.append([bit_number])

    '''doing'''
    result = Xavier.call('eval', board_name, 'get_io', read_io_list)
    if result is False:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error") 
    result_str = ""
    for num_val in result:
        result_str += "bit%d" %num_val[0] + "=%d," %num_val[1]
    result_str = result_str[:-1]
    return Utility.handle_done(result_str)