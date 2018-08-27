import struct
import os
import serial
from ee.common import logger
import ee.common.utility as utility

uart_flow_ctrl = {
    "SgUartHardStreamDisable":0,
    "SgUartHardStreamEnable" :1,
    "SgUartFlowCtrlEnable":2,
    }

uart_parity = {
    "NONE":serial.PARITY_NONE,
    "ODD":serial.PARITY_ODD,
    "EVEN":serial.PARITY_EVEN,
    }

uart_data_bits = {
    5:serial.FIVEBITS,
    6:serial.SIXBITS,
    7:serial.SEVENBITS,
    8:serial.EIGHTBITS,
}

uart_stop_bit = {
    1:serial.STOPBITS_ONE,
    1.5:serial.STOPBITS_ONE_POINT_FIVE,
    2:serial.STOPBITS_TWO,
}
class UartBus(object):
    def __init__(self,name):
        self.__ser = serial.Serial(timeout=0)
        self.__ser.port = name
        self.name = name
        self.__is_use = False

    def get_uart_status(self):
        if os.path.exists(self.name):
            return True
        else :
            return False
            
    @property
    def is_open(self):
        return self.__ser.isOpen()
        
    def _open(self):
        logger.info("uart open:"+str(self.name))
        try:
            self.__ser.open()
        except Exception as e:
            logger.error("uart open device name :%s error:%s"%(str(self.name),repr(e)))
            return False
        else:
            logger.info("open uart %s success fileno : %d:"%(str(self.name),self.__ser.fileno()))
        return True
    
    def _close(self):
        if self.is_open:
            logger.debug("uart close:"+str(self.name))
            self.__ser.close()
        return True

    def fileno(self):
        return self.__ser.fileno()

    def config(self,baud_rate= 115200,
                       data_bits = 8,
                       parity = 'NONE',
                       stop_bits = 1,
                       flow_ctrl = "SgUartHardStreamDisable"):
        logger.info("uart set baud_rate: %s ; flow_ctrl : %s ; data_bits: %s; stop_bits : %s ;parity: %s;"\
                     %(baud_rate, flow_ctrl, data_bits,stop_bits,parity))

        self.__ser.baudrate = baud_rate
        self.__ser.bytesize = uart_data_bits[data_bits]
        self.__ser.parity  = uart_parity[parity]
        self.__ser.stopbits = uart_stop_bit[stop_bits]
        if flow_ctrl == "SgUartHardStreamEnable":
            self.__ser.rtscts = True
        elif flow_ctrl == "SgUartFlowCtrlEnable":
            self.__ser.xonxoff = True
        self.__is_use = True

        if self.get_uart_status() is False:
            logger.warning("uart device:%s does not exist"%(str(self.name)))
            self._close()
            return False
        elif self.is_open is True:
            self._close()

        status = self._open()
        if status is False:
            logger.error("uart %s set param error"%(self.name))
            return False
        else :
            return True
    
    def read(self, length=512):
        return self.read_bytes(length)

    def write(self, data):
        return self.write_bytes(data)

    def read_bytes(self, length):
        """ read bytes string data from uart
            Args:
                length(int)   : the maximum number of read data bytes
            Returns:
                on success, return a string of bytes data
                on error, return False
        """
        if self.get_uart_status() is False:
            self._close()
            return False
        elif self.__is_use is False:
            return False
        elif self.is_open is False:
            self._open()
        
        try:
            data = self.__ser.read(length)
        except Exception as e:
            logger.error("read uart %s error:%s"%(self.name, repr(e)))
            return False

        logger.debug('read uart %s length:%d'%(self.name, len(data)))
        return data
    
    def write_bytes(self,data):
        """ write byte string data to uart
            Args:
                data(string)   : a string of bytes data
            Returns:
                on success, return True
                on error, return False
        """
        if self.get_uart_status() is False:
            self._close()
            return False
        elif self.__is_use is False:
            return False
        elif self.is_open is False:
            self._open()
        length = len(data)
        logger.debug("write uart %s length:%d"
            %(self.name, length))
        try:
            writen_len = self.__ser.write(data)
        except Exception as e:
            logger.error("write uart %s length:%d error:%s"%(self.name, length, repr(e)))
            return False
        
        if(writen_len != length):
            logger.warning("write uart device:%s length fail,except length:%s, reality length:%s"%(self.name, length, writen_len))
            return False
        
        return True

    def close(self):
        self.__is_use = False
        return self._close()