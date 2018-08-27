__author__ = 'haite'

from ee.profile import profile
from ee.profile.xobj import XObject
from ee.common import logger
from ee.eedispatcher import EEDispatcher
from ee.common import utility

def uart_param_config(name, baud_rate, data_bits, parity, stop_bits, timestamp):
    """ Set uart bus parameter
            
            Args:
                baud_rate(int)   : UART baud rate
                data_bits(int)   : Data width 5/6/7/8
                parity_type(str) : parity type. "ODD"/"EVNE"/"NONE"
                stop_bits(float) : stop bit width. 1/2
                time_insert(str) : PL UART Insert timestamp Control, "TS"/"NONE"
            Returns:
                bool: True | False, True for success, False for adc read failed
    """
    try:
        uart = XObject.get_object(name)
        isok = True
        if utility.mount_on_fpga(uart.name):
            uart.disable()
            uart.enable()
            uart.config(baud_rate, data_bits, parity, stop_bits, timestamp)
        else:
            isok = uart.config(baud_rate, data_bits, parity, stop_bits)
        
        return isok
    except Exception as e:
        logger.error("the %s uart param config execute error:%s"%(name, repr(e)))
        return False

def uart_close(uart_id):
    try:
        uart = XObject.get_object(uart_id)
        if utility.mount_on_fpga(uart.name):
            uart.disable()
        else:
            uart.close()

        return True
    except Exception as e:
        logger.error("close  the %s uart error:%s"%(uart_id,repr(e)))
        return False

EEDispatcher.register_method(uart_param_config)
EEDispatcher.register_method(uart_close)