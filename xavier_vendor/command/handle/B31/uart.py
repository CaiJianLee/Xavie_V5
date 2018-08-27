__author__ = 'haite'

import command.server.handle_utility as Utility
from ee.common import logger

from ee.common import xavier as Xavier1
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
    

global uart_device_list
uart_device_list=None

def get_uart_device_list():
    global uart_device_list
    if uart_device_list is None:
        uart_device_list = {}
        buses = Xavier.call("get_buses")
        for name, bus in buses.iteritems():
            if bus['bus'] == 'uart':
                uart_device_list[name] = bus
    return uart_device_list

@Utility.timeout(1)
def uart_config_handle(params):
    UART_CHANNEL_LIST = get_uart_device_list()
    uart_string = ''
    for uart_name in UART_CHANNEL_LIST.keys():
        uart_string += uart_name
        uart_string += ","
    help_info = "uart config(<channel>,<baud>,<bits>,<stop>,<parity>,{<timestamp>})$\r\n\
\tchannel=("+uart_string[:-1] +")$\r\n\
\tbaud=(115200,38400,19200,9600,4800,2400,1200,300)$\r\n\
\tbits=(5,6,7,8)$\r\n\
\tstop=(1,1.5,2)$\r\n\
\tparity=(odd,even,none)$\r\n\
\ttimestamp=(ON,OFF)$\r\n\
\t\tdefault:OFF"

    '''help'''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    timestamp = "OFF"

    '''params analysis '''
    param_count = len(params)
    if param_count < 5 or param_count > 6:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'] - param_count,"param count error")
    for index in range(0, param_count):
        if index == 0:
            channel = params[index]
        elif index == 1:
            baud = int(params[index])
        elif index == 2:
            bits = int(params[index])
        elif index == 3:
            stop = float(params[index])
        elif index == 4:
            parity = params[index].upper()
        elif index == 5:
            timestamp = params[index]
        else :
            return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'] - index,"param error")
    
    logger.info(str(channel) + " " + str(baud) + " " + str(bits) + " " + str(stop) + " " + str(parity) + " " + str(timestamp))
    
    if channel not in UART_CHANNEL_LIST:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"channel param error")
    
    if timestamp.upper() == "OFF":
        timestamp = "NONE"
    else:
        timestamp = "TS"
    logger.warning("cmd uart")
    result = Xavier.call("uart_param_config",channel, baud, bits, parity, stop, timestamp)
    if result == False:
         return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    
    return Utility.handle_done()

@Utility.timeout(1)
def uart_close_handle(params):
    UART_CHANNEL_LIST = get_uart_device_list()
    uart_string = ''
    for uart_name in UART_CHANNEL_LIST.keys():
        uart_string += uart_name
        uart_string += ","
    help_info = "uart close(<channel>})$\r\n\
\tchannel=("+uart_string[:-1] +")$"

    '''help'''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    '''params analysis '''
    param_count = len(params)
    if param_count != 1:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'] - param_count,"param count error")

    channel = params[0]
    
    if channel not in UART_CHANNEL_LIST:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"channel param error")
    
    result = Xavier.call("uart_close",channel)
    if result == False:
         return Utility.handle_error(Utility.handle_errorno['handle_errno_execute_failure'],"execute error")
    
    return Utility.handle_done()
